import os
import time
import smtplib
import xml.etree.ElementTree as ET
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def convert_xml_to_email(xml_file):
    try:
        # Parse XML
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Extract data
        subject = root.find('subject').text
        date_sent = root.find('time_sent').text[:8]  # Extracting only the date part
        time_sent = root.find('time_sent').text[8:14]  # Extracting only the time part
        from_address = root.find('from').text
        message_body = root.find('body').text

        # Format email message as HTML ## YOU MAY REFORMAT AS NEEDED. TIME AND DATE WILL NOT BE FULLY CORRECT SOMETIMES. ##
        formatted_message = f"""
            <html>
                <body>
                    <h2 style="color:red;">Subject: URGENT: {subject}</h2>
                    <p>Sender: {from_address}</p>
                    <p>Date: {date_sent}</p>
                    <p>Time: {time_sent}</p>
                    <hr>
                    <p><strong>Message:</strong></p>
                    <p>{message_body}</p>
                </body>
            </html>
        """

        # Send email 
        send_email(from_address, 'Recipient@emailhost.com', subject, formatted_message) ## INSERT RECIPIENT IF WANTING TO SEND TO AN ADDRESS. USE YOUR OWN EMAIL ADDRESS HERE OTHERWISE. ##

    except Exception as e:
        print(f"An error occurred while formatting or sending the email: {e}")

def send_email(sender, recipient, subject, body):
    try:
        smtp_server = 'smtp.SERVERADDRESS.com' ## YOU WILL NEED THE SMTP SERVER. SOME TYPICAL ONES: smtp.office365.com (Office 365), smtp.mail.me.com (iCloud), smtp.gmail.com (Gmail), smtp-mail.outlook.com (Outlook)...etc ##
        smtp_port = 587 ## MOST SERVERS USE 25, 465, 587, AND 2525 ##
        smtp_username = 'Sender@emailhost.com' ## YOUR EMAIL, AKA YOUR LOGIN FOR THIS SERVICE. ##
        smtp_password = 'Mysupersecretpassword' ## PASSWORD. BE AWARE. IF YOU NEED TO USE OAUTH2 THERE ARE ADDITIONAL CONFIGURATIONS. THIS SCIRPT DOES NOT HANDLE INCLUSION OF OAUTH2 TOKENS. ##

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient
        msg['Subject'] = f'URGENT: {subject}'

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")


# Directory to monitor
directory = r'C:\FILELOCATION\FILESUBLOCATION\DEEPERFOLDER' ## INCLUDE EXACT LOCATION FOR THE UMS MESSAGE SYSTEM WHERE THE .XML FILES ARE STORED. ##

# Track files already processed
processed_files = set()

while True:
    # Get list of XML files in directory
    xml_files = [file for file in os.listdir(directory) if file.endswith('.xml') and not file.startswith('weeklyhb')]

    # Check for new
    new_files = [file for file in xml_files if file not in processed_files]

    # Process new
    for file in new_files:
        xml_file_path = os.path.join(directory, file)
        convert_xml_to_email(xml_file_path)
        processed_files.add(file)

    # 1m sleep before recheck
    time.sleep(60)
    
    # UrgentPush By Jamie Needham
    # Version 1.52 6/12/24 