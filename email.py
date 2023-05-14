import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_join_request_email(group_url):
    # set up the SMTP server
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # or 465 if using SSL/TLS
    smtp_username = "kris42581@gmail.com"
    smtp_password = "fjfbeaflbcwmamja"
    smtp_conn = smtplib.SMTP(smtp_server, smtp_port)
    smtp_conn.starttls()
    smtp_conn.login(smtp_username, smtp_password)

    # create the email message
    sender_email = " no-reply.savagesales@gmail.com"
    receiver_email = "shadman16203063@gmail.com"
    subject = "Private Facebook Group Join Request"
    body = f'''\
Hi Admin,

A new user has requested to join the private Facebook group and needs to answer the group questions. Please check the following group URL:
{group_url}

Thanks,
Savage Sales
'''.format(group_url)
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    message.add_header('reply-to', 'no-reply@kris42581.com')


    # send the email
    try:
        smtp_conn.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)

    # close the SMTP connection
    smtp_conn.quit()

send_join_request_email("")