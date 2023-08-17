import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
import configparser
import mysql.connector
import sys

def create_webdriver():
    try:
        # Try creating a Chrome webdriver
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        return webdriver.Chrome(options=chrome_options)
    except:
        try:
            # Try creating a Firefox webdriver
            firefox_options = webdriver.FirefoxOptions()
            firefox_options.add_argument("--start-maximized")
            return webdriver.Firefox(options=firefox_options)
        except:
            try:
                # Try creating an Edge webdriver
                return webdriver.Edge(r"msedgedriver.exe")
            except:
                raise Exception("No suitable browser found")

edgeBrowser = create_webdriver()

if __name__ == "__main__":
    user_input = sys.argv[1]

driver = edgeBrowser
url = user_input
driver.get(url)
loginid = ['abcd','u0000028']
password = ['abcd','1234']
error_messages = []

def testing(username, password, inputfields,driver):
    sampleElement = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, inputfields[0])))

    sampleElement.send_keys(username)

    sampleElement2 = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, inputfields[1])))
    
    sampleElement2.send_keys(password,Keys.RETURN)


conn = requests.get(url)
#get input fields
soup = BeautifulSoup(conn.content,features="lxml")
inputs = soup.find_all('input')
inputfield=[]
# Get the ids of the input fields
for tag in inputs:
    input = tag.get('id',None)
    if input is not None:
        inputfield.append(input)

for i in range(len(loginid)):
    testing(loginid[i],password[i],inputfield,driver)
    sampleElement2 = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, '//*[@class="ui error message"]')))
    error_messages.append(str(sampleElement2))

if error_messages[0] == error_messages[1]:
    print('there is no vulnerabilitiy')
else:
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
    vulnerability = "Overinformative error"
    description = "Error messages are present that might provide data for attackers to use: " + error_messages[1]
    solution = "Use less informative error messages."
    insert_query = "INSERT INTO low_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
    values = (vulnerability, description, solution)
    db_cursor.execute(insert_query, values)
    db_connection.commit()

    db_cursor.close()
    db_connection.close()
    print("This is a vulnerability. There is too much info")

input_text_loginid = driver.find_element(By.ID,'loginId')
input_text_password = driver.find_element(By.ID,'password')
input_text_loginid.send_keys('u0000028')
input_text_password.send_keys('password',Keys.RETURN)
