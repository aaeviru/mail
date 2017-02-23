# -*- coding: utf-8 -*-

import os
import imaplib, smtplib, socket
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

def process_mailbox(M,mail_add,from_add,to_add,maillist):
    """
    Do something with emails messages in the folder.  
    For the sake of this example, print some headers.
    """
    rv, data = M.search(None, '(ON \"' + date.today().strftime("%d-%b-%Y") + '\")','(FROM \"' + mail_add + '\")')
    #rv, data = M.search(None, '(FROM \"' + mail_add + '\")')
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
	if msg['Date'] == None:
		continue
	if (subject,msg['Date']) in maillist:
		continue
	else:
		s = smtplib.SMTP_SSL(setup["smtp_server"])
                s.login(setup["username"],setup["password"] )
		maillist.add((subject,msg['Date']))
        	print 'Message %s: %s' % (num, subject)
	        print 'Raw Date:', msg['Date']
        	print 'From:', msg['From']
		msg.replace_header("Subject",msg["From"]+":"+msg["Subject"])
		msg.replace_header("From",from_add)
		msg.replace_header("To",','.join(to_add))
		s.sendmail(from_add,to_add,msg.as_string())
		s.quit()
            

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
                sys.stdout.flush()
		m = imaplib.IMAP4_SSL(setup["imap_server"])
		rv, data = m.login(setup["username"],setup["password"] )
		rv, data = m.select(mailbox)
    		if rv == 'OK':
			for mail_add in setup["maillist"].split(','):
				mail_add = mail_add.strip('\n')
	        		process_mailbox(m,mail_add,setup["address"],setup[mail_add].split(','),maillist[mail_add])
    		else:
        		print "ERROR: Unable to open mailbox ", rv
		m.close()
		m.logout()

    		time.sleep(60)
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
		for mail_add in setup["maillist"].split(','):
                        fout = open(mail_add,"w")
                        for tmp in maillist[mail_add]:
                                fout.write(tmp[0] + "/" + tmp[1] + "\n")
                        fout.close()
	except imaplib.IMAP4.error as err:
		print err
