
import sys
import socket
import difflib
import select
import os
import threading
import getloc

# this aint workin!
#
# cwd = os.getcwd()
# repypath = os.path.join(cwd, "repylib")
# try:
#     path = os.environ['PYTHONPATH']
#     os.environ['PYTHONPATH'] = "%s:%s" % (repypath, path)
# except KeyError:
#     os.environ['PYTHONPATH'] = repypath

import overlord

# constants
MAX_LISTEN_QUEUE = 10
READ_SIZE = 4096

VPT_LHEADER = 'vpts{'
VPT_RHEADER = '}vpts'
VPT_FIELDSEP = '='


# globals
threadlist = []
threadlist_lock = threading.Lock()

connlist = []
connlist_lock = threading.Lock()

vptlist = []
vptlist_lock = threading.Lock()

# dict of location: viewpoint[]
locations = {}
locations_lock = threading.Lock()



class ViewpointException(Exception):
    """ """
    None



class viewpoint():

    def __init__(self, url, ip, location, page):
        self.url = url
        self.page = page
        self.ip = ip
        self.location = location

    def compute_diff(self, other_vpt):
        None



class connection():
    
    def __init__(self, ip, port, socket=None):

        assert len(ip.split('.')) == 4, "Invalid ip addr"
        assert port > 0, "Invalid port"

        self.socket = socket
        self.ip = ip
        self.port = port


    def __del__(self):
        self.socket.close()

    def is_connected(self):
        return True if self.socket is not None else False



def _sendmsg(sockobj, msg):
    """ """
    tosend = len(msg)
    totbytes = 0
    while len(msg) > 0:
       bytessent = sockobj.send(msg)
       msg = msg[bytessent:]   
       totbytes += bytessent

    assert totbytes == tosend


def _sendheader(sockobj, length):
    """ """
    msg = VPT_LHEADER+"length="+str(length)+VPT_RHEADER
    _sendmsg(sockobj, msg)



def sendmsg(sockobj, msg):
    """ """
    _sendheader(sockobj, len(msg))
    _sendmsg(sockobj, msg)
   


def readheader(sock):

    chunk = sock.recv(READ_SIZE)
    head = chunk
    # loop until we have the left and right portions of the header
    while VPT_RHEADER not in head and VPT_LHEADER not in head and len(chunk) > 0:
        chunk = sock.recv(READ_SIZE)
        head += chunk

    return head



def recvmsg(sock):

    assert isinstance(sock, socket.socket)

    chunk = readheader(sock)
    headstoppos = chunk.find(VPT_RHEADER) + len(VPT_RHEADER)
    if headstoppos <= len(VPT_RHEADER):
        raise ViewpointException("Failed to get header for message")

    head = chunk[:headstoppos]
    msg = chunk[headstoppos:]

    # we want to isolate the value immediately after VPT_FIELDSEP
    #  and immediately before VPT_RHEADER
    try:
        msglen = int(head.split(VPT_FIELDSEP)[1].split(VPT_RHEADER)[0])
    except ValueError as e:
        raise ViewpointException("Failed to read header for message: %s" % (e))

    toread = msglen - (len(chunk) - headstoppos)
    while toread > 0 and len(chunk) > 0:
        chunk = sock.recv(READ_SIZE)
        msg += chunk
        toread -= len(chunk)

    assert len(msg) == msglen

    return msg



def get_viewpoint(connection, url):
    """ Threads start execution here """

    try:
        sendmsg(connection.socket, url)
        print "sent url %s to %s" % (url, connection.ip)

        page = recvmsg(connection.socket)
        print "recieved %s byte page from %s" % (len(page), connection.ip)

        # get location
        location = getloc.stringify_location(getloc.get_location(connection.ip))

        vpt = viewpoint(url, connection.ip, location, page)

        vptlist_lock.acquire()
        vptlist.append(vpt)
        vptlist_lock.release()

        print "got viewpoint for %s from %s" % (vpt.url, vpt.ip)

    except ViewpointException as e:
        print "%s: Failed to get viewpoint for %s from %s" % (e, url, connection.ip)



def setup_listener(ip, port, max_queue):
    """ """
    
    assert len(ip.split('.')) == 4, "Invalid ip addr"
    assert port > 0, "Invalid port"

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    s.listen(max_queue)
    print "Listening on port %s:%s" % (ip, str(port)) 

    assert(s)
    return s



def readall(fd):
    """ Will read all available data from the fd, we use os.read
    so we don't block when less than READ_SIZE bytes are available 
    """

    assert fd.fileno() >= 0, "Invalid file descriptor"

    fdnum = fd.fileno()
    chunk = os.read(fdnum, READ_SIZE)
    data = chunk
    while len(chunk) == READ_SIZE: 
        chunk = os.read(fdnum, READ_SIZE)
        data += chunk

    return data



def readbytes(fd, toread):
    """ Will block until toread bytes have been read! """

    assert fd.fileno() >= 0, "invalid file descriptor"
    assert toread > 0, "Invalid num of bytes to read"
    
    fdnum = fd.fileno()
    data = ""
    chunk = " " # junk so we can treat below as a do while
    while toread > 0 and len(chunk) > 0:
        rd = READ_SIZE if READ_SIZE < toread else toread
        chunk = os.read(fdnum, rd)
        data += chunk
        toread -= len(chunk)

    return data



def establish_connection(localsock):
    """ """
    assert localsock

    socket, addrinfo = localsock.accept()
    conn = connection(addrinfo[0], addrinfo[1], socket)

    connlist_lock.acquire()
    connlist.append(conn)
    connlist_lock.release()

    print "connection to %s established" % (conn.ip)

    return conn



def create_connthread(connection, url):

    assert connection and url

    newthread = threading.Thread(target=get_viewpoint, args=[connection, url])

    threadlist_lock.acquire()
    threadlist.append(newthread)
    threadlist_lock.release()

    print "created %s to get %s from %s" % (newthread.name, url, connection.ip)

    return newthread



def join_all_threads():

    for thread in threadlist:
        thread.join() 
        threadlist_lock.acquire()
        threadlist.remove(thread)
        threadlist_lock.release()


def wait_for_conn(lsock, url):
    
    assert lsock > 0, "Invalid listening socket"

    print "Waiting for incoming connections...\nq to exit"
    fin = 0
    while not fin:
        fdset = select.select([lsock, sys.stdin], [], [])[0]
        for fd in fdset:
            if fd == sys.stdin:
                userstr = readall(fd)
                if 'q\n' in userstr:
                    fin = 1
            elif fd == lsock:
                conn = establish_connection(lsock)
                newthread = create_connthread(conn, url)
                newthread.start()


def usage():
    print "Usage: <ip> <port> <url>"



def close_all_connections():
    """ """
    for conn in connlist:
        connlist_lock.acquire()
        connlist.remove(conn)
        conn.socket.close()
        connlist_lock.release()
    


def run_repy_clients(geniuser, ip, port):
    
    # get vesels
    print "Acquiring repy vessels..."
    repyvessels = overlord.Overlord(geniuser, 10, "wan", "out.repy", "repyvessel.log")
    print "Complete"

    # run on vessels
    repyvessels.run(ip, port)



def main():

    if len(sys.argv) < 4:
        #usage()
        #return 1
        print "For testing yall!!!!!!!"
        sys.argv.append("stredger")
        sys.argv.append("142.104.69.48")
        sys.argv.append(35467)
        sys.argv.append("http://google.com")

    geniuser = sys.argv[1]
    thisip = sys.argv[2]
    thisport = sys.argv[3]
    urltoview = sys.argv[4]

    repythread = threading.Thread(target=run_repy_clients, args=[geniuser, thisip, thisport])
    repythread.start()

    sock = setup_listener(thisip, thisport, MAX_LISTEN_QUEUE)
    listenthread = threading.Thread(target=wait_for_conn, args=[sock, urltoview])
    #wait_for_conn(sock, urltoview)

    

    sock.close()
    join_all_threads()
    close_all_connections()
    # TODO: terminate repy thread!!
    
    for vpt in vptlist:
        print "view from %s at %s" % (str(vpt.location), vpt.ip)
        print vpt.page


if __name__ == "__main__":

    sys.exit(main())
