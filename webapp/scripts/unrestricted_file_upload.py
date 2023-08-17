import os
import time
import configparser
from seleniumBot import driver
from seleniumBot import userLogin
from seleniumBot import analyseConfig
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
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


config = configparser.ConfigParser()
config.read('config.ini')
username = config['Advanced Scan Settings']['scraping_username']
password = config['Advanced Scan Settings']['scraping_password']
target_url = 'https://chmsdemo.greenfossil.com/'
fileList = []
for filename in os.listdir('testFiles'):
    fileList.append(os.path.join('testFiles', filename))

homePage = userLogin(target_url, username, password)
role = driver.find_element(By.CSS_SELECTOR, 'span.label').text


if role == 'Administrator':
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.dropdown')))
    homePage = driver.find_element(By.CSS_SELECTOR, 'div.dropdown div a').get_attribute('href')
    driver.get(homePage+'/editPhoto')


elif role != 'Administrator':
    driver.get(homePage+'/editPhoto')


fileUpload = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'imageUpload')))
unrestricted_count = 0
for i in range(len(fileList)):
    time.sleep(10)
    print(fileList[i])
    fileUpload.send_keys(os.path.realpath(fileList[i]))
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.message')))
        message = driver.find_element(By.CSS_SELECTOR, 'div.message').text
    except TimeoutException:
        unrestricted_count += 1
if unrestricted_count > 0:
    db_cursor = db_connection.cursor()
    # Insert a row into the MySQL table
    vulnerability = "Unrestricted file upload"
    description = "Files that may not be allowed to upload can be uploaded."
    solution = "Add validation for file uploading."
    insert_query = "INSERT INTO medium_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
    values = (vulnerability, description, solution)
    db_cursor.execute(insert_query, values)
    db_connection.commit()

    db_cursor.close()
    db_connection.close()

    message = 'Unrestricted file upload vulnerability detected'
else:
    message = 'Unrestricted file upload vulnerability not detected'

print('finished testing')
driver.quit()
print(message)