import os
import time
import smtplib
import xml.etree.ElementTree as ET
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import pytz

def convert_utc_to_central(utc_time_str): ## YOU WILL NEED TO MODIFY THIS TO YOUR TIMEZONE ##
    # Define the UTC and Central Time time zones
    utc_zone = pytz.timezone('UTC')
    central_zone = pytz.timezone('US/Central')
    
    # Parse the UTC time string
    utc_time = datetime.strptime(utc_time_str, '%Y%m%d%H%M%S')
    utc_time = utc_zone.localize(utc_time)
    
    # Convert to Central Time
    central_time = utc_time.astimezone(central_zone)
    
    # Return formatted time
    return central_time.strftime('%m-%d-%y %H:%M:%S') ## MODIFY FORMAT TO YOUR LIKING #

def convert_xml_to_email(xml_file, use_oauth2=False): ## CHANGE THIS TO TRUE TO USE OAUTH2 ##
    try:
        # Parse XML
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Extract data
        subject = root.find('subject').text
        time_sent_str = root.find('time_sent').text
        from_address = root.find('from').text
        message_body = root.find('body').text
        
        # Convert UTC time to Central Time ## CHANGE TO YOUR TIMEZONE ##
        central_time_str = convert_utc_to_central(time_sent_str)
        
        # Extract date and time parts from Central Time
        date_sent, time_sent = central_time_str.split(' ')  

        # Format email message as HTML
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

        # EMAIL SEND. FILL OUT RECIPIENT BELOW.
        send_email(from_address, 'Recipient@emailhost.com', subject, formatted_message, use_oauth2)

    except Exception as e:
        print(f"An error occurred while formatting or sending the email: {e}")

def send_email(sender, recipient, subject, body, use_oauth2):
    try:
        smtp_server = 'smtp.SERVERADDRESS.com' ## YOU WILL NEED THE SMTP SERVER. SOME TYPICAL ONES: smtp.office365.com (Office 365), smtp.mail.me.com (iCloud), smtp.gmail.com (Gmail), smtp-mail.outlook.com (Outlook)...etc ##
        smtp_port = 587 ## MOST SERVERS USE 25, 465, 587, AND 2525 ##
        smtp_username = 'Sender@emailhost.com' ## YOUR EMAIL, AKA YOUR LOGIN FOR THIS SERVICE. ##

        if use_oauth2:
            # OAuth2 CONFIG. ONLY FILL OUT IF USING OAUTH2
            client_id = 'OAUTH2 CLIENT ID'
            client_secret = 'OAUTH2 CLIENT SECRET'
            token_url = 'OAUTH2 TOKEN URL'

            # OAuth2 token Fetch
            client = BackendApplicationClient(client_id=client_id)
            oauth = OAuth2Session(client=client)
            token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)

            # FILL OUT OAUTH2 ACCESS TOKEN BELOW
            auth = lambda: (smtp_username, token['access_token'])
        else:
            smtp_password = 'Mysupersecretpassword' ## IF NOT USING OAUTH2, SOME SERVICES REQUIRE APP-SPECIFIC PASSWORDS. SEE DOCUMENTATION ##
            auth = lambda: (smtp_username, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient
        msg['Subject'] = f'URGENT: {subject}'

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(*auth())
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

## CHANGE DIRECTORY LOCATION TO URGENT MESSAING PROGRAM FOLDER > MESSAGING > LOGIN NAME > ALERTS FOLDER. XML FILES SHOULD BE IN HERE. ##
directory = r'C:\FILELOCATION\FILESUBLOCATION\DEEPERFOLDER' 

# Track files processed (this doesnt always work, sorry)
processed_files = set()

# Toggleable OAuth2
use_oauth2 = False  ## CHANGE THIS TO TRUE IF USING OAUTH2 ##

while True:
    # GET FULL LIST OF XML FILES AND EXCLUDE ALL WEEKLY HEARTBEAT MESSAGES. IF YOU WANT TO TURN TEST MESSAGES BACK ON, RENOVE: "and not file.startswith('weeklyhb')" ##
    xml_files = [file for file in os.listdir(directory) if file.endswith('.xml') and not file.startswith('weeklyhb')]

    # Check for new files
    new_files = [file for file in xml_files if file not in processed_files]

    # Process new files
    for file in new_files:
        xml_file_path = os.path.join(directory, file)
        convert_xml_to_email(xml_file_path, use_oauth2)
        processed_files.add(file)

    # 1m sleep before recheck
    time.sleep(60)
    
    # UrgentPush By Jamie Needham
    # Version 1.56 OAUTH2 edition 6/13/24
