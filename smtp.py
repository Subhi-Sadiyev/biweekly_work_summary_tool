### for confuguring email server
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, body, to_email, cc_email, from_email, password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Cc'] = cc_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Include both 'To' and 'Cc' recipients in the list
    recipients = [to_email] + [cc_email]

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(from_email, password)
        server.sendmail(from_email, recipients, msg.as_string())
        server.close()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")