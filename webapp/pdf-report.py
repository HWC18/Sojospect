import pdfkit as pdf
import mysql.connector
import os

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
query = 'SELECT `Severity`, `Vulnerability Type`, `Checked at` FROM vulnerabilities'
cursor.execute(query)

# Fetch column names from the cursor description
column_names = [desc[0] for desc in cursor.description]

# Fetch all the rows from the result set
rows = cursor.fetchall()

# Store the data in a tuple
data_header = tuple(column_names)
data_tuple = tuple(rows)

print(data_header)
print(data_tuple)

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

# Close the cursor and the database connection
cursor.close()
connection.close()

# Read the existing HTML template
with open('./templates/Website4.html', 'r') as file:
    html_template = file.read()

# Replace a placeholder in the template with the generated table content
html_output = html_template.replace('{{table_content}}', table_content)

# Write the final HTML output to a file
with open('output.html', 'w') as file:
    file.write(html_output)

# Set the path to wkhtmltopdf executable file
path_wkhtmltopdf = ".\wkhtmltopdf\\bin\\wkhtmltopdf.exe"  # This may vary depending on your system
config = pdf.configuration(wkhtmltopdf=path_wkhtmltopdf)


# pdf.from_file('generated.html','new_report2.pdf', configuration=config)

# pdf.from_file('template.html','new_report4.pdf', configuration=config)


output_filename = 'new_report.pdf'
output_path = os.path.join(os.getcwd(), output_filename)

counter = 1
while os.path.exists(output_path):
    counter += 1
    output_filename = f"new_report{counter}.pdf"
    output_path = os.path.join(os.getcwd(), output_filename)

# Use the updated filename in your code
pdf.from_file('output.html', output_filename, configuration=config)
