import socket
from http.server import *
import sys
import urllib
import threading
import time


routingsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
routingsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
routingsocket.bind(('', 1080))
routingsocket.listen(1000000000)

number_of_servers = 3
counter = 0
page = " "
method = 1         #default round robin

weights = [2, 4, 5]
temp_weight = weights[0]


parent_servers = [("192.168.43.119", 8081), ('192.168.43.119', 8082), ('192.168.43.119', 8080)]

print "Tag --clear-log to clear the log file"
print "Add method tag: e.g. --method=1"
print "1. Round robin"
print "2. Weighted round robin"

if len(sys.argv) >= 2 and "--clear-log" in sys.argv[1]:
	fp = open("requests.log", "w")
	fp.close()
if len(sys.argv) >= 2 and ("--method" in sys.argv[1]):
	type_m = sys.argv[1]
	method = int(type_m.split("=")[1])
elif len(sys.argv) >= 3 and ("--method" in sys.argv[2]):
	type_m = sys.argv[2]
	method = int(type_m.split("=")[1])

assert(method <= 2)



def process_request(client_socket, client_address):
	global counter
	global temp_weight
	global weights
	request = client_socket.recv(1000000000)
	print("Request received from client")
	print request

	timestamp = time.strftime("%d %b %Y %H:%M:%S ", time.localtime())
	fp = open("requests.log", "a+")
	fp.write(timestamp +" "+ str(client_address[0]) +" "+ request.split("\n")[0] + "\n")
	fp.close()


	parentsocket = socket.socket()
	parentsocket.connect(parent_servers[counter])

	if method == 1:
		counter = (counter + 1)%number_of_servers
	elif method == 2:
		temp_weight -= 1
		if temp_weight == 0:
			counter = (counter + 1)%number_of_servers
			temp_weight = weights[counter]

	parentsocket.send(request)
	print "Receiving from parent"
	while True:
		page = parentsocket.recv(1000000000)
		client_socket.send(page)

		if not page:
			break

	print "File received"
	print page
	client_socket.close()
	parentsocket.close()	

while True:
	client_socket, client_address = routingsocket.accept()
	request_thread = threading.Thread(target = process_request, args = (client_socket, client_address))
	request_thread.start()
	request_thread.join()

routingsocket.close()


