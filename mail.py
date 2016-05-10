# -*- coding: utf-8 -*-

import os
import imaplib, smtplib
import email
from email import header
import quopri
import sys
from datetime import datetime
from datetime import date, timedelta
import time
# メール保存用リスト
maillist = {}
setup = {}
fset = open("setup.txt","r")
for line in fset:
	tmp = line.split(':')
	setup[tmp[0]] = tmp[1].strip('\n')	
fset.close()
mailbox = "INBOX"

def process_mailbox(M,S,mail_add,from_add,to_add,maillist):
    """
    Do something with emails messages in the folder.  
    For the sake of this example, print some headers.
    """

    rv, data = M.search(None, '(ON \"' + date.today().strftime("%d-%b-%Y") + '\")','(FROM \"' + mail_add + '\")')
    if rv != 'OK':
        print "No messages found!"
        return

    for num in data[0].split():
        rv, data = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print "ERROR getting message", num
            return

        msg = email.message_from_string(data[0][1])
        decode = header.decode_header(msg['Subject'])[0]
        subject = decode[0]
	if (subject,msg['Date']) in maillist:
		continue
	else:
		maillist.add((subject,msg['Date']))
        	print 'Message %s: %s' % (num, subject)
	        print 'Raw Date:', msg['Date']
        	print 'From:', msg['From']
		msg.replace_header("From",from_add)
		msg.replace_header("To",','.join(to_add))
		S.sendmail(from_add,to_add,msg.as_string())
            

m = imaplib.IMAP4_SSL(setup["imap_server"])
s = smtplib.SMTP_SSL(setup["smtp_server"])
# IMAP,SMTPにログイン
try:
    rv, data = m.login(setup["username"],setup["password"] )
except imaplib.IMAP4.error:
    print "LOGIN FAILED!!! "
    sys.exit(1)
s.login(setup["username"],setup["password"] )
print rv, data

#rv, mailboxes = m.list()
#if rv == 'OK':
#    print "Mailboxes:"
#    print mailboxes
#メールボックスの選択

for mail_add in setup["maillist"].split(','):
	mail_add = mail_add.strip('\n')
	maillist[mail_add] = set()
	if os.path.isfile(mail_add):
		fin = open(mail_add,"r")
		for line in fin:
			line = line.strip('\n')
			d = datetime.strptime(line.split('/')[1][:16],"%a, %d %b %Y")
			if d.date() == date.today():
				print d
				maillist[mail_add].add(tuple(line.split('/')))
		fin.close()

while True:
	try:

		rv, data = m.select(mailbox)
    		if rv == 'OK':
        		print "Processing mailbox...\n"
			for mail_add in setup["maillist"].split(','):
				mail_add = mail_add.strip('\n')
	        		process_mailbox(m,s,mail_add,setup["address"],setup[mail_add].split(','),maillist[mail_add])
    		else:
        		print "ERROR: Unable to open mailbox ", rv
    		time.sleep(5)
	except KeyboardInterrupt:
		print "exit"
		for mail_add in setup["maillist"].split(','):
			fout = open(mail_add,"w")
			for tmp in maillist[mail_add]:
				fout.write(tmp[0] + "/" + tmp[1] + "\n")
			fout.close()
		break
	except socket.error as msg:
		print msg
		m.login(setup["username"],setup["password"] )
		s.login(setup["username"],setup["password"] )
m.close()
m.logout()
s.close()
