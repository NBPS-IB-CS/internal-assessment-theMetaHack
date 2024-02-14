import json
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

AWS_REGION = 'us-east-1'


ses_client = boto3.client('ses', region_name=AWS_REGION)

def lambda_handler(event, context):
    
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    #https://invoicemanager-landingzone.s3.amazonaws.com/202410_12341234_Joe.pdf.pdf
    url = source_bucket + '.s3.amazonaws.com/' + source_key 
    filename = source_key
    #customNo = filename[3:6]
    #InvNo = filename[13:16]
    
    SENDER_EMAIL = 'contact2hriship@gmail.com'
    RECIPIENT_EMAIL =  'contact2hriship@gmail.com' 
    
    
    send_email(SENDER_EMAIL, RECIPIENT_EMAIL)
    
def getCustomerEmail(customNo):
    # query database 
    return 'contact2hriship@gmail.com'
    
def send_email(SENDER_EMAIL, RECIPIENT_EMAIL):
    subject = 'Your Invoice Payment'
    
    body = 'Dear Customer, please find your invoice here: '

    # Set up email content
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = RECIPIENT_EMAIL
    message['Subject'] = subject

    # Add the message body
    message.attach(MIMEText(body, 'plain'))
    
    #attach file
    try:
        s3_object = s3_client.get_object(Bucket='your_s3_bucket_name', Key=INVOICE_FILE_PATH)
        attachment = MIMEApplication(s3_object['Body'].read(), Name='invoice.pdf')
        attachment['Content-Disposition'] = f'attachment; filename="invoice.pdf"'
        message.attach(attachment)
    except Exception as e:
        print(f"Error retrieving invoice file: {str(e)}")

    # Send the email using Amazon SES
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

# Uncomment the line below if you want to test the Lambda function locally
# send_email(None, None)


    #source_bucket = event['Records'][0]['s3']['bucket']['name']
    #source_key = event['Records'][0]['s3']['object']['key']
    #filename = source_key
    #s3 = boto3.client('s3')
    
