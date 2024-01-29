import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from db.dynamodb_operations import DynamoDBOperations
from db.mysql_operations import DBOperations
import uuid
from lxml import html
import datetime
from loguru import logger
import pytz
from scrapy.http import HtmlResponse
import requests
from scrapy.exceptions import CloseSpider


class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["nrn.com"]
    url = "https://www.nrn.com/news?infscr=1&page="
    page = 1
    start_urls = [url + str(page)]
    domain_name = 'https://www.nrn.com'

    dbConn = DBOperations()
    dbConn.connect()
    dbConn.getDBVersion()

    last_worked_date = dbConn.fetch_last_data(domain_name)
    if last_worked_date != None:
        last_worked_date = last_worked_date[0]

    def parse(self, response):
        while True:
            status = []
            event_url = response.css(".title a::attr(href)")    

            headers = {
                "Content-Type": "text/html; charset=UTF-8",  
            } 

            for link in event_url:
                _url = self.domain_name + link.get()
                res = requests.get(_url)
                html_content = res.text 
                _response = HtmlResponse(url=_url, body=html_content.encode('utf-8'), headers=headers)
                status.append(self.parse_links(_response))

            if False in status: 
                raise CloseSpider("Stopping the spider because, All Latest News are Covered.")
            else:
                self.page += 1
                next_page = self.url + str(self.page)
                res = requests.get(next_page)
                html_content = res.text 
                _response = HtmlResponse(url=next_page, body=html_content.encode('utf-8'), headers=headers)
                self.parse(_response)
        
        # event_url = response.css(".title a::attr(href)")

        # for link in event_url:
        #     yield response.follow(link.get(), callback=self.parse_links)

        # # ONLY TWO PAGES
        # for i in range(1, 2):
        #     next_page = self.url + str(self.page + i)
        #     yield scrapy.Request(next_page, callback=self.parse)
        
        # return


    def parse_links(self, response):

        sel = Selector(response)
        tree = html.fromstring(response.text)

        # Extract all the data
        date = response.css(".author-and-date span::text").get()
        if date is None:
            return "Date Not Present"
        formated_date = datetime.datetime.strptime(date, '%b %d, %Y')

        logger.info(self.last_worked_date)
        logger.info(formated_date)

        if self.last_worked_date is not None and formated_date == self.last_worked_date:
            logger.info("Scraping finished. Already have the latest entries in the database.")
            return False

        title = sel.xpath("//h1/text()").get()
        summary = sel.xpath(
            "//div[@class='field field-name-field-penton-content-summary field-type-text-long field-label-hidden']/text()"
        ).get()
        author = response.css(".author-and-date span a::text").get()
        img_url = response.css(".big-article__image img::attr(src)").get()

        article_content_xpath = [
            "//div[@class='article-content ']",
            "//div[@class='article-content']",
            "//div[@class='gallery-article-p']",
        ]
        article_content = ""
        for xpath in article_content_xpath:
            tags_article_content = tree.xpath(xpath)

            if len(tags_article_content) > 0:
                p_elements = tags_article_content[0].xpath(".//p")
                for p_element in p_elements:
                    article_content += p_element.text_content().strip() + "\n"

                break

        img_url_xpath = [
            "//div[@class='big-article__image']/img/@src",
            "//div[@class='gallery-image-container__big']/img/@src"
        ]
        img_url = ""
        for xpath in img_url_xpath:
            tags_imgURL = tree.xpath(xpath)
            if len(tags_imgURL) > 0:
                img_url = tags_imgURL[0]
                break

        if title != None:
            if summary == None:
                summary = ""
            if author == None:
                author = ""
            if date == None:
                date = ""
            if article_content == None:
                article_content = ""
            if img_url == None:
                img_url = ""

            scrape_data = {
                "id": self.dbConn.getMaxSeq()+1,
                "title": title.strip(),
                "summary": ' '.join(summary.replace("\n", "").split()).strip(),
                "author": ' '.join(author.replace("\n", "").split()).strip(),
                "date": formated_date,
                "article_content":  " ".join(article_content.split()).strip(),
                "image_url": img_url,
                "domain_name": self.domain_name,
            }

            self.dbConn.insert(scrape_data)
            self.dbConn.commit()

            return True
