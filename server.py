#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        request = self.data.decode("utf-8").split(" ")
        if self.checkErrors(request):
            return
        if self.checkSecurity(request):
            return
        data = self.getData(request)
        response = self.getResponse(request, data)
        self.sendResponse(response)


    def checkErrors(self, request):
        # 301 correct path not ending with /
        if os.path.isdir("www" + request[1]) and not request[1].endswith("/"):
            response = "HTTP/1.1 301 Moved Permanently\n" + "Location: " + request[1] + "/\n"
            self.request.sendall(bytearray(response, "utf-8"))
            return True

        # 405 method not allowed
        if request[0] != "GET":
            response = "HTTP/1.1 405 Method Not Allowed\n" + "Content-Type: text/html\n\n" + "405 Method Not Allowed"
            self.request.sendall(bytearray(response, "utf-8"))
            return True
            
        # 404 not found
        if not os.path.exists("www" + request[1]):
            response = "HTTP/1.1 404 Not Found\n" + "Content-Type: text/html\n\n" + "404 Not Found"
            self.request.sendall(bytearray(response, "utf-8"))
            return True

        # if no errors return False 
        return False
    
    def checkSecurity(self, request):
        # security check
        if ".." in request[1]:
            response = "HTTP/1.1 404 Not Found\n" + "Content-Type: text/html\n\n" + "404 Not Found"
            self.request.sendall(bytearray(response, "utf-8"))
            return True
        return False

    def getData(self, request):
        # get data from file
        if request[1].endswith("/"):
            request[1] = request[1] + "index.html"
        f = open("www" + request[1], "r")
        data = f.read()
        f.close()
        return data

    def getResponse(self, request, data):
        # create response 
        if request[1].endswith(".css"):
            content_type = "text/css"
        else:
            content_type = "text/html"
        return "HTTP/1.1 200 OK\n" + "Content-Type: " + content_type + "\n\n" + data

    def sendResponse(self, response):
        # send response
        self.request.sendall(bytearray(response, "utf-8"))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
