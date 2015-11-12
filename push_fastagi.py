#!/usr/bin/env python
# $Id: push_fastagi.py,v 1.22 2015/11/12 18:44:41 fabio Exp $

import os, sys, string, yaml, getopt, httplib2
import SocketServer, socket
from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler

conf = {}

def daemonize():
    global conf
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit first parent
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1)
        
    os.setsid()

    # do second fork
    try: 
        pid = os.fork() 
        if pid > 0:
            # exit from second parent, print eventual PID before
            file(conf['pidfile'],'w+').write("%s\n" % pid)
            sys.exit(0) 
    except OSError, e: 
        print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
        sys.exit(1) 
        
    print "Exiting Main Thread. pid: %d" % os.getpid()
    os.umask(022)
    [os.close(i) for i in xrange(3)]
    os.open(os.devnull, os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)

class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SocketServer.TCPServer.server_bind(self)

class AGIClientHandler(StreamRequestHandler):
    def __init__(self, *args, **kwargs):
        self.env = {}
        StreamRequestHandler.__init__(self, *args, **kwargs)

    def handle(self):
        global conf
        while 1:
            line = self.rfile.readline().strip()
            if line == '':
                break
            key,data = line.split(':')[0], ':'.join(line.split(':')[1:])
            key = key.strip()
            data = data.strip()
            if key <> '':
                if not conf['fork']:
                    print "'%s' : '%s'" % (key,data)
                else:
                    pass
                self.env[key] = data

        agi_extension = '%s%s' % (conf['prefix'],self.env['agi_dnid'])
        host = os.uname()[1]
        callerId = self.env['agi_callerid']
        userEmail = self.env['agi_arg_1']
        tm = self.env['agi_uniqueid']
        if userEmail is not None and host is not None and callerId is not None and tm is not None:
            headers = {
                'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
                'Content-type': 'application/json'
            }
            data = '{"submit": 1, "push": {"userEmail": "%s", "host": "%s", "receiver": "%s", "cid": "%s", "timestamp": "%s"}}' % (userEmail,host,agi_extension,callerId,tm)
            http = httplib2.Http(ca_certs=conf['certfile'], disable_ssl_certificate_validation=conf['disable_certificate'])
            try:
                response, content = http.request(conf['url'], 'POST', body=data, headers=headers)
            except socket.error, e:
                msg = "Problem connecting to webservice: %s" % e
                raise RuntimeError(msg)

if __name__ == '__main__':
    conffile = '%s/settings.yaml' % os.path.dirname(os.path.abspath(__file__)) 
    if not os.path.isfile(conffile):
        msg = "%s doesn't exist." % conffile
        raise RuntimeError(msg)

    conf = yaml.load(file(conffile, 'r'))
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f")
    except getopt.GetoptError, err:
        print str(err)

    for opt, arg in opts:
        if opt == "-f":
            conf['fork'] = False

    if conf['fork']:
        daemonize()

    ThreadingTCPServer.allow_reuse_address = True
    ThreadingTCPServer.address_family = socket.AF_INET
    server = ThreadingTCPServer((conf['listen'], conf['port']), AGIClientHandler)
    server.serve_forever()
