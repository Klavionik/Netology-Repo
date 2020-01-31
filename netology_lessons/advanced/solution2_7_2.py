"""
LESSON 2.7, EX. 3
"""

import email
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_SMTP = "smtp.gmail.com"
GMAIL_IMAP = "imap.gmail.com"


class NEmail:

    def __init__(self, smtp_server, imap_server, login, password):
        self.smtp = smtp_server
        self.imap = imap_server
        self.login = login
        self.password = password

    def _build_message(self, subj, recipients, message):
        msg = MIMEMultipart()
        msg['From'] = self.login
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subj
        msg.attach(MIMEText(message))
        return msg

    # send message
    def send(self, subject, recipients, message):
        msg = self._build_message(subject, recipients, message)

        with smtplib.SMTP(GMAIL_SMTP, 587) as smtp:
            # identify ourselves to smtp gmail client
            smtp.ehlo()
            # secure our email with tls encryption
            smtp.starttls()
            # re-identify ourselves as an encrypted connection
            smtp.ehlo()

            smtp.login(self.login, self.password)
            smtp.sendmail(self.login, to_addrs=recipients, msg=msg.as_string())
        # send end

        print('Message sent!')

    def receive(self, header=None, folder='inbox'):
        criterion = '(HEADER Subject "%s")' % header if header else 'ALL'

        with imaplib.IMAP4_SSL(GMAIL_IMAP) as imap:
            imap.login(self.login, self.password)
            imap.list()
            imap.select(folder)
            result, data = imap.uid('search', None, criterion)
            assert data[0], 'There are no letters with current header'
            latest_email_uid = data[0].split()[-1]
            result, data = imap.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)

        return email_message


if __name__ == '__main__':
    email_manager = NEmail(GMAIL_SMTP, GMAIL_IMAP, 'klavionik@gmail.com', '2ZoK64mbMF9w')
    email_manager.send('Subject', ['jediroman@rambler.ru'], 'Message')
    print(email_manager.receive())
