from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import boto3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'


class Inv:
    year = '0000'
    month = '00'
    filename = ''
    customerid=''
    key = ''


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
        return render_template('dashboard.html', user=user)

    return redirect('/login')


@app.route('/invoices')
def invoices():
    bucket_name = 'invoicemanager-documents'

    bucket_name = 'invoicemanager-documents'

    AWS_REGION = 'us-east-1'
    AWS_ACCESS_KEY_ID = '[CENSORED]'
    AWS_SECRET_ACCESS_KEY = '[CENSORED]'

    # Create an S3 client
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_REGION)

    # List objects in the bucket
    response = s3.list_objects_v2(Bucket=bucket_name)
    inv_list = []

    # Check if there are any objects in the bucket
    if 'Contents' in response:
        print("Files in bucket '{}' :".format(bucket_name))
        for obj in response['Contents']:
            print(obj['Key'])
            split_key = obj['Key'].split("_")
            year = split_key[0][0:4]
            month = split_key[0][5:7]
            customerid =split_key[1]
            filename =split_key[2]
            new_inv = Inv()
            new_inv.year =year
            new_inv.month =month
            new_inv.customerid =customerid
            new_inv.filename =filename
            new_inv.key =obj['Key']

            inv_list.append(new_inv)
    else:
        print("No files found in bucket '{}'.".format(bucket_name))

    return render_template('invoices.html', inv_list=inv_list)

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
