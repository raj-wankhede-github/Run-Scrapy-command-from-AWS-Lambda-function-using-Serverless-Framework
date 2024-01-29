import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from db.mysql_operations import DBOperations
from lxml import html
import datetime
from loguru import logger
from scrapy.http import HtmlResponse
import requests
from scrapy.exceptions import CloseSpider
import dateparser


class FooddiveSpider(scrapy.Spider):
    name = "fooddive"
    allowed_domains = ["fooddive.com"]
    url = "https://www.fooddive.com/?page="
    page = 1
    start_urls = [url + str(page)]
    domain_name = "https://www.fooddive.com"

    dbConn = DBOperations()
    dbConn.connect()
    dbConn.getDBVersion()

    last_worked_date = dbConn.fetch_last_data(domain_name)
    if last_worked_date != None:
        last_worked_date = last_worked_date[0]

    def parse(self, response):
        while True:
            status = []
            event_url = response.css(".feed__title a::attr(href)")
            lst = [i.get() for i in event_url]
            logger.debug(lst)
            headers = {
                "Content-Type": "text/html; charset=UTF-8",
            }

            for link in event_url:
                if link.get()[:4] != "http":
                    _url = self.domain_name + link.get()
                    res = requests.get(_url)
                    html_content = res.text
                    _response = HtmlResponse(
                        url=_url, body=html_content.encode("utf-8"), headers=headers
                    )
                    status.append(self.parse_links(_response))

            if False in status:
                raise CloseSpider(
                    "Stopping the spider because, All Latest News are Covered."
                )
            else:
                self.page += 1
                next_page = self.url + str(self.page)

                res = requests.get(next_page)
                html_content = res.text
                _response = HtmlResponse(
                    url=next_page, body=html_content.encode("utf-8"), headers=headers
                )
                self.parse(_response)

        # event_url = response.css(".feed__title a::attr(href)")

        # for link in event_url:
        #     yield response.follow(link.get(), callback=self.parse_links)

        # # Scrape n numbers of pages
        # for i in range(1, 2):
        #     next_page = self.url + str(self.page + i)
        #     yield scrapy.Request(next_page, callback=self.parse)

    def parse_links(self, response):
        sel = Selector(response)
        tree = html.fromstring(response.text)

        # Extract all the data
        date = response.css(".published-info::text").get()
        if date is None:
            return "Date Not Present"
        else:
            date = date.split("Published ")[1].replace("\n", "").strip()

        try:
            formated_date = dateparser.parse(date)
        except Exception as exc:
            return "Date Not Present"

        logger.info(self.last_worked_date)
        logger.info(formated_date)

        if self.last_worked_date is not None and formated_date == self.last_worked_date:
            logger.info(
                "Scraping finished. Already have the latest entries in the database."
            )
            return False

        title = sel.xpath("//h1[@class='display-heading-04']/text()").get()
        summary = response.css(".first-page-pdf p::text").get()
        author = response.css(".author-name a::text").get()
        date = response.css(".published-info::text").get()
        img_url = response.css(".article-hero-img img::attr(src)").get()

        # -------- Author --------
        author = ""
        author_xpath = ["//div[@class='author-name']/a", "//div[@class='author ']"]
        for a_xpath in author_xpath:
            tags_author = tree.xpath(a_xpath)

            if len(tags_author) > 0:
                author = tags_author[0].text_content()
                break

        article_content_xpath = [
            "//div[@class=' large medium article-body']",
            "//div[@class=' large medium article-body ']",
        ]
        article_content = ""
        for xpath in article_content_xpath:
            tags_article_content = tree.xpath(xpath)

            if len(tags_article_content) > 0:
                p_elements = tags_article_content[0].xpath(".//p")
                for p_element in p_elements:
                    article_content += p_element.text_content().strip() + "\n"
                break

        if title != None:
            if summary == None:
                summary = ""
            if author == None:
                author = ""
            if date == None:
                date = ""
            else:
                date = date.split("Published ")[1].replace("\n", "").strip()
            if article_content == None:
                article_content = ""
            if img_url == None:
                img_url = ""
            else:
                img_url = FooddiveSpider.allowed_domains[0] + img_url

            scrape_data = {
                "id": self.dbConn.getMaxSeq() + 1,
                "title": title.strip(),
                "summary": " ".join(summary.replace("\n", "").split()).strip(),
                "author": " ".join(author.replace("\n", "").split()).strip(),
                "date": formated_date,
                "article_content": " ".join(article_content.split()).strip(),
                "image_url": img_url,
                "domain_name": self.domain_name,
            }

            self.dbConn.insert(scrape_data)
            self.dbConn.commit()
            return True
