import json
from datetime import datetime
from decimal import Decimal

from flask import Flask, request, render_template, redirect, session, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import bcrypt
import boto3
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

bucket_name = 'invoicemanager-documents'

AWS_REGION = 'us-east-1'
AWS_ACCESS_KEY_ID = 'REDACTED'
AWS_SECRET_ACCESS_KEY = 'REDACTED'

# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name=AWS_REGION)
lambda_client = boto3.client('lambda', aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name=AWS_REGION)

class Invoice(db.Model):
    year = db.Column(db.Integer, primary_key=False)
    month = db.Column(db.Integer, primary_key=False)
    filename = db.Column(db.String(1000), primary_key=False)
    customerid=db.Column(db.String(100), primary_key=False)
    key = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric, primary_key=False)
    paid = db.Column(db.String(100), primary_key=False)
    customeremail = db.Column(db.String(100), primary_key=False)
    createdon = db.Column(db.DateTime, primary_key=False)
    lastReminder = db.Column(db.DateTime, primary_key=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid user')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        inv_list = Invoice.query.order_by(desc(Invoice.lastReminder), desc(Invoice.createdon)).limit(5).all()
        return render_template('dashboard.html', user=user, inv_list=inv_list)

    return redirect('/login')


@app.route('/invoices')
def invoices():

    #inv_list = Invoice.query.order_by(desc(Invoice.createdon)).all()

    inv_list = Invoice.query.order_by(desc(Invoice.createdon)).limit(500).all()

    if not inv_list:
        print("No files found in bucket ")

    return render_template('invoices.html', inv_list=inv_list)



@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')

@app.route('/upload', methods=['POST'])
def upload_file():

    if request.method == 'POST':
        file = request.files['file']
        form_inv = get_invoice_obj(file.filename)
        new_inv  = Invoice.query.filter_by(year= form_inv.year, month=form_inv.month,filename=file.filename).first()
        if new_inv :
            #new_inv.lastReminder = datetime.now()
            print("Invoice already exists")
        else:
            new_inv = form_inv
            new_inv.createdon = datetime.now()

        new_inv.paid = request.form['status']
        new_inv.customeremail = request.form['email']
        new_inv.amount = Decimal(request.form['amount'])
        db.session.add(new_inv)
        db.session.commit()

        print("DB saved")
        # Check if the file is selected
        if file:

            try:

                # Upload file to S3 bucket :
                s3.upload_fileobj(file, "invoicemanager-landingzone", file.filename, ExtraArgs={'Tagging': 'paid={}'.format(new_inv.paid)})
                #return 'File uploaded successfully to AWS S3!'
                return render_template_string("""
                                    <html>
                            <head>
                                <title>Redirecting...</title>
                                <script type="text/javascript">
                                    setTimeout(function() {
                                        window.location.href = "/dashboard";
                                    }, 5000); // 5000 milliseconds = 5 seconds
                                </script>
                                <style>
                                    body {
                                        display: flex;
                                        justify-content: center;
                                        align-items: center;
                                        height: 100vh;
                                        margin: 0;
                                    }
                                    .container {
                                        text-align: center;
                                    }
                                </style>
                            </head>
                            <body>
                                <div class="container">
                                    <h2>File uploaded successfully to AWS S3! <BR><BR> You will be redirected in 5 seconds...</h2>
                                </div>
                            </body>
                            </html>
                                """)
            except Exception as e:
                print("An error occurred:", e)
                return 'Upload failed.' + str(e)


        else:
            return 'No file selected. Upload failed.'

@app.route('/reminder', methods=['GET'])
def send_reminder():

    customeremail = request.args.get('email')
    link = request.args.get('link')

    print(link)
    lambda_function_name = 'EmailSender'


    # Extract customer email and invoice link from the request
    customer_email = customeremail
    invoice_link = 'https://invoicemanager-documents.s3.us-east-1.amazonaws.com/'+link

    if not customer_email or not invoice_link:
        return jsonify({'error': 'Missing customer_email or invoice_link'}), 400

    payload = {
        "customer_email": customer_email,
        "invoice_link": invoice_link
    }

    print(payload)
    try:
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType='RequestResponse',  # Use 'RequestResponse' to get the response from Lambda
            Payload=json.dumps(payload)
        )

        response_payload = json.loads(response['Payload'].read())
        return render_template_string("""
                    <html>
            <head>
                <title>Redirecting...</title>
                <script type="text/javascript">
                    setTimeout(function() {
                        window.location.href = "/invoices";
                    }, 5000); // 5000 milliseconds = 5 seconds
                </script>
                <style>
                    body {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container {
                        text-align: center;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Reminder sent successfully. <BR><BR> You will be redirected in 5 seconds...</h2>
                </div>
            </body>
            </html>
                """)
        #return jsonify(response_payload)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


def get_invoice_obj(filename):
    pattern = r'(\d{4})(\d{2})_(\d+)_([A-Za-z]+)\.pdf'

    match = re.match(pattern, filename)

    if match:
        new_inv = Invoice()
        new_inv.year = match.group(1)
        new_inv.month = match.group(2)
        new_inv.customerid = match.group(3)
        new_inv.filename =filename
        return new_inv
    else:
        return False

if __name__ == '__main__':
    app.run(debug=True)
