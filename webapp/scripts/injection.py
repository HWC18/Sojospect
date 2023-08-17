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
from selenium.webdriver.edge.options import Options
import re
import configparser
import mysql.connector
import sys




config = configparser.ConfigParser()
config.read("config.ini")

if __name__ == "__main__":
    user_input = sys.argv[1]


config = configparser.ConfigParser()
config.read("config.ini")

username = config.get('Advanced Scan Settings','scraping_username')
password = config.get('Advanced Scan Settings','scraping_password')
ifsql=config.get('Advanced Scan Settings','injection_sql_payload')
ifxss=config.get('Advanced Scan Settings','injection_xss_payload')
payloadfile='sqlpayload.txt'
if  ifsql=='1' and ifxss=='1':
    payloadfile='xsssqlpayloads.txt'
elif ifsql=='1':
    payloadfile='sqlpayload.txt'
elif ifxss=='1':
    payloadfile='xsspayload.txt'
def trypass(password,idlist,username,edgeBrowser):

    sampleElement = WebDriverWait(edgeBrowser, 10).until(
    EC.presence_of_element_located((By.ID, idlist[0])))

    sampleElement.send_keys(username)

    sampleElement2 = WebDriverWait(edgeBrowser, 10).until(
        EC.presence_of_element_located((By.ID, idlist[1])))
    
    sampleElement2.send_keys(password)

    sampleElement.send_keys(Keys.ENTER)
def injection(edgeBrowser,payload,url,username,password,loginfield,loginurl):
        vulns = ""
        
        page_source = edgeBrowser.page_source
        soup = BeautifulSoup(page_source, features="html.parser")

        #for item in soup.select("[type^='hidden']"):
            #item.decompose()

        greenbt=[soup.find(class_="green")]
        if greenbt!=[None]:
            sampleElement2 = WebDriverWait(edgeBrowser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "green")))
            time=edgeBrowser.find_element(By.CLASS_NAME, "green")
            if time.is_displayed():
                    time.click()
        
        inputs = soup.find_all('input')
        if inputs ==[]:
            print('url have no inputfield')
            return 1
        inputfield=[]
        checks=[]
        dates=[]
        numonly=['Phone','Postal Code','Email','phone','email','Capacity',"Fee","Local Contact"]
        for tag in inputs:
            input = tag.get('name',None)
            readonly=tag.get('readonly',None)
            place=tag.get('placeholder',None)
            labels=tag.parent('label')
            checkbox=tag.get('type',None)
            check='o'
            isanum=0
            if input is not None:
                for i in labels:
                    for num in numonly:
                        check=re.compile(f'{num}').search(str(i))
                        
                        
                        if check:
                            
                            if num=='Email':
                                dates.append([input,"greenfossil@gmail.com"])
                            else:
                                dates.append([input,"122"])
                                
                            isanum=1
                            break
                        else:
                            isanum=0
                if isanum==0:
                    if readonly=='readonly':
                        pass
                    elif checkbox=='hidden':
                        pass
                    elif checkbox=="checkbox" or check=="radio":
                        
                        checks.append(input)
                    elif check=="file":
                        pass
                    elif place=='dd/mm/yyyy':
                        dates.append([input,"2/2/2020"])
                    elif place=='h:mm a':
                        dates.append([input,"7:00 am"])
                    elif place=='hh:mm':
                        dates.append([input,"01:00"])
                    elif place=='dd/mm/yyyy h:mm a':
                        dates.append([input,"01/07/2023 12:00 am"])
                    else:
                        inputfield.append(input)
        if inputfield ==[]:
            print('url have no inputfield to test')
            return 1

        soup2 = BeautifulSoup(page_source, features="html.parser")
        
        
        inputs2 = soup2.find_all(class_="selection")
        inputfield2=[]
        for tag in inputs2:
            hidden = tag.get('type',None)
            if hidden=='hidden':
                pass
            else:
                input2 = tag.get('class',None)
                if input2 is not None:
                    inputfield2.append(input2)
        #For pages with no selection fields
        inputs3= soup2.find_all(class_="toggle")
        if inputs3!=[]:
            sampleElement2 = WebDriverWait(edgeBrowser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "toggle")))
            toggle=edgeBrowser.find_elements(By.CLASS_NAME, "toggle")
            
            #To click to make the choices visable 
            for field in toggle:
                if field.is_displayed():
                    #click to open selection field
                    field.click()
                    break
        Next=soup2.find_all('button')
        Nextbt=[]
        for value in Next:
            n=value.text
            if n=="Next":
                na=value.get('name',None)
                Nextbt.append(na)
        
        
        if inputfield !=[] and inputfield2==[]:
            if dates!=[]:
                 for i in dates:
                    sampleElement = WebDriverWait(edgeBrowser, 10).until(
                    EC.presence_of_element_located((By.NAME, i[0])))
                    if sampleElement.is_displayed():
                        sampleElement.clear()
                        sampleElement.send_keys(i[1])
            for i in inputfield:
                sampleElement = WebDriverWait(edgeBrowser, 10).until(
                EC.presence_of_element_located((By.NAME, i)))
                if sampleElement.is_displayed():
                    if sampleElement.is_enabled():
                        if i!="partialNricOpt":
                            sampleElement.clear()
                        sampleElement.send_keys(f"{payload}")
            if sampleElement.is_enabled():
                sampleElement.send_keys(Keys.ENTER)
            else:
                print('url have no enabled inputfield')
                return 1
            if Nextbt!=[]:
                injection(edgeBrowser,payload,url,username,password,loginfield,loginurl)
                return

            url2 = edgeBrowser.current_url
            print(url2)
            if url2==f"{loginurl}":
                trypass(password,loginfield,username,edgeBrowser)
                sleep(0.1)
                print('fail')
                data=[url,payload,'fail']
                print(data)
            else:
                afterurl=edgeBrowser.current_url
                if afterurl == url:
                    page_source2 = edgeBrowser.page_source
                    soup3 = BeautifulSoup(page_source2, features="html.parser")
                    sure=soup3.find_all('button',string=re.compile(f'Search'))
                    print(sure)
                    if sure ==[]:
                        print('fail')
                        data=[url,payload,'fail']
                        print(data)
                    else:
                        message=[soup3.find('div',class_='ui info message')]
                        if message!=[None]:
                            print(len(message[0].text))
                            print(message[0].text)
                            if len(message[0].text)==129:
                                print('pass')
                                data=[url,payload,'vulnerability']
                                vulns += str(data) + "\n"

                                print(data)
                            elif len(message[0].text)==66:
                                print('fail')
                                data=[url,payload,'fail']
                                print(data)
                            else:
                                print('pass')
                                data=[url,payload,'vulnerability']
                                vulns += str(data) + "\n"
                                
                                print(data)
                        else:
                            addchild=soup3.find_all('h1',string=re.compile(f'Add Child Newcomer'))      
                            if addchild !=[]:  
                                addchildsearch=soup3.find_all(string=re.compile(f'No potential duplicates found'))
                                if addchildsearch==[]:
                                    print('pass')
                                    data=[url,payload,'vulnerability']
                                    vulns += str(data) + "\n"

                                    print(data)
                                else:
                                    print('fail')
                                    data=[url,payload,'fail']
                                    print(data)
                                proceed=soup3.find_all('button')
                                for value in proceed:
                                    n=value.text
                                    if n=="Yes, proceed to add":
                                        na=value.get('name',None)
                                        proceedbt = WebDriverWait(edgeBrowser, 10).until(
                                            EC.presence_of_element_located((By.NAME, na)))
                                        proceedbt.click()
                                url=edgeBrowser.current_url
                                injection(edgeBrowser,payload,url,username,password,loginfield,loginurl)
                            else:
                                cellgroup=soup3.find_all('h1',string=re.compile(f'Cell Group Search'))
                                if cellgroup !=[]:  
                                    cellgroupsearch=soup3.find_all(string=re.compile(f'There are no Cell Group/s found'))
                                    if cellgroupsearch==[]:
                                        print('pass')
                                        data=[url,payload,'vulnerability']
                                        vulns += str(data) + "\n"

                                        print(data)
                                    else:
                                        print('fail')
                                        data=[url,payload,'fail']
                                        print(data)
                                else:
                                    print('fail')
                                    data=[url,payload,'fail']
                                    print(data)                                                           
                else:
                    page_source = edgeBrowser.page_source
                    soup3 = BeautifulSoup(page_source, features="html.parser")
                    sure=soup3.find_all(string=re.compile(f'{payload}'))
                    sure2=soup3.find_all(f'{payload}')
                    print(sure)
                    print(sure2)
                    if sure2 ==[]:
                        print('fail')
                        data=[url,payload,'fail']
                        print(data)
                    else:
                        print('pass')
                        data=[url,payload,'vulnerability']
                        vulns += str(data) + "\n"

                        print(data)
                    
        #For pages with selection fields
        payload1=payload
        if inputfield !=[] and inputfield2!=[]:
            
            #To find selection fields to click to make the choices visable and interable 
            sampleElement2 = WebDriverWait(edgeBrowser, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "selection")))
            Selection=edgeBrowser.find_elements(By.CLASS_NAME, "selection")
            
            #To click to make the choices visable 
            print(payload)
            for field in Selection:
                if field.is_displayed():
                    #click to open selection field
                    field.click()
                
                    #find the first option
                    clcik=field.find_element(By.CLASS_NAME,"item")
                    #Select the first option
                    if clcik.is_displayed():
                        sleep(0.1)
                        clcik.click()
            if dates!=[]:
                 for i in dates:
                    sampleElement = WebDriverWait(edgeBrowser, 10).until(
                    EC.presence_of_element_located((By.NAME, i[0])))
                    if sampleElement.is_displayed():
                        sampleElement.clear()
                        sampleElement.send_keys(i[1])
            #Fill in all writeable inputfield with xss payload
            payload1=payload
            goodinput=''
            for i in inputfield:
                if i!="preferred":
                    if i =="partialNricOpt":
                        payload="123A"
                    else:
                        payload=payload1
                    if i !='loginIdOpt':
                        sampleElement = WebDriverWait(edgeBrowser, 10).until(
                        EC.presence_of_element_located((By.NAME, i)))
                        
                        if sampleElement.is_displayed():

                            if sampleElement.is_enabled():
                                if i!="partialNricOpt":
                                    sampleElement.clear()
                            
                                sampleElement.send_keys(f"{payload}")
                            goodinput=i
            #Submit the form to test payload
            
            sampleElement = WebDriverWait(edgeBrowser, 10).until(
                        EC.presence_of_element_located((By.NAME, goodinput)))
            if sampleElement.is_enabled():
                sampleElement.send_keys(Keys.ENTER)
            else:
                print('url have no enabled inputfield')
                return 1
            if Nextbt!=[]:
                injection(edgeBrowser,payload,url,username,password,loginfield,loginurl)
                return
            
            afterurl=edgeBrowser.current_url
            if afterurl == url:
                page_source2 = edgeBrowser.page_source
                soup3 = BeautifulSoup(page_source2, features="html.parser")
                sure=soup3.find_all('button',string=re.compile(f'Search'))
                print(sure)
                if sure ==[]:
                    print('fail')
                    data=[url,payload,'fail']
                    print(data)
                else:
                    message=[soup3.find('div',class_='message')]
                    if message!=[None]:
                        print(len(message[0].text))
                        print(message[0].text)
                        if len(message[0].text)==129:
                            print('pass')
                            data=[url,payload,'vulnerability']
                            vulns += str(data) + "\n"

                            print(data)
                        elif len(message[0].text)==66:
                                print('fail')
                                data=[url,payload,'fail']
                                print(data)
                        else:
                            print('fail')
                            data=[url,payload,'fail']
                            print(data)
                    else:
                            addchild=soup3.find_all('h1',string=re.compile(f'Add Child Newcomer'))      
                            if addchild !=[]:
                                addchildsearch=soup3.find_all(string=re.compile(f'potential duplicates found'))
                                if addchildsearch==[]:                     
                                    print('pass')
                                    data=[url,payload,'vulnerability']
                                    vulns += str(data) + "\n"

                                    print(data)
                                else:
                                    print('fail')
                                    data=[url,payload,'fail']
                                    print(data)
                                #proceed=soup3.find_all('button')
                                
                                #for value in proceed:
                                    #n=value.text
                                    #if n=="Yes, proceed to add":
                                        #na=value.get('name',None)
                                        #proceedbt = WebDriverWait(edgeBrowser, 10).until(
                                            #EC.presence_of_element_located((By.NAME, na)))
                                        #proceed.click()
                                        
                                #url=edgeBrowser.current_url
                                #injection(edgeBrowser,payload,url,username,password,loginfield)
                            else:
                                cellgroup=soup3.find_all('h1',string=re.compile(f'Cell Group Search'))
                                if cellgroup !=[]:  
                                    cellgroupsearch=soup3.find_all(string=re.compile(f'There are no Cell Group/s found'))
                                    if cellgroupsearch==[]:
                                        print('pass')
                                        data=[url,payload,'vulnerability']
                                        vulns += str(data) + "\n"

                                        print(data)
                                    else:
                                        print('fail')
                                        data=[url,payload,'fail']
                                        print(data)
                                else:
                                    print('fail')
                                    data=[url,payload,'fail']
                                    print(data)
                        
            else:
                page_source = edgeBrowser.page_source
                soup3 = BeautifulSoup(page_source, features="html.parser")
                print(payload1)
                sure=soup3.find_all(string=re.compile(f'{payload1}'))
                sure2=soup3.find_all(f'{payload1}')
                print(sure)
                print(sure2)
                if sure2 ==[]:
                    print('fail')
                else:
                    data=[url,payload,'vulnerability']
                    print(data)

        return vulns
    
url = user_input

conn = requests.get(url)


soup = BeautifulSoup(conn.content,features="lxml")
print(soup)
links = soup.find_all('script')
J = str(links[3])
from urlextract import URLExtract
logins = soup.find_all('input')
loginfield=[]
for tag in logins:
    input = tag.get('id',None)
    if input is not None:
        loginfield.append(input)
print(loginfield)

options = Options()
options.use_chromium = True
options.add_argument("headless")

edgeBrowser = webdriver.Edge()
# This is the step for maximizing browser window
#edgeBrowser.maximize_window()
#edgeBrowser.minimize_window()
# Browser will get navigated to the given URL
edgeBrowser.get(url)
loginurl=edgeBrowser.current_url


vulns = trypass(password,loginfield,username,edgeBrowser)

if vulns != None:
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
    description = vulns
    solution = "Implement stronger password policies and account lockout mechanisms"
    insert_query = "INSERT INTO critical_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
    values = (vulnerability, description, solution)
    db_cursor.execute(insert_query, values)
    db_connection.commit()

    db_cursor.close()
    db_connection.close()

page_source = edgeBrowser.page_source
#,
#
text_file = open(payloadfile, "r")
xsslist = text_file.read().split('\n')
text_file.close()
print(payloadfile)

text_file = open("input_fields.txt", "r")
urllist = text_file.read().split(', ')
text_file.close()
inject=[]
for i in urllist:
    if i !='':
        inject.append(f'{i}')

for url in inject:
    for payload in xsslist:
        print(url)
        edgeBrowser.get(url)
        wait = WebDriverWait(edgeBrowser, 10)
        wait.until(EC.url_to_be(url))
        skip=injection(edgeBrowser,payload,url,username,password,loginfield,loginurl)
        if skip ==1:
            break