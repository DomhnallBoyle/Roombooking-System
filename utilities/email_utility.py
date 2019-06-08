from flask_mail import Message
from app import mail, app


class EmailUtility(object):

    def __init__(self):
        self.sender = app.config.get('MAIL_USERNAME')

    def send_email(self, subject, message, recipients):
        with app.app_context():
            for recipient in recipients:
                html = 'Hi {},<br><br>{}<br><br>Room Booking System'.format(recipient.split('@')[0], message)
                msg = Message(subject, sender=self.sender, recipients=[recipient])
                msg.html = html
                mail.send(msg)
