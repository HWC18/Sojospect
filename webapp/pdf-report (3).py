import pdfkit as pdf
import mysql.connector
from datetime import date
today = date.today()

# Establish a connection to the MySQL database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1qwer$#@!',
    database='sojospect'
)

# Create a cursor object
cursor = connection.cursor()

# Execute a query to fetch the table data
query = 'SELECT Category, Description, Scanned FROM vulnerabilities'
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
query = 'SELECT Plugin, Description, Solution FROM critical_severity'
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
critical_severity = '<table style="border:none;border-collapse:collapse;"><tbody>  '
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


# Execute a query to fetch the table data
query = 'SELECT Plugin, Description, Solution FROM medium_severity'
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
query = 'SELECT Plugin, Description, Solution FROM low_severity'
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

scanned = "Scanned by: Fahim"
datetdy = today.strftime("%d/%m/%Y")
sj_version = "v1.1.1"
# Close the cursor and the database connection
cursor.close()
connection.close()
# Read the existing HTML template
with open("C:\\Users\\FAHIM_MN\\OneDrive\\Desktop\\SP Sem 5\\Report Generation\\template.html", 'r') as file:
    html_template = file.read()
# Replace a placeholder in the template with the generated table content
html_output = html_template.replace('{{table_content}}', table_content).replace('{{critical_severity}}', critical_severity).replace('{{medium_severity}}', medium_severity).replace('{{low_severity}}', low_severity).replace('{{actions}}', actions).replace('{{scanned_by}}', scanned).replace('{{date}}', datetdy).replace('{{version}}', sj_version)

# Write the final HTML output to a file
with open('C:\\Users\\FAHIM_MN\\OneDrive\\Desktop\\SP Sem 5\\Report Generation\\output.html', 'w') as file:
    file.write(html_output)

# Set the path to wkhtmltopdf executable file
path_wkhtmltopdf = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"  # This may vary depending on your system
config = pdf.configuration(wkhtmltopdf=path_wkhtmltopdf)


# pdf.from_file('generated.html','new_report2.pdf', configuration=config)

# pdf.from_file('template.html','new_report4.pdf', configuration=config)

pdf.from_file('C:\\Users\\FAHIM_MN\\OneDrive\\Desktop\\SP Sem 5\\Report Generation\\output.html','C:\\Users\\FAHIM_MN\\OneDrive\\Desktop\\SP Sem 5\\Report Generation\\new_report6.pdf', configuration=config)


# pdf.from_file('Sample Vulnerability Assesment Report (1).htm','new_report.pdf', configuration=config)

# url = 'https://docs.google.com/document/d/1LBwOM9DVN5MWCFS8-aAe6TB5dNhCTiIB/edit?usp=sharing&ouid=117805999518184891080&rtpof=true&sd=true'

# pdf.from_url(url, 'website.pdf', configuration=config)