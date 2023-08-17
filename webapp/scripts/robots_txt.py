import scrapy
from scrapy.crawler import CrawlerProcess
import sys
import configparser
import mysql.connector
import os

if __name__ == "__main__":
    user_input = sys.argv[1]

url = user_input

input_urls = []
test = 0

class TestSpider(scrapy.Spider):
    name = "robotstest"
    allowed_domains = [url]
    #allowed_domains = ["amazon.com"]
    start_urls = [url + "/robots.txt"]
    #start_urls = ["https://www.amazon.com/robots.txt"]


    def __init__(self, *args, **kwargs):
        super(TestSpider, self).__init__(*args, **kwargs)
        self.config_file_path = kwargs.get("config_file_path")

    def start_requests(self):
        user_input = sys.argv[1]
        url = user_input
        self.allowed_domains = [url]
        yield scrapy.Request(url + "/robots.txt", self.parse, errback=self.handle_error)

    def handle_error(self, failure):
        if failure.value.response.status == 404:
            self.insert_vulnerability()
        else:
            self.logger.error(f"Request failed: {failure}")

    def insert_vulnerability(self):
        config = configparser.ConfigParser()
        config.read(self.config_file_path)

        db_host = config.get('SQL Database', 'db_host')
        db_user = config.get('SQL Database', 'db_user')
        db_password = config.get('SQL Database', 'db_password')

        db_connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database="vulnerabilities"
        )

        db_cursor = db_connection.cursor()

        vulnerability = "No robots_txt"
        description = "robots.txt is a necessary standard used by websites to communicate with web crawlers and other automated agents (like search engine bots) about which parts of the site should not be crawled or scraped."
        solution = "Add the robots_txt in the website directory."

        insert_query = "INSERT INTO low_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
        values = (vulnerability, description, solution)

        db_cursor.execute(insert_query, values)
        db_connection.commit()

        db_cursor.close()
        db_connection.close()
        self.logger.info("Robots.txt does not exist")


if __name__ == "__main__":
    # Get the absolute path to the directory containing this script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Get the absolute path to the parent directory of the script's directory
    parent_directory = os.path.dirname(script_directory)
    
    # Construct the absolute path to the config.ini file
    config_file_path = os.path.join(parent_directory, "config.ini")
    
    # Create a CrawlerProcess instance
    process = CrawlerProcess()

    # Add your spider to the process
    process.crawl(TestSpider, config_file_path=config_file_path)

    # Start the crawling process
    process.start()