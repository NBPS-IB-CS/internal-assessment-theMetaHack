import json
import re
import os
import boto3

def lambda_handler(event, context):
   
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']
    filename = source_key
        
    destination_bucket ="invoicemanager-documents"
    
    print('source_bucket',source_bucket)
    print('key',source_key)
    
    json = validate_file(filename)
    print(json)
    
    destination_key ="invoicemanager-documents/"+ json['Year'] +'/'+json['Month']+'/'+ filename
    
    #print(validate_file(filename))
    
    
   
    # TODO implement
    return {
        'statusCode': 200,
        #'body': json.dumps('Hello from Hrishi!')
    }


def validate_file(filename):
    pattern = r'(\d{4})(\d{2})_(\d+)_([A-Za-z]+)\.pdf'
    match = re.match(pattern, filename)
    
    if match:
        year = match.group(1)
        month = match.group(2)
        id_number = match.group(3)
        name = match.group(4)

        return {
            "Month": month,
            "Year": year,
            "ID": id_number,
            "Name": name
        }
    else:
        return {
            "Month": 00,
            "Year": 00,
            "ID": 0,
            "Name": name,
            "message":"wrong file name"
        }
        
    print(month)
    print(year)
    print(id_number)
    print(name)
    
