import pdfkit as pdf
import mysql.connector
from datetime import date
today = date.today()

# Establish a connection to the MySQL database
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
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
    table_content += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap;">{column}</span></p></td>'
table_content += '</tr>'

for row in rows:
    table_content += '<tr>'
    for value in row:
        table_content += f'<td style="border-left:solid #000000 0.5pt;border-right:solid #000000 0.5pt;border-bottom:solid #000000 0.5pt;border-top:solid #000000 0.5pt;vertical-align:top;padding:0pt 5.4pt 0pt 5.4pt;overflow:hidden;overflow-wrap:break-word;"><p dir="ltr" style="line-height:1.2;margin-top:0pt;margin-bottom:0.1pt;"><span style="font-size: 30px; font-family: Calibri, sans-serif; color: rgb(0, 0, 0); background-color: transparent; font-weight: 400; font-style: normal; font-variant: normal; text-decoration: none; vertical-align: baseline; white-space: pre-wrap; ">{value}</span></p></td>'
    table_content += '</tr>'

table_content += '</tbody></table>'
scanned = "Scanned by: Fahim"
datetdy = today.strftime("%d/%m/%Y")
sj_version = "v1.1.1"
# Close the cursor and the database connection
cursor.close()
connection.close()
# Read the existing HTML template
with open(".\\templates\\Report.html", 'r') as file:
    html_template = file.read()
# Replace a placeholder in the template with the generated table content
html_output = html_template.replace('{{table_content}}', table_content).replace('{{scanned_by}}', scanned).replace('{{date}}', datetdy).replace('{{version}}', sj_version)

# Write the final HTML output to a file
with open(".\\templates\\Output.html", 'w') as file:
    file.write(html_output)

# Set the path to wkhtmltopdf executable file
path_wkhtmltopdf = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"  # This may vary depending on your system
config = pdf.configuration(wkhtmltopdf=path_wkhtmltopdf)


pdf.from_file('.\\templates\\Output.html','.\\templates\\new_report6.pdf', configuration=config)


# pdf.from_file('Sample Vulnerability Assesment Report (1).htm','new_report.pdf', configuration=config)

# url = 'https://docs.google.com/document/d/1LBwOM9DVN5MWCFS8-aAe6TB5dNhCTiIB/edit?usp=sharing&ouid=117805999518184891080&rtpof=true&sd=true'

# pdf.from_url(url, 'website.pdf', configuration=config)