
import os

from threading import Thread
from flask_mail import Message
from app import app
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body, attachlist=[], bcc=None):   
    msg = Message(subject, sender=sender, recipients=recipients, bcc=bcc)
    msg.body = text_body
    msg.html = html_body

    if attachlist:
        for filepath in attachlist:
            with app.open_resource(filepath, "rb") as f:
                fname = os.path.basename(filepath)
                msg.attach("filepath", "application/octet-stream", f.read(), 'attachment; filename="{0}"'.format(fname))
    Thread(target=send_async_email, args=(app, msg)).start()
