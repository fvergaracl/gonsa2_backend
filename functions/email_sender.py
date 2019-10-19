#!/usr/bin/env python
# -*- coding: utf-8 -*-
import smtplib
import os.path
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from settings.config import Config, emailconfig

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

def type_of_emails(request_type):
	email_content = ''
	n_parameters_need = -1
	if request_type == 'new_account':
		# 5 parameters
		# Platform name, Platform name, Url to login, User, Password
		n_parameters_need = 5
		found = True
		with open(os.path.join(root_dir(), 'emails/new_account.html')) as file:
			email_content = file.read().replace('\n', '')
	elif request_type == 'pass_changed':
		# 6 parameters
		# Platform name,  name , username, ip, datetime, email contact
		n_parameters_need = 6
		found = True
		with open(os.path.join(root_dir(), 'emails/pass_changed.html')) as file:
			email_content = file.read().replace('\n', '')
	elif request_type == 'password_recovery':
		# 5 parameters
		# Platform name, username, url+token, ip, datetime
		n_parameters_need = 5
		found = True
		with open(os.path.join(root_dir(), 'emails/password_recovery.html')) as file:
			email_content = file.read().replace('\n', '')
	else:
		found = False
	return email_content, found, n_parameters_need




def email_to_send(parameters_, type_email, Subject, destine_email):
    try:
    	email_conf = emailconfig()
    	config = Config()
        strFrom = email_conf.get_user()
        strTo = destine_email

        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = Subject + ' - ' + config.get_platform_name()
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        msgText = MIMEText('This is the alternative plain text message.')
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it below
        email_content, found, n_parameters = type_of_emails(type_email)
        print len(parameters_)
        if not found:
        	return [False, 'Type of email not found']
        if len(parameters_) != n_parameters:
        	return [False, 'The number of parameters entered are not valid']
        final_email = email_content.format(*parameters_)
        msgText = MIMEText(final_email, 'html')
        msgAlternative.attach(msgText)

        # This example assumes the image is in the current directory
        fp = file(os.path.join(root_dir(), 'emails/logo.png'), 'rb')
        msgImage = MIMEImage(fp.read(), _subtype="png")

        fp.close()

        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)

        # Send the email (this example assumes SMTP authentication is required)
        smtp = smtplib.SMTP_SSL(email_conf.get_url(), email_conf.get_port())
        smtp.ehlo()
        smtp.login(strFrom, email_conf.get_pass())
        smtp.sendmail(strFrom, strTo, msgRoot.as_string())

        smtp.quit()
        print 
        return [True, 'enviado******']
    except Exception as e:
    	print e
    	return [False, 'NOOO ENVIADO']
