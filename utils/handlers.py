# coding: utf-8

from logging.handlers import SMTPHandler


class SMTPHandlerUnicode(SMTPHandler):

    def emit(self, record):
        try:
            import smtplib
            from email.utils import formatdate

            from email.mime.text import MIMEText

            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)

            msg = self.format(record)

            message = MIMEText(msg, _charset="utf-8")

            message.add_header("Subject", self.getSubject(record))
            message.add_header("From", self.fromaddr)
            message.add_header("To", ",".join(self.toaddrs))
            message.add_header("Date", formatdate())

            if self.username:
                if self.secure is not None:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()
                smtp.login(self.username, self.password)

            smtp.sendmail(self.fromaddr, self.toaddrs, message.as_string())

            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)