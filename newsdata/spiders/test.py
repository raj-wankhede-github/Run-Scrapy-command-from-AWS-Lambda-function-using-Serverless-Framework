import scrapy
import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from db.dynamodb_operations import DynamoDBOperations
import uuid


class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["nrn.com"]
    url = "https://www.nrn.com/news?infscr=1&page="
    page = 1
    start_urls = [url + str(page)]

    def parse(self, response):
        event_url = response.css(".title a::attr(href)")

        for link in event_url:
            yield response.follow(link.get(), callback=self.parse_links)

        # ONLY TWO PAGES
        for i in range(1, 4):
            next_page = self.url + str(self.page + i)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_links(self, response):
        # Select the specific <div> containing the <p> tags
        div_element = response.xpath('//div[@class="article-content "]')

        # Select all <p> tags within the <div>
        paragraphs = div_element.xpath(".//following-sibling::p")

        # Initialize a list to store the extracted content
        extracted_content = []

        # Iterate through the <p> tags
        for paragraph in paragraphs:
            # Extract text from all child elements of the <p> tag
            paragraph_text = paragraph.xpath(".//text()").extract()

            # Join the extracted text to form a single string
            paragraph_text = " ".join(paragraph_text).strip()

            # Append the extracted text to the result list
            extracted_content.append(paragraph_text)

        # Process or yield the extracted content as needed
        if extracted_content:
            yield {"content": extracted_content}
