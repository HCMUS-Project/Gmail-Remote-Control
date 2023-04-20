import os
from gmail_api import *

from flask import Flask, render_template, redirect, url_for, request
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap


load_dotenv()  # take environment variables from .env.

SECRET_KEY = os.getenv("SECRET_KEY")
PORT = os.getenv("PORT")
SERVER_EMAIL = os.getenv("SERVER_EMAIL")

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

Bootstrap(app)

# init gmail api
gmail_credential = None
gmail_service = None
thread_id = None
client_profile = None


def authorize():
    return os.path.exists('token.json')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""

    if request.method == "POST":
        global client_profile, gmail_credential, gmail_service

        gmail_credential = create_gmail_credential()
        gmail_service = build_gmail_service(gmail_credential)

        isSuccess, client_profile = check_authentication_success(gmail_service)

        if isSuccess:
            print("AUTHENTICATION: Success")
            print("CLIENT PROFILE:", client_profile)

            return redirect(url_for('control'))
        else:
            print("AUTHENTICATION: Fail")
            error = "Authentication failed"

    return render_template('login.html', error=error)


@app.route('/disconnect', methods=['GET', 'POST'])
def disconnect():
    try:
        logout(gmail_service)
    except:
        pass

    return redirect(url_for('login'))


@app.route('/control', methods=['GET', 'POST'])
def control():
    # authorize user
    if not authorize():
        return redirect(url_for('login'))

    return render_template('control.html', client_email=client_profile['emailAddress'], server_email=SERVER_EMAIL)


@app.route('/review', methods=['GET', 'POST'])
def review():
    if not authorize():
        return redirect(url_for('login'))

    sender, date, body = None, None, None

    if request.method == "GET":
        # authorize user
        authorize()
        sender, date, body = BindIncomingEmails(gmail_service, thread_id)

    return render_template('review.html', client_email=client_profile["emailAddress"], server_email=SERVER_EMAIL, date=date, body=body)


@app.route('/send-request', methods=['GET', 'POST'])
def send_request():
    # authorize user
    if not authorize():
        return redirect(url_for('login'))

    if request.method == "POST":
        global thread_id

        data = request.get_json()

        print("data:", data)

        # email content
        to = SERVER_EMAIL
        subject = 'Control Request'
        message_text = data["content"].replace("<br/>", "\n")

        print("message_txt:", message_text)
        # create and send email
        message = create_gmail_message(to, subject, message_text)
        print("message:", message)

        message, thread_id = gmail_send_message(gmail_service, message)
        print("thread_id:", thread_id)

    return redirect(url_for('review'))


@app.route('/another-request', methods=['GET', 'POST'])
def new_request():
    # authorize user
    if not authorize():
        return redirect(url_for('login'))

    return redirect(url_for('control'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, threaded=True, debug=True)
