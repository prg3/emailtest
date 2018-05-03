#!/usr/bin/env python

import configparser
import time
import smtplib
import poplib
import random
from email.mime.text import MIMEText

import pprint

pp = pprint.PrettyPrinter(indent=4)

config=configparser.ConfigParser()
config.read('config.ini')
randomnum = random.randint(1,10000000)
canarystring = "This is a canary test - %s"%(randomnum)

def sendEmail():
    msg = MIMEText(canarystring)
    msg['Subject'] = "Canary Test"
    msg['From'] = config['DEFAULT']['emailfrom']
    msg['To'] = config['DEFAULT']['emailto']

    try:
        s = smtplib.SMTP(config['DEFAULT']['smtpserver'])
        s.sendmail(config['DEFAULT']['emailfrom'], [ config['DEFAULT']['emailto'] ], msg.as_string())
        s.quit()
    except:
        s.set_debuglevel(1000)
        s.sendmail(config['DEFAULT']['emailfrom'], [ config['DEFAULT']['emailto'] ], msg.as_string())
        s.quit()

def checkEmail():
    pop = poplib.POP3_SSL(config['DEFAULT']['popserver'])
    # pop.set_debuglevel(1000)
    pop.user(config['DEFAULT']['popaccount'])
    pop.pass_(config['DEFAULT']['poppassword'])
    numMessages = len(pop.list()[1])
    for i in range(numMessages):
        msg = pop.retr(i+1)
        header=1
        for line in msg[1]:
            if line == '':
                header=0
                continue
            if header == 0:
                contentline = line
                break
        try:
            pop.dele(i+1)
        except:
            print "Error deleting"
        pop.quit()

    if (contentline == canarystring):
        return 0
    return 1


sendEmail()
time.sleep(config['DEFAULT']['maildelay'])

if ( not checkEmail() ):
    print "Success"
else:
    print "Failure"
