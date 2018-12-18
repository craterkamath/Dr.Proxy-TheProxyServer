from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import os
import urllib2
import hashlib
import collections
import threading

class webServerHandler(BaseHTTPRequestHandler):

    def compare(self,x,y) : 
        return collections.Counter(x) == collections.Counter(y)

    
    def validate_cache(self,cache_filename) : 
        print "Validating Cache"
        old_data = open(cache_filename).readlines()
        new_data = urllib2.urlopen(self.path).readlines()
        #now i have 2 lists, need to check if they are equal
        if not self.compare(new_data,old_data):
            open(cache_filename,'w+').writelines(new_data)
        print "Validated Cache"

    def do_GET(self):
        try:
            m = hashlib.md5()
            m.update(self.path)
            cache_filename = m.hexdigest() + ".cached"
            cache_hit = 0 
            if os.path.exists(cache_filename) : 
                print "Cache hit"
                data = open(cache_filename).readlines()
                cache_hit = 1
            else:
                print "Cache miss"
                print "http:/" + self.path
                data = urllib2.urlopen(self.path).readlines()
                open(cache_filename,'w+').writelines(data)
                print "Cached Page"
            #print len(data)
            self.send_response(200)
            #self.send_header()
            
            
            self.end_headers()
            self.wfile.writelines(data)
            
            if cache_hit : 
                validate_cache_thread = threading.Thread(target = self.validate_cache,args = (cache_filename,))
                validate_cache_thread.start()
                validate_cache_thread.join()
            
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


def main():
    try:
        port = 8081
        server = HTTPServer(('192.168.43.119', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
