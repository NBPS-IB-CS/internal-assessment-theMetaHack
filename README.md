# Invoice-Manager-IA-project
Invoice manager using the cloud for my IB Computer Science IA project

Folder invoice-manager-flask is the code for the Flask website. The rest of the folders are AWS code. EmailSender is used to send reminder emails, and InvoiceMover is used to sort uploaded invoices in the AWS s3 bucket. InvoiceMover is configured to trigger when a new invoice is uploaded to AWS. Both are AWS Lambda functions.

To run the flask application, follow the steps at [the flask installation guide](https://flask.palletsprojects.com/en/3.0.x/installation/). Specifically, creating and running the environment. Many functions will not work without entering AWS access keys. 

