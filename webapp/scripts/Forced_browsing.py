import scrapy
from pathlib import Path
from scrapy.http import FormRequest
import configparser
import os
import mysql.connector
from scrapy.crawler import CrawlerProcess
import sys

if __name__ == "__main__":
    user_input = sys.argv[1]

test = 0

class TestSpider(scrapy.Spider):
    name = "directorytest1"
    allowed_domains = [user_input]
    handle_httpstatus_list = [403, 404]

    def parse(self, response):
        config_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))

        config = configparser.ConfigParser()
        config.read(config_file_path)
        
        username = config.get('Advanced Scan Settings', 'scraping_username')
        password = config.get('Advanced Scan Settings', 'scraping_password')
        force_browse = config.get('Advanced Scan Settings', 'scan_for_forced_browsing')
        if int(force_browse) == 1:
            print('Hello, I am called')
            return FormRequest.from_response(response, formdata={
                'loginId': username,
                'password': password
            }, callback=self.continue_scraping)
        else:
            print('Hello, I am not called')
            return
        
    def continue_scraping(self, response):
        file_to_open = open("directory_force.txt", 'w')
        file_to_open.close()
        config = configparser.ConfigParser()
        config.read(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini')))
        wordlist = config.get('Advanced Scan Settings', 'directory_wordlists')
        print(f'{wordlist}_wordlist.txt')
        wordlist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', f'{wordlist}_wordlist.txt'))
        with open(wordlist_path, 'r') as myfile:
            newlist = [line.strip() for line in myfile]
        directory_force = []
        for line in newlist:
            url = yield response.follow(f'/{line}', callback=self.scrap_new_page)
            if url:  # Make sure the URL is not None
                directory_force.append(url)

        if directory_force:
            config = configparser.ConfigParser()
            config.read(config_file_path)
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
            vulnerability = "Injection"
            description = "URLs that can be forced browsed to: " + directory_force
            solution = "Implement urls that have been encoded."
            insert_query = "INSERT INTO low_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
            values = (vulnerability, description, solution)
            db_cursor.execute(insert_query, values)
            db_connection.commit()

            db_cursor.close()
            db_connection.close()

    def scrap_new_page(self, response):
        if response.status == 200:
            string1 = str(response).replace("<200 " + user_input, "")
            string2 = string1.replace(">", "")
            url = string2.strip()  # Remove leading/trailing whitespace

        return url


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