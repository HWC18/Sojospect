from flask import Flask, flash, render_template, request, send_file, send_from_directory,  make_response, redirect, jsonify, session, abort, url_for
import signal
import mysql.connector
import configparser

from bs4 import BeautifulSoup
from xhtml2pdf import pisa

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support.ui import Select
from subprocess import Popen, PIPE
import threading
import webbrowser
import os
import subprocess
import functools
from datetime import datetime
from datetime import date
import pdfkit as pdf
import io


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define a list of routes that do not require authentication
AUTH_EXEMPT_ROUTES = ['/login', '/']

# Load the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Get values from the config file
db_host = config.get('SQL Database', 'db_host')
db_user = config.get('SQL Database', 'db_user')
db_password = config.get('SQL Database', 'db_password')

# Configure MySQL connection
db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password
)

# Create a cursor object
cursor = db.cursor()

# Check if the 'vulnerabilities' database exists
cursor.execute("SHOW DATABASES")
databases = [database[0] for database in cursor]

if 'vulnerabilities' not in databases:
    # Create the 'vulnerabilities' database
    cursor.execute("CREATE DATABASE vulnerabilities")

# Switch to the 'vulnerabilities' database
db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database="vulnerabilities"
)
cursor = db.cursor()

# Create the 'pdf_files' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS pdf_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    saved_time DATETIME,
    file_data LONGBLOB
)
""")

# Create the 'users' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    admin TINYINT(1),
    username VARCHAR(50),
    password VARCHAR(255)
)
""")

# Create the 'vulnerabilities' table
cursor.execute("""
CREATE TABLE IF NOT EXISTS vulnerabilities (
    Severity VARCHAR(50),
    `Vulnerability Type` VARCHAR(50),
    `Checked at` DATETIME,
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(255),
    checked_date DATE
)
""")

# Check if 'users' table is empty
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]

# If no users exist, prompt to create an admin account
if user_count == 0:
    admin_username = input("Enter admin username: ")
    admin_password = input("Enter admin password: ")

    # Insert the admin account into the 'users' table
    cursor.execute("INSERT INTO users (admin, username, password) VALUES (1, %s, %s)", (admin_username, admin_password))
    db.commit()


@app.route('/')
def login_page():
    return render_template('login.html')

def check_credentials(username, password):
    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    values = (username, password)
    cursor.execute(query, values)
    user = cursor.fetchone()
    cursor.close()

    if user:
        return user  # Return the user row
    else:
        return None
        
# Define a route for the login request
@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        # Handle JSON request
        data = request.get_json()
        username = data['username']
        password = data['password']

        # Perform authentication logic
        user = check_credentials(username, password)
        if user:
            session['username'] = username  # Store the authenticated username in the session
            session['admin'] = user[1]  # Store the admin value in the session
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    else:
        # Handle HTML request (form submission)
        username = request.form['username']
        password = request.form['password']

        # Perform authentication logic
        user = check_credentials(username, password)
        if user:
            session['username'] = username  # Store the authenticated username in the session
            session['admin'] = user  # Store the admin value in the session
            return redirect('/') 
        else:
            return redirect('/login')  # Redirect back to the login page with an error message

def admin_required(route_func):
    @functools.wraps(route_func)
    def decorated_route(*args, **kwargs):
        if session.get('admin'):
            return route_func(*args, **kwargs)
        else:
            abort(401)  # Unauthorized

    return decorated_route

def is_authenticated():
    return 'username' in session

@app.before_request
def before_request():
    if request.path not in AUTH_EXEMPT_ROUTES and not is_authenticated():
        print("Not logged in")
        abort(401)
    else:
        print(session)

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data
    session.clear()

    # Redirect the user to the login page
    return redirect(url_for('login_page'))

# Set up a route to fetch data from the MySQL table
@app.route('/website4')

def vulnerabilities():
    cursor = db.cursor()
    query = "SELECT Severity, `Vulnerability Type`, `url`, `Checked at` FROM vulnerabilities"
    cursor.execute(query)
    data = cursor.fetchall()
    data.reverse()
    print(data)
    cursor.close()
    username = session['username']
    admin = session['admin']
    return render_template('website4.html', data=data, username=username, admin=admin)

@app.route('/website')
def website1():
    # Connect to the MySQL database
    db_connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database='vulnerabilities'
    )
    cursor = db_connection.cursor()

    # Fetch the latest ID from the vulnerabilities table
    cursor.execute("SELECT id FROM vulnerabilities ORDER BY id DESC LIMIT 1")
    latest_id = cursor.fetchone()

    if latest_id is None:
        # Handle case where no data is found
        latest_url = None
        lowrisk = 0
        mediumrisk = 0
        highrisk = 0
        conductedscans = 0
    else:
        latest_id = latest_id[0]

        # Fetch the URL from the latest row using the latest_id
        cursor.execute("SELECT url FROM vulnerabilities WHERE id = %s", (latest_id,))
        latest_url = cursor.fetchone()[0]

        # Fetch the counts of severity levels based on the latest 'Checked at' value
        cursor.execute("""
            SELECT
                SUM(CASE WHEN severity = 'High' THEN 1 ELSE 0 END) AS highrisk,
                SUM(CASE WHEN severity = 'Medium' THEN 1 ELSE 0 END) AS mediumrisk,
                SUM(CASE WHEN severity = 'Low' THEN 1 ELSE 0 END) AS lowrisk
            FROM vulnerabilities
            WHERE `Checked at` = (SELECT MAX(`Checked at`) FROM vulnerabilities)
        """)
        counts = cursor.fetchone()

        highrisk = counts[0]
        mediumrisk = counts[1]
        lowrisk = counts[2]

        cursor.execute("SELECT url FROM vulnerabilities WHERE id = %s", (latest_id,))
        latest_url = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT `Checked at`) FROM vulnerabilities")
        conductedscans = cursor.fetchone()[0]

    # Close the database connection
    cursor.close()
    db_connection.close()

    currentvulnerabilities = lowrisk + mediumrisk + highrisk
    username = session['username']
    admin = session['admin']

    return render_template('Website.html', lowrisk=lowrisk, mediumrisk=mediumrisk, highrisk=highrisk,
                            conductedscans=conductedscans, currenttargets=latest_url,
                            currentvulnerabilities=currentvulnerabilities, username=username, admin=admin)

@app.route('/download_pdf', methods=['POST'])
def download_pdf(datecheck):
    today = date.today()

    connection = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database='vulnerabilities'
    )

    # Create a cursor object
    cursor = connection.cursor()

    # Execute a query to fetch the table data
    query = 'SELECT Severity, `Vulnerability Type`, `Checked at` FROM vulnerabilities'
    cursor.execute(query)

    # Fetch column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Fetch all the rows from the result set
    rows = cursor.fetchall()

    # Store the data in a tuple
    data_header = tuple(column_names)
    data_tuple = tuple(rows)

    # print(data_header)
    # print(data_tuple)

    # Generate the HTML table content
    table_content = '<table style="border:none;border-collapse:collapse;"><tbody>  '
    table_content += '<tr style="height:0pt;" >'
    for column in column_names:
        table_content += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;background-color:#e7e6e6;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;">{column}</span></p></td>'
    table_content += '</tr>'

    for row in rows:
        table_content += '<tr>'
        for value in row:
            table_content += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap; ">{value}</span></p></td>'
        table_content += '</tr>'

    table_content += '</tbody></table>'

    # Execute a query to fetch the table data

    # Fetch column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Fetch all the rows from the result set
    rows = cursor.fetchall()

    # Store the data in a tuple
    data_header = tuple(column_names)
    data_tuple = tuple(rows)

    # print(data_header)'unrestricted_file_upload.py'
    # print(data_tuple)

    omitted = "Ommitted Scans:<br>"
    config = configparser.ConfigParser()
    config.read('config.ini')
    scripts = ['cookie_attribute_checking.py','unrestricted_file_upload.py','Get_Input_Urls.py','bruteforce.py', 'Forced_browsing.py', 'injection.py', 'sessionReplay.py', "overinformative_error.py", "robots_txt.py"]
    for script in scripts:
        setting_name = script.split('.')[0]  # Extract the script name without the extension
        setting_value = config.get('Advanced Scan Settings', 'scan_for_' + setting_name, fallback='1')  # Use fallback value of '1' if setting is not found

        if setting_value == '0': 
            omitted += setting_name + ", "

    critical_severity = ""
    # Generate the HTML table content
    critical_severity += '<table style="border:none;border-collapse:collapse;"><tbody>  '
    critical_severity += '<tr style="height:0pt;" >'
    for column in column_names:
        critical_severity += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;background-color:#e7e6e6;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;">{column}</span></p></td>'
    critical_severity += '</tr>'

    for row in rows:
        critical_severity += '<tr>'
        for value in row:
            critical_severity += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap; ">{value}</span></p></td>'
        critical_severity += '</tr>'

    critical_severity += '</tbody></table>'

    query_low = 'SELECT COUNT(*) FROM low_severity'
    cursor.execute(query_low)
    lowcount = cursor.fetchone()[0]

    query_medium = 'SELECT COUNT(*) FROM medium_severity'
    cursor.execute(query_medium)
    mediumcount = cursor.fetchone()[0]

    query_high = 'SELECT COUNT(*) FROM critical_severity'
    cursor.execute(query_high)
    highcount = cursor.fetchone()[0]

    # Execute a query to fetch the table data
    query = 'SELECT Vulnerability, Description, Solution FROM medium_severity'
    cursor.execute(query)

    # Fetch column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Fetch all the rows from the result set
    rows = cursor.fetchall()

    # Store the data in a tuple
    data_header = tuple(column_names)
    data_tuple = tuple(rows)

    # print(data_header)
    # print(data_tuple)

    # Generate the HTML table content
    medium_severity = '<table style="border:none;border-collapse:collapse;"><tbody>  '
    medium_severity += '<tr style="height:0pt;" >'
    for column in column_names:
        medium_severity += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;background-color:#e7e6e6;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;">{column}</span></p></td>'
    medium_severity += '</tr>'

    for row in rows:
        medium_severity += '<tr>'
        for value in row:
            medium_severity += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap; ">{value}</span></p></td>'
        medium_severity += '</tr>'

    medium_severity += '</tbody></table>'


    # Execute a query to fetch the table data
    query = 'SELECT Vulnerability, Description, Solution FROM low_severity'
    cursor.execute(query)

    # Fetch column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Fetch all the rows from the result set
    rows = cursor.fetchall()

    # Store the data in a tuple
    data_header = tuple(column_names)
    data_tuple = tuple(rows)

    # print(data_header)
    # print(data_tuple)

    # Generate the HTML table content
    low_severity = '<table style="border:none;border-collapse:collapse;"><tbody>  '
    low_severity += '<tr style="height:0pt;" >'
    for column in column_names:
        low_severity += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;background-color:#e7e6e6;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;">{column}</span></p></td>'
    low_severity += '</tr>'

    for row in rows:
        low_severity += '<tr>'
        for value in row:
            low_severity += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap; ">{value}</span></p></td>'
        low_severity += '</tr>'

    low_severity += '</tbody></table>'



    # Execute a query to fetch the table data
    query = 'SELECT `Action to Take`, Description FROM actions'
    cursor.execute(query)

    # Fetch column names from the cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Fetch all the rows from the result set
    rows = cursor.fetchall()

    # Store the data in a tuple
    data_header = tuple(column_names)
    data_tuple = tuple(rows)

    # print(data_header)
    # print(data_tuple)

    # Generate the HTML table content
    actions = '<table style="border:none;border-collapse:collapse;"><tbody>  '
    actions += '<tr style="height:0pt;" >'
    for column in column_names:
        actions += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;background-color:#e7e6e6;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;">{column}</span></p></td>'
    actions += '</tr>'

    for row in rows:
        actions += '<tr>'
        for value in row:
            actions += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap; ">{value}</span></p></td>'
        actions += '</tr>'

    actions += '</tbody></table>'
    username = session['username']
    scanned = "Scanned by: " + username
    datetdy = today.strftime("%d/%m/%Y")
    sj_version = "v1.0.0"
    # Close the cursor and the database connection

    # Fetch the latest ID from the vulnerabilities table
    cursor.execute("SELECT id FROM vulnerabilities ORDER BY id DESC LIMIT 1")
    latest_id = cursor.fetchone()

    if latest_id is None:
        # Handle case where no data is found
        latest_url = None
    else:
        latest_id = latest_id[0]

        # Fetch the URL from the latest row using the latest_id
        cursor.execute("SELECT url FROM vulnerabilities WHERE id = %s", (latest_id,))
        latest_url = cursor.fetchone()[0]

    # Read the existing HTML template
    with open(".\\templates\\Report.html", 'r') as file:
        html_template = file.read()
    # Replace a placeholder in the template with the generated table content
    html_output = html_template.replace('{{omitted}}', omitted).replace('{{reporturl}}', latest_url).replace('{{lowcount}}', str(lowcount)).replace('{{mediumcount}}', str(mediumcount)).replace('{{highcount}}', str(highcount)).replace('{{table_content}}', table_content).replace('{{critical_severity}}', critical_severity).replace('{{medium_severity}}', medium_severity).replace('{{low_severity}}', low_severity).replace('{{actions}}', actions).replace('{{scanned_by}}', scanned).replace('{{date}}', datetdy).replace('{{version}}', sj_version)

    # Write the final HTML output to a file
    with open(".\\templates\\Output.html", 'w') as file:
        file.write(html_output)

    # Set the path to wkhtmltopdf executable file
    path_wkhtmltopdf = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"  # This may vary depending on your system
    config = pdf.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # Get the current date and time
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    user = session['username']
    pdf_file_name = f'report_{current_datetime}_scanned_by_{user}.pdf'

    pdf.from_file('.\\templates\\Output.html', pdf_file_name, configuration=config)

    with open(pdf_file_name, 'rb') as pdf_file:
        file_data = pdf_file.read()
    # Create a cursor object
    cursor = connection.cursor()

    # Insert the data into the pdf_files table
    insert_query = "INSERT INTO pdf_files (filename, saved_time, file_data) VALUES (%s, %s, %s)"
    data = (pdf_file_name, datecheck, file_data)
    cursor.execute(insert_query, data)
    connection.commit()
    cursor.close()
    connection.close()
    # Return the PDF file as an attachment with the formatted file name
    return send_file(pdf_file_name, as_attachment=True)


processes = []

@app.route('/execute', methods=['POST'])
def execute_script(user_input):
    
    db_connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database='vulnerabilities'
    )

    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM low_severity")
    cursor.execute("DELETE FROM medium_severity")
    cursor.execute("DELETE FROM critical_severity")
    db_connection.commit()
    db_connection.close()

    scripts_folder = 'scripts/'
    scripts = ['cookie_attribute_checking.py','unrestricted_file_upload.py','Get_Input_Urls.py','bruteforce.py', 'Forced_browsing.py', 'injection.py', 'sessionReplay.py', "overinformative_error.py", "robots_txt.py"]

    # Load the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    for script in scripts:
        script_path = scripts_folder + script
        setting_name = script.split('.')[0]  # Extract the script name without the extension
        setting_value = config.get('Advanced Scan Settings', 'scan_for_' + setting_name, fallback='1')  # Use fallback value of '1' if setting is not found

        if setting_value == '1':  # Run the script if the setting value is 1
            process = subprocess.Popen(['python', script_path, user_input])
            processes.append(process)

    for process in processes:
        process.wait()


    result = 'Scripts executed successfully.'
    return result

@app.route('/cancel', methods=['POST'])
def cancel_processes():
    for process in processes:
        if os.name == 'nt':  # Windows platform
            process.terminate()  # Terminate the process
        else:  # Unix-based platforms
            process.send_signal(signal.SIGTERM)  # Send the termination signal


    db_connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database='vulnerabilities'
    )

    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM low_severity")
    cursor.execute("DELETE FROM medium_severity")
    cursor.execute("DELETE FROM critical_severity")
    username = session['username']
    return redirect('/website2')


@app.route('/get_pdf/<group_arg>', methods=['POST'])
def get_pdf(group_arg):
    
    db_connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database='vulnerabilities'
    )

    cursor = db_connection.cursor()

    query = "SELECT file_data FROM pdf_files WHERE saved_time = %s"
    cursor.execute(query, (group_arg,))
    pdf_data = cursor.fetchone()

    if pdf_data:
        pdf_data = pdf_data[0]
        # Replace 'application/pdf' with the appropriate MIME type for your PDF
        return send_file(io.BytesIO(pdf_data), mimetype='application/pdf')
    else:
        return "PDF not found."
    
@app.route('/process', methods=['POST'])
def process_input():
    db_connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database='vulnerabilities'
    )

    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = db_connection.cursor()

    input_data = request.form['input_field']
    result = execute_script(input_data)
    username = session['username']

    scripts_folder = 'scripts/'
    scripts = ['cookie_attribute_checking.py','unrestricted_file_upload.py','Get_Input_Urls.py', 'bruteforce.py', 'Forced_browsing.py', 'injection.py', 'sessionReplay.py',
               "overinformative_error.py", "robots_txt.py"]

    # Load the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')
    for script in scripts:
        setting_name = script.split('.')[0]  # Extract the script name without the extension
        setting_value = config.get('Advanced Scan Settings', 'scan_for_' + setting_name, fallback='1')  # Use fallback value of '1' if setting is not found

        if setting_value == '0':  # Insert a row with "Omitted" severity and script name as Vulnerability Type
            cursor.execute("INSERT INTO vulnerabilities (Severity, `Vulnerability Type`, url, `Checked at`) VALUES (%s, %s, %s, %s)",
                           ("Omitted", setting_name, input_data, current_datetime))
    
    # Retrieve data from low_severity, medium_severity, and critical_severity tables
    cursor.execute("SELECT Vulnerability FROM low_severity")
    low_severity_data = cursor.fetchall()
    
    cursor.execute("SELECT Vulnerability FROM medium_severity")
    medium_severity_data = cursor.fetchall()
    
    cursor.execute("SELECT Vulnerability FROM critical_severity")
    critical_severity_data = cursor.fetchall()

    # Insert data into vulnerabilities table with corresponding severity values
    # Check if any vulnerabilities are added from the severity tables
    if low_severity_data or medium_severity_data or critical_severity_data:
        # Insert data into vulnerabilities table with corresponding severity values
        for vulnerability in low_severity_data:
            cursor.execute("INSERT INTO vulnerabilities (Severity, `Vulnerability Type`, url, `Checked at`) VALUES (%s, %s, %s, %s)",
                           ("Low", vulnerability[0], input_data, current_datetime))

        for vulnerability in medium_severity_data:
            cursor.execute("INSERT INTO vulnerabilities (Severity, `Vulnerability Type`, url, `Checked at`) VALUES (%s, %s, %s, %s)",
                           ("Medium", vulnerability[0], input_data, current_datetime))

        for vulnerability in critical_severity_data:
            cursor.execute("INSERT INTO vulnerabilities (Severity, `Vulnerability Type`, url, `Checked at`) VALUES (%s, %s, %s, %s)",
                           ("High", vulnerability[0], input_data, current_datetime))
    else:
        # Insert a row with "None" severity and "No vulnerability" type
        cursor.execute("INSERT INTO vulnerabilities (Severity, `Vulnerability Type`, url, `Checked at`) VALUES (%s, %s, %s, %s)",
                       ("None", "No vulnerabilities found!", input_data, current_datetime))

    download_pdf(current_datetime)

    cursor.execute("DELETE FROM low_severity")
    cursor.execute("DELETE FROM medium_severity")
    cursor.execute("DELETE FROM critical_severity")

    # Commit changes to the database
    db_connection.commit()
    db.commit()

    cursor.close()
    db_connection.close()
    
    return redirect('/website4')


@app.route('/website6', methods=['GET', 'POST'])
def config_page():
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    if request.method == 'POST':
        # Update the configuration based on form submission
        for section in config.sections():
            for key in config[section]:
                new_value = request.form.get(f'{section}-{key}')
                config.set(section, key, new_value)

        # Save the updated configuration to the file+
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    admin = session['admin']

    return render_template('website6.html', config=config, username=session['username'], admin=admin)

@app.route('/website2', methods=['GET', 'POST'])
def website2():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if request.method == 'POST':
        # Update the configuration based on form submission
        for section in config.sections():
            for key in config[section]:
                new_value = str(request.form.get(f'{section}-{key}'))
                config.set(section, key, new_value)

        # Save the updated configuration to the file+
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        admin = session['admin']
        return render_template('Scan.html', username=session['username'], admin=admin)
            
    admin = session['admin']
    return render_template('Website2.html', config=config, username=session['username'], admin=admin)

@app.route('/website7')
def pdf_list():
    pdf_folder = 'pdfs'  # Path to the folder containing the PDF files
    pdf_files = os.listdir(pdf_folder)  # Get the list of PDF files

    admin = session['admin']
    return render_template('Website7.html', pdf_files=pdf_files, username=session['username'], admin=admin)

@app.route('/open_pdf', methods=['POST'])
def open_pdf():
    pdf_folder = 'pdfs'  # Path to the folder containing the PDF files
    filename = request.form['filename']
    
    # Create a response with the PDF file
    response = make_response(send_from_directory(pdf_folder, filename))
    response.headers['Content-Type'] = 'application/pdf'
    
    return response

@app.route('/admin')
@admin_required
def index():
    # Fetch all users from the user table
    cursor = db.cursor()
    cursor.execute("select username, password, admin from users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('Admin.html', users=users)

@app.route('/add_user', methods=['POST'])
@admin_required
def add_user_route():
    # Get the form data submitted by the user
    username = request.form.get('username')
    password = request.form.get('password')
    admin = int(request.form.get('admin', 0))  # Convert to integer (0 or 1)

    try:
        # Insert the new user into the user table
        cursor = db.cursor()
        query = "INSERT INTO users (username, password, admin) VALUES (%s, %s, %s)"
        values = (username, password, admin)
        cursor.execute(query, values)
        db.commit()
        cursor.close()
    except mysql.connector.Error as e:
        # Show the MySQL error as a message box
        flash(f"MySQL Error: {str(e)}", 'error')
        return redirect('/admin')

    return redirect('/admin')


if __name__ == '__main__':
    url = 'http://127.0.0.1:5000'
    webbrowser.open(url)
    app.run(debug=False)

