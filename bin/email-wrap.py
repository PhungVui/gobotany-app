#!/usr/bin/env python
#
# To run a script on Heroku such that our admins get emailed its output
# (this is useful for daily automated scripts, for example) first add
# the SendGrid Heroku add-on to your application:
#
#      heroku addons:add sendgrid:starter
#
# Then set the environment variable $MAIL_TO:
#
#      heroku config:set MAIL_TO=sid@newfs.org,bill@newfs.org
#
# Finally, put the name of this script at the front of any command line:
#
#     bin/email-wrap.py bin/nightly.sh (or whatever)
#
# The result is that the command's output, both stdout and stderr, will
# be collected and then emailed to your list of email addresses.

import os
import smtplib
import subprocess
import sys
import time

if __name__ == '__main__':
    mail_to = os.environ.get('MAIL_TO', None)
    username = os.environ.get('SENDGRID_USERNAME', None)
    password = os.environ.get('SENDGRID_PASSWORD', None)
    app_name = os.environ.get('HEROKU_APPNAME', None)

    if mail_to is None or not mail_to.strip():
        print >>sys.stderr, 'Error: set MAIL_TO before calling email-wrap.py'
        exit(1)

    if not username or not password:
        print >>sys.stderr, 'Error: need "heroku addons:add sendgrid:starter"'
        exit(1)

    if app_name is None:
        print >>sys.stderr, 'Error: set HEROKU_APPNAME before calling email-wrap.py'
        exit(1)

    if len(sys.argv) > 1: 
        script_name = sys.argv[1]
    else:
        script_name = "nothing"

    current_time = time.strftime("%H:%M", time.gmtime())

    template = '[{server}] log output: {script} ran on {time} GMT'
    subject = template.format(server=app_name, script=script_name, time=current_time)

    p = subprocess.Popen(
        sys.argv[1:],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        )
    (output, ignored) = p.communicate()

    fromaddr = 'no-reply@newenglandwild.org'
    toaddrs = mail_to.replace(',', ' ').split()
    message = '\r\n'.join((
            'To: {}'.format(', '.join(toaddrs)),
            'From: {}'.format(fromaddr),
            'Subject: {}'.format(subject),
            '',
            output.replace('\n', '\r\n')))

    server = smtplib.SMTP('smtp.sendgrid.net', 587, 'heroku.com')
    # server.set_debuglevel(1)
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, message)
    server.quit()
