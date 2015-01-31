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
import urlparse
import mimetypes

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPHeader(object):
    def __init__(self, path, host, method="GET", message=""):

        self.request = "%s %s HTTP/1.1\r\n" %(method, path)
        self.request += "Host: %s\r\n" %host
        self.request += "User-Agent: Python\r\n"
        self.request += "Accept: */*\r\n"

        if method == "GET":
            self.request += "Content-type: %s\r\n" %(mimetypes.guess_type(path)[0]) # Test THIS TODO
        else:
            self.request += "Content-type: application/x-www-form-urlencoded\r\n"

        self.request += "Connection: close\r\n"
        self.request += "Content-Length: %s\r\n\r\n" %len(message)
        self.request += message

    def get_header(self):
        return self.request.encode('utf-8')

class HTTPClient(object):

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

        result = ''

        while not result:
            readable, writable, exceptions = select.select(sockin, sockout, sockexc)

            for s in readable:
                sockin.pop()
                result = self.recvall(s)
                sock.close()

            for s in writable:
                s.sendall(request)
                sockin.append(sockout.pop())

            for s in exceptions:
                print 'Exception'
                sys.exit()

        return result

    # read everything from the socket
    # TODO add a timeout if the connection doesn't close
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(4096)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        code = 500
        body = ""
        parsed = urlparse.urlsplit(url)
        # sock = self.connect(parse.get('path', '/'), 80)
        # self.poll_sockets(sock, 'GET / HTTP/1.1\r\n\r\n')
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        # Encoded message to send in POST
        encoded = urllib.urlencode(args) if args else ''

        parsed =  urlparse.urlsplit(url)
        header = HTTPHeader(parsed.path, parsed.hostname, "POST", encoded)
        request = header.get_header()

        port = parsed.port if parsed.port else 80
        sock = self.connect(parsed.hostname, port)

        result = self.poll_sockets(sock, request)
        code, body = self.parse_result(result)

        return HTTPRequest(code, body)

    def parse_result(self, result):
        """
        Takes an HTTP/1.1 response and returns a status code and message body
        """
        try:
            head, body = re.split(r'\r\n\r\n', result, 1)
            code = head.split()[1]
        except:
            code = 500
            body = ''
        return code, body

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    # for testing right now
    request = client.POST(sys.argv[2], {'a':'foo', 'b':'bar'})
    print request.code
    print request.body
    # if (len(sys.argv) <= 1):
    #     help()
    #     sys.exit(1)
    # elif (len(sys.argv) == 3):
    #     print client.command( sys.argv[1], sys.argv[2] ) # still not convnced
    #     print '2'
    # else:
    #     print client.command( command, sys.argv[1] ) # Still not convinced
    #     print '3'
