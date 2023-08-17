import scrapy


class TestspiderSpider(scrapy.Spider):
    name = "TestSpider"
    allowed_domains = ["chmsdemo.greenfossil.com"]
    start_urls = ["http://chmsdemo.greenfossil.com/"]

    def parse(self, response):
        pass
