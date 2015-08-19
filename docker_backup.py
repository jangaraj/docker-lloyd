#!/usr/bin/python

import sys, os, commands
from docker import Client

def system_command(clicommand, type):
     try:
         status, output = commands.getstatusoutput(clicommand)
     except TypeError:
         error_message = "Problem with command: %s" % (clicommand) 
         print >>sys.stderr, error_message
         send_email(os.environ['EMAIL_TO'], os.environ['EMAIL_FROM'], "PROBLEM: docker backup of " + sys.argv[1], error_message)
         if type == 'output':
             return ""
         else:
             return status
  
     if status == 0:
         if type == 'output':
             return output
         else:
             return status
     else:
         error_message = "Problem with command: %s\nError: %s" % (clicommand, output)
         print >>sys.stderr, error_message
         send_email(os.environ['EMAIL_TO'], os.environ['EMAIL_FROM'], "PROBLEM: docker backup of " + sys.argv[1], error_message)
         if type == 'output':
             return ""
         else:
             return status

def send_email(to, efrom, subject, message):
    if to == "":
       return
    import smtplib
    from email.mime.text import MIMEText
    print "Email: %s - %s" % (subject, message)
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = efrom
    msg['To'] = to
    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(efrom, [efrom], msg.as_string())
        s.quit()
    except:
        print >>sys.stderr, 'ERROR: Problem with sending of email'

sprefix = system_command('date +"' + os.environ['PREFIX'] + '"', 'output')
ssuffix = system_command('date +"' + os.environ['SUFFIX'] + '"', 'output')

c = Client(base_url='unix://docker.sock', version='1.18')
volumes = c.inspect_container(sys.argv[1])['Volumes']
for volume in volumes:
    tar_path = os.environ['BACKUPS'] + sprefix + \
                   sys.argv[1] + '_' + volume.replace('/', '-')[1:] + ssuffix + ".tar.gz"
    tar_command = "tar -zvcf " + tar_path + " " + volumes[volume]

    print "BACKUP: %s" % (sys.argv[1])
    if system_command(tar_command, 'status') != 0:
        continue;

    print "UPLOAD: %s" % (sys.argv[1])

    system_command('s3cmd --access_key="' + os.environ['ACCESS_KEY'] + '" --secret_key="' + os.environ['SECRET_KEY'] + \
          '" -c /dev/null ' + os.environ['S3CMD_OPTS'] + ' put "' + tar_path + '" ' + \
          os.environ['BUCKET'], 'status')
      
    system_command('rm "'+ tar_path + '"', 'status')
