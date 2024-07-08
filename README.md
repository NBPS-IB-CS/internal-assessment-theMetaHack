# Invoice-Manager-IA-Project

Invoice manager using the cloud for my IB Computer Science IA project.

## Project Structure

- **invoice-manager-flask**: Contains the code for the Flask website.
- **EmailSender**: AWS Lambda function used to send reminder emails.
- **InvoiceMover**: AWS Lambda function used to sort uploaded invoices in the AWS S3 bucket. It is configured to trigger when a new invoice is uploaded to AWS.

## Running the Flask Application

To run the Flask application, follow these steps:

1. Install Flask by following the [Flask installation guide](https://flask.palletsprojects.com/en/3.0.x/installation/).
2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up your AWS access keys. Many functions will not work without entering AWS access keys:
    ```sh
    export AWS_ACCESS_KEY_ID=<your_access_key_id>
    export AWS_SECRET_ACCESS_KEY=<your_secret_access_key>
    ```

5. Run the Flask application:
    ```sh
    flask run
    ```

## AWS Lambda Functions

### EmailSender

The `EmailSender` Lambda function is responsible for sending reminder emails. 

### InvoiceMover

The `InvoiceMover` Lambda function is responsible for sorting uploaded invoices in the AWS S3 bucket. It is triggered automatically when a new invoice is uploaded.

## Configuration

Ensure you have your AWS credentials set up properly in your environment for the Lambda functions to work correctly. You can set these up in your terminal or through an AWS credentials file.

## Additional Resources

For more information on Flask, visit the [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/).
