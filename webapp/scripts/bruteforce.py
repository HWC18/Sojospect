import requests
from bs4 import BeautifulSoup
from urlextract import URLExtract
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support.ui import Select
import configparser
import mysql.connector
import sys

if __name__ == "__main__":
    user_input = sys.argv[1]

# Load the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

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

config = configparser.ConfigParser()
config.read("config.ini")
passwordtotest = config.get('Advanced Scan Settings','bruteforce_amount')
url = user_input
#enter username password

# Detect available web browsers and create a webdriver
def create_webdriver():
    try:
        # Try creating a Chrome webdriver
        chrome_options = Options()
        chrome_options.add_argument("headless")
        return webdriver.Chrome(options=chrome_options)
    except:
        try:
            # Try creating a Firefox webdriver
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.add_argument("headless") 
            return webdriver.Firefox(options=firefox_options)
        except:
            try:
                from selenium.webdriver.edge.options import Options as EdgeOptions
                # Try creating an Edge webdriver
                options = EdgeOptions()
                options.use_chromium = True
                options.add_argument("headless")
                return webdriver.Edge(options=options)
            except:
                raise Exception("No suitable browser found")

edgeBrowser = create_webdriver()

def trypass(password,idlist,username,edgeBrowser):

    sampleElement = WebDriverWait(edgeBrowser, 10).until(
    EC.presence_of_element_located((By.ID, idlist[0])))

    sampleElement.send_keys(username)

    sampleElement2 = WebDriverWait(edgeBrowser, 10).until(
        EC.presence_of_element_located((By.ID, idlist[1])))
    
    sampleElement2.send_keys(password)

    sampleElement.send_keys(Keys.ENTER)

conn = requests.get(url)
#password list
text_file = open("passwordlist.txt", "r")
newlist = text_file.read().split('\n')
text_file.close()
num=int(passwordtotest)
passlist=newlist[:num]
print(passlist)
#get input fields
soup = BeautifulSoup(conn.content,features="lxml")
inputs = soup.find_all('input')
inputfeild=[]
# Get the ids of the input fields
for tag in inputs:
    input = tag.get('id',None)
    if input is not None:
        inputfeild.append(input)
print(inputfeild)

# This is the step for maximizing browser window
edgeBrowser.maximize_window()
# Browser will get navigated to the given URL
edgeBrowser.get(user_input)
initial_login_url = edgeBrowser.current_url

#For all password in list
for i in passlist:

    trypass(i,inputfeild,'U0000026',edgeBrowser)
    url=edgeBrowser.current_url
    
    #if still in login page
    if str(url) == initial_login_url :
        print('---------------------')
        #find error message
        page_source = edgeBrowser.page_source
        sampleElement2 = WebDriverWait(edgeBrowser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@class="ui error message"]')))
        a=str(sampleElement2.text)
        print(a)
      
        #output base on error
        if len(a)==70:
            print('test pass there is password limit')
            trypass(i,inputfeild,'U0000027',edgeBrowser)
            print('---------------------')
            #find error message
            page_source = edgeBrowser.page_source
            sampleElement2 = WebDriverWait(edgeBrowser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="ui error message"]')))
            a=str(sampleElement2.text)
            print(a)
            print(len(a))
            if len(a)==70:
                print('account locked')
            else:
                print('account allows has timer for unlock')
            break
        elif len(a)==28:
            print('user does not exist')
            break
        else:
            print('unknown error')
            break
    else:
        db_cursor = db_connection.cursor()
        # Insert a row into the MySQL table
        vulnerability = "Brute Force"
        description = "Account successfully cracked using brute force attack"
        solution = "Implement stronger password policies and account lockout mechanisms"
        insert_query = "INSERT INTO critical_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
        values = (vulnerability, description, solution)
        db_cursor.execute(insert_query, values)
        db_connection.commit()

        db_cursor.close()
        db_connection.close()
        break

