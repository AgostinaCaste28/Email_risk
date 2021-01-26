import time
from itertools import chain
import email
from email.header import decode_header
import imaplib

imap_ssl_host = 'imap.gmail.com'  # imap.mail.yahoo.com
imap_ssl_port = 993

username = 'casomlac@gmail.com'
password = 'Prueba321*'

# Restrict mail search. Be very specific.
# Machine should be very selective to receive messages.
criteria = {
    'Body':    'risk',
   
}
uid_max = 0


def search_string(uid_max, criteria):
    c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items())) + [('UID', '%d:*' % (uid_max+1))]
    return '(%s)' % ' '.join(chain(*c))
    # Produce search string in IMAP format:
    #   e.g. (FROM "me@gmail.com" SUBJECT "abcde" BODY "123456789" UID 9999:*)


def get_first_text_block(msg):
    type = msg.get_content_maintype()

    if type == 'multipart':
        for part in msg.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif type == 'text':
        return msg.get_payload()


# server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
# server.login(username, password)
# server.select('INBOX')

# result, data = server.uid('search', None, search_string(uid_max, criteria))

# uids = [int(s) for s in data[0].split()]
# if uids:
#     uid_max = max(uids)
    # Initialize `uid_max`. Any UID less than or equal to `uid_max` will be ignored subsequently.

# server.logout()

# Connect to the database
import pymysql
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Prueba321***',
                             database='emails',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()

# Keep checking messages ...
# I don't like using IDLE because Yahoo does not support it.
while 1:
    # Have to login/logout each time because that's the only way to get fresh results.

    server = imaplib.IMAP4_SSL(imap_ssl_host, imap_ssl_port)
    server.login(username, password)
    server.select('INBOX')

    result, data = server.uid('search', None, search_string(uid_max, criteria))

    uids = [int(s) for s in data[0].split()]
    for uid in uids:
        # Have to check again because Gmail sometimes does not obey UID criterion.
        if uid > uid_max:
            result, data = server.uid('fetch', str(uid), '(RFC822)')  # fetch entire message
            msg = email.message_from_bytes(data[0][1])

            asunto = decode_header(msg["Subject"])[0][0]
            fecha = decode_header(msg["date"])[0][0]
            if isinstance(asunto, bytes):
                # if it's a bytes, decode to str
                asunto = asunto.decode()
            # email sender
            #print(msg.get("Seen"))
            remitente = msg.get("From")
            
            
            uid_max = uid

            text = get_first_text_block(msg)
            # print ('New message :::::::::::::::::::::')
            # print (text)
            
            # Create a new record
            str_sql = "INSERT INTO mails_risk (fecha, remitente, asunto ) VALUES ('" +fecha +"','" + remitente + "', '"+ asunto + "')"
            cursor.execute(str_sql)
            connection.commit()
                

server.logout()
time.sleep(1)