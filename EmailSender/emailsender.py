import json
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

AWS_REGION = 'us-east-1'
ses_client = boto3.client('ses', region_name=AWS_REGION)

def lambda_handler(event, context):
    SENDER_EMAIL = 'contact2hriship@gmail.com'

    # Extract customer email and invoice link from the event
    customer_email = event.get('customer_email').lower()
    print(customer_email)
    #customer_email =SENDER_EMAIL
    invoice_link = event.get('invoice_link')

    if not customer_email or not invoice_link:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing customer_email or invoice_link')
        }

    # Send the email
    response = send_email(SENDER_EMAIL, customer_email, invoice_link)
    return response

def send_email(sender_email, recipient_email, invoice_link):
    subject = 'Your Invoice Payment'
    body = f'Dear Customer, please find your invoice here: {invoice_link}'

    # Set up email content
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Add the message body
    message.attach(MIMEText(body, 'plain'))

    # Send the email using Amazon SES
    try:
        response = ses_client.send_raw_email(
            Source=message['From'],
            Destinations=[message['To']],
            RawMessage={'Data': message.as_string()}
        )
        print("Email sent. Message ID:", response['MessageId'])
        return {
            'statusCode': 200,
            'body': json.dumps('Email sent successfully!')
        }
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error sending email: {str(e)}')
        }
