import seleniumBot
import configparser
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import mysql.connector

# Load the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

db_host = config.get('SQL Database', 'db_host')
db_user = config.get('SQL Database', 'db_user')
db_password = config.get('SQL Database', 'db_password')

db_connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database="vulnerabilities"
)

def checkCookie(username, password):
    cookie = seleniumBot.getCookie(username, password)
    print(cookie)
    if cookie['secure'] != True or cookie['httpOnly'] != True:
        result = "'secure' value on cookie is not set to True or 'httpOnly' value is not set to True"
        
        db_cursor = db_connection.cursor()
        # Insert a row into the MySQL table
        vulnerability = "Cookie attribute is not secure."
        description = "'secure' value on cookie is not set to True or 'httpOnly' value is not set to True."
        solution = "Set cookie values to be secure and/or httpOnly."
        insert_query = "INSERT INTO low_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
        values = (vulnerability, description, solution)
        db_cursor.execute(insert_query, values)
        db_connection.commit()

        db_cursor.close()
        db_connection.close()
        
        print(result)
    else:
        result = "No vulnerabilities found"
        print(result)

checkCookie(config['Advanced Scan Settings']['scraping_username'], config['Advanced Scan Settings']['scraping_password'])