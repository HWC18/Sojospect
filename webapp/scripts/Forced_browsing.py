import requests
from bs4 import BeautifulSoup
from time import sleep
import configparser
import sys
import configparser
import os
import mysql.connector

if __name__ == "__main__":
    user_input = sys.argv[1]

directory_forceable = []
config = configparser.ConfigParser()
config.read("config.ini")
username = config.get('Advanced Scan Settings','scraping_username')
password = config.get('Advanced Scan Settings','scraping_password')
force_browse = config.get('Advanced Scan Settings','scan_for_forced_browsing')
wordlist = config.get('Advanced Scan Settings','directory_wordlists')

def crawl_directory(base_url, new_list):
    directory_force = []
    for word in new_list:
        url = f"{base_url}{word}"
        response = requests.get(url)
        print(f'i am getting this url: ${url}')
        if response.status_code == 200:
            directory_force.append(url)

    return directory_force


def wordlist_function():
    if wordlist == "1k":
        myfile = open('scripts/1k_wordlist.txt','r')
    elif wordlist == "10k":
        myfile = open('scripts/10k_wordlist.txt','r')
    elif wordlist == "36k":
        myfile = open('scripts/36k_wordlist.txt','r') 
    newlist = []
    for line in myfile:
        line = '/'+ line
        newlist.append(line.replace("\n",""))
    return(newlist)

if int(force_browse) == 1:
    word_list = wordlist_function()
    base_url = user_input
    directory_force = crawl_directory(base_url,word_list)
    if directory_force is not None:
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
        vulnerability = "Forced browsing"
        description = "URLs that can be forced browsed to: " + str(directory_force)
        solution = "Implement urls that have been encoded."
        insert_query = "INSERT INTO low_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
        values = (vulnerability, description, solution)
        db_cursor.execute(insert_query, values)
        db_connection.commit()

        db_cursor.close()
        db_connection.close()
        print('there is an directory force error')
        print(f"this is the list of urls with pages that can be directory-forced: ${str(directory_force)}")
    else:
        print('there is no directory force error')
