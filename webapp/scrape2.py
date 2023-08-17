from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import codecs
import re
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

url = "https://chmsdemo.greenfossil.com/login"
driver.get(url)

wait = WebDriverWait(driver, 10)
wait.until(EC.url_to_be(url))

page_source = driver.page_source
soup = BeautifulSoup(page_source, features="html.parser")

check_inputs = input("Do you want to check for input fields? (y/n): ")

if check_inputs.lower() == 'y':
    inputs = soup.find_all('input')
    num_inputs = len(inputs)

    count = 1
    for i in inputs:
        print(str(i) + "\n")
        count += 1

    print("There are", num_inputs, "input fields on this page.\n")

inputField = input("Enter the input field element name: ")
inputElement = driver.find_element(By.ID,inputField)
print(inputElement)

inputkey = input("Enter what you want to type in this field: ")
inputElement.send_keys(inputkey)

inputField = input("Enter the second input field element name: ")
inputElement = driver.find_element(By.ID,inputField)
print(inputElement)

inputkey = input("Enter what you want to type in this field: ")
inputElement.send_keys(inputkey)

inputElement.send_keys(Keys.ENTER)

print(driver.current_url)
check_inputs = input("Do you want to switch to another url? (y/n): ")

if check_inputs.lower() == 'y':
    url = input("Enter a url: ")
else:
    url = driver.current_url

driver.get(url)

wait = WebDriverWait(driver, 10)
wait.until(EC.url_to_be(url))

page_source = driver.page_source
soup = BeautifulSoup(page_source, features="html.parser")
# find all input fields

dropdowns = soup.find_all(class_='dropdown')
count = 1
for i in dropdowns:
    print(str(i) + "\n")
    count += 1

inputField = input("Enter the input field element class: ")
inputElement = driver.find_element(By.CLASS_NAME,inputField)
print(inputElement)
inputElement.click()

dropdownvalue = input("Enter what option you want to enter into the dropdown list: ")
clickOption = driver.find_element(By.XPATH, "//div[@data-value='" + dropdownvalue + "']")
clickOption.click()

inputkey = input("Enter what you want to type in this field: ")
inputElement.send_keys(inputkey)

keyword = input("Enter a keyword: ")
matches = soup.body.find_all(string=re.compile(keyword))

len_match = len(matches)
title = soup.title.text
file = codecs.open('article_scraping.txt', 'a+')
file.write(title+"\n")
file.write("Instances of your keyword:\n")

count = 1
for i in matches:
    print(str(count) + "." + i + "\n")
    file.write(str(count) + "." + i + "\n")
    count += 1

print("There were " + str(len_match) + " matches found for the keyword.")
file.write("There were " + str(len_match) + " matches found for the keyword.")
file.close()

driver.quit()