from flask_mail import Mail, Message
from flask import Flask

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '861191839@qq.com'
app.config['MAIL_PASSWORD'] = 'fiewwphllkspbehj'
app.config['MAIL_DEFAULT_SENDER'] = '861191839@qq.com'

mail = Mail(app)


with app.app_context():
    msg = Message("Test", recipients=["1017760136@qq.com"])
    msg.body = "This is a test email."
    mail.connect()


    try:
        mail.send(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
