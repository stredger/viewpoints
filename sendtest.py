
import socket
import difflib

#getpage = 'http://localhost'
getpage = 'http://google.com'
#getpage = 'http://en.wikipedia.org/wiki/Jon_Gooch' # doesnt work currently
#getpage = 'http://www.feedme.uk.com/' # doesnt work currently

#addrs = [('142.104.69.48', 12345)]

addrs = [('190.227.163.141', 12345), ('129.108.202.11',12345)]
socks = []
pages = []


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('142.104.69.48', 35467))
s.listen(1)
conn, addr = s.accept()
socks.append(conn)

for sock in socks:
    #sock = socket.create_connection(addr, timeout=12)

    sock.send(getpage)

    chunk = sock.recv(1024)
    print chunk
    headstoppos = chunk.find('}vpts') + len('}vpts')
    head = chunk[:headstoppos]
    print head
    page = chunk[headstoppos:]
    toread = int(head.split('=')[1].split('}')[0]) - (len(head) - headstoppos)
    print page, toread

    while toread > 0 and len(chunk) > 0:
        chunk = sock.recv(4096)
        page += chunk
        toread -= len(chunk)

    print "that page was", len(page), "bytes"

    pages.append(page)

#diff = difflib.HtmlDiff()
#print diff.make_file(pages[1], pages[2])
print pages[0]
