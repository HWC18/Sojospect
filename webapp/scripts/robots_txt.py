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

    def parse(self, response):
       if(response.status == 200):
            
            config = configparser.ConfigParser()
            config.read("config.ini")

            # Get values from the config file
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
            # Insert a row into the MySQL table
            vulnerability = "Present robots_txt"
            description = "robots_txt file might provide information that attackers could use."
            solution = "Delete the robots_txt present in the website directory."
            insert_query = "INSERT INTO low_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
            values = (vulnerability, description, solution)
            db_cursor.execute(insert_query, values)
            db_connection.commit()

            db_cursor.close()
            db_connection.close()
            print("Robots.txt does exist")
       else:
           print("Robots.txt does not exist")


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