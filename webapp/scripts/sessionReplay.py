from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import configparser
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

url = user_input

target_url = user_input
driver = webdriver.Chrome()
driver.maximize_window()

def sessionReplay(url, username, password):
    login_url = url + 'login' 
    driver.get(login_url)
    driver.find_element(By.ID, 'loginId').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password, Keys.RETURN)
    time.sleep(5)

    Admin_cookie_value = driver.get_cookie('APP_SESSION')['value']
    #print(Admin_cookie_value)
    driver.execute_script('window.open('');')
    driver.switch_to.window(driver.window_handles[1])
    time.sleep(5)

    driver.get(login_url)
    driver.find_element(By.ID, 'loginId').send_keys('U0000028')
    driver.find_element(By.ID, 'password').send_keys('password', Keys.RETURN)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.profile img')))
    originalProfile = driver.find_element(By.CSS_SELECTOR, 'span.profile img').get_attribute('src')
    print(originalProfile)
    
    User_cookie = driver.get_cookie('APP_SESSION')
    #print(User_cookie['value'])
    User_cookie['value'] = Admin_cookie_value
    driver.delete_cookie('APP_SESSION')
    driver.add_cookie(User_cookie)

    driver.refresh()
    newProfile = driver.find_element(By.CSS_SELECTOR, 'span.profile img').get_attribute('src')
    #print(newProfile)

    if originalProfile != newProfile:
        db_cursor = db_connection.cursor()
        # Insert a row into the MySQL table
        vulnerability = "Session Replay"
        description = "User interactions on the website can be replayed by attackers."
        solution = "Ensure that data transferred is encrypted."
        insert_query = "INSERT INTO medium_severity (Vulnerability, Description, Solution) VALUES (%s, %s, %s)"
        values = (vulnerability, description, solution)
        db_cursor.execute(insert_query, values)
        db_connection.commit()

        db_cursor.close()
        db_connection.close()
        return 'Session replay was successful'
    else:
        return 'Session replay was unsucessful'

test = sessionReplay(target_url, 'Admin', 'password')
print(test)