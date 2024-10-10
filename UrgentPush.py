
import os
import time
import smtplib
import xml.etree.ElementTree as ET
import json
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from pathlib import Path
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
        send_email(from_address, config.get("recipient"), subject, formatted_message, use_oauth2)

    except Exception as e:
        print(f"An error occurred while formatting or sending the email: {e}")

def send_email(sender, recipient, subject, body, use_oauth2):
    try:
        smtp_server = config.get("smtp_server") ## YOU WILL NEED THE SMTP SERVER. SOME TYPICAL ONES: smtp.office365.com (Office 365), smtp.mail.me.com (iCloud), smtp.gmail.com (Gmail), smtp-mail.outlook.com (Outlook)...etc ##
        smtp_port = config.get("smtp_port", 587) ## MOST SERVERS USE 25, 465, 587, AND 2525 
        smtp_username = config.get("smtp_username") ## YOUR EMAIL, AKA YOUR LOGIN FOR THIS SERVICE. ##

        if use_oauth2:
            # OAuth2 CONFIG. ONLY FILL OUT IF USING OAUTH2
            client_id = config.get("client_id")
            client_secret = config.get("client_secret")
            token_url = config.get("token_url")

            # OAuth2 token Fetch
            client = BackendApplicationClient(client_id=client_id)
            oauth = OAuth2Session(client=client)
            token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret)

            # FILL OUT OAUTH2 ACCESS TOKEN BELOW
            auth = lambda: (smtp_username, token['access_token'])
        else:
            smtp_password = config.get("smtp_password") ## IF NOT USING OAUTH2, SOME SERVICES REQUIRE APP-SPECIFIC PASSWORDS. SEE DOCUMENTATION ##
            auth = lambda: (smtp_username, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient
        msg['Subject'] = f'URGENT: {subject}' ## CHANGE TO DESIRED SUBJECT ##

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(*auth())
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")

if __name__ == "__main__":
    bundle_dir = Path(__file__).parent.resolve()
    exec_dir = bundle_dir
    in_bundle = False
    config = {}
    LOGLEVEL = "DEBUG"
    with open('config.json') as f:
        config = json.load(f)

    if not os.path.isdir(exec_dir / "logs"):
        os.mkdir(exec_dir / "logs")
    logger = logging.getLogger("urgentpush_logs")
    logging.basicConfig(filename=exec_dir/"logs/urgentpush.log", filemode='a', level=LOGLEVEL, format='%(name)s - %(levelname)s - %(message)s')

    logger.info("====init====")
 
    ## CHANGE DIRECTORY LOCATION IN CONFIG TO URGENT MESSAING PROGRAM FOLDER > MESSAGING > LOGIN NAME > ALERTS FOLDER. XML FILES SHOULD BE IN HERE. ##
    directory = config.get("directory")

    # Track files processed 
    processed_files = set()

    # Toggleable OAuth2
    use_oauth2 = False  ## CHANGE THIS TO TRUE IF USING OAUTH2 ##

# Path to log file
log_file = os.path.join(directory, 'processed_files_log.txt') #THIS LOG FILE NAME CAN BE CHANGED. THIS IS TO TRACK WHAT HAS ALREADY SENT.

# Load processed files from log file
def load_processed_files(log_file):
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            return set(f.read().splitlines())
    return set()

# Save processed files to log file
def save_processed_files(log_file, processed_files):
    with open(log_file, 'w') as f:
        f.write('\n'.join(processed_files))

# Load processed files from log
processed_files = load_processed_files(log_file)

while True:
    # Get list of XML files in directory
    xml_files = [file for file in os.listdir(directory) if file.endswith('.xml') and not file.startswith('weeklyhb')]

    # Check for new files
    new_files = [file for file in xml_files if file not in processed_files]

    # Process new files
    for file in new_files:
        xml_file_path = os.path.join(directory, file)
        convert_xml_to_email(xml_file_path)
        processed_files.add(file)

    # Save processed files to log file
    save_processed_files(log_file, processed_files)

    # Sleep for 1 minute before checking again
    time.sleep(60) #THIS CAN BE CHANGED IF YOU WANT FEWER OR MORE CHECKS OF THE CLIENT.
        
        # UrgentPush By Jamie Needham
        # Version 1.57 Logging/Entra 10/10/2024
