'''
Created on 20 Jan 2017

https://www.huyng.com/posts/modifying-python-simplehttpserver

@author: achamara
'''

from SimpleHTTPServer import SimpleHTTPRequestHandler

import posixpath
import os
import urllib


class RequestHandler(SimpleHTTPRequestHandler):
    
    # modify this to add additional routes
    ROUTES = ()
    
    @staticmethod
    def changeRootFolder(customPath):
        RequestHandler.ROUTES = customPath 
        
    def translate_path(self, path):
        """translate path given routes"""

        for pattern, rootdir in self.ROUTES:
            print (pattern , rootdir)
        # set default root to cwd
        root = os.getcwd()
        
        # look up routes and set root directory accordingly
        for pattern, rootdir in self.ROUTES:
            if path.startswith(pattern):
                # found match!
                path = path[len(pattern):]  # consume path up to pattern len
                root = rootdir
                break
        
        # normalize path and prepend root directory
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        
        path = root
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)

        return path

# if __name__ == '__main__':
 #   httpd = SocketServer.TCPServer(("", 8282), RequestHandler)
  #  print ("serving at port", 8282)
   # httpd.serve_forever()
