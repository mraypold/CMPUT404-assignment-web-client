#!/usr/bin/env python
# coding: utf-8
# Copyright 2013-2015 Abram Hindle, Michael Raypold
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import select
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

VERBOSE = True

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        sock = self.init_socket()
        try:
            sock.connect((host, port))
        except socket.error as msg:
            print 'Connection failed'
            print 'Error code: %s, message: %s' %(str(msg[0]), msg[1])
            sys.exit()
        else:
            print 'Connected to %s' %host
        return sock

    def init_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print 'Failed to create socket'
            print 'Error code: %s, message: %s' %(str(msg[0]), msg[1])
            sys.exit()
        else:
            print 'Socket created'
        return sock

    def poll_sockets(self, sock, request):
        '''Sends the request on the specified socket and polls for response'''

        sockin = []
        sockout = [sock]
        sockexc = []

        while True:
            readable, writable, exceptions = select.select(sockin, sockout, sockexc)

            for s in readable:
                if VERBOSE: print 'Have readable socket'
                sockin.pop()
                print(self.recvall(s))
                # print s.recv(4096)
                print('wtf is happening')
                sys.exit()

            for s in writable:
                if VERBOSE: print 'Have writable socket'
                s.sendall(request)
                sockin.append(sockout.pop())

            for s in exceptions:
                if VERBOSE: print 'Have exception'
                sys.exit()

        return None

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(4096)
            if (part):
                buffer.extend(part)
            else:
                done = not part
            print str(buffer)
        return str(buffer)

    def GET(self, url, args=None):
        if VERBOSE: print 'GETing %s' %url
        code = 500
        body = ""
        sock = self.connect(url, 80)
        self.poll_sockets(sock, 'GET / HTTP/1.1\r\n\r\n')
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        if VERBOSE: print 'POSTing %s' %url
        code = 500
        body = ""
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[2], command )
