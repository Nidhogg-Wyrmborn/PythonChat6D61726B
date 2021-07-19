try:
	import socket
	import Server
	from threading import Thread

	serverthread = Thread(target=Server.main)
	serverthread.daemon = True
	serverthread.start()

	# server's IP address
	SERVER_HOST = "0.0.0.0"
	SERVER_PORT = 5002 # port we want to use
	separator_token = "<SEPARATOR>" # we will use this to separate the client name & message


	# initialize list/set of all connected client's sockets
	client_sockets = set()
	client_addresses = set()
	# create a TCP socket
	s = socket.socket()
	# make the port as reusable port
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# bind the socket to the address we specified
	s.bind((SERVER_HOST, SERVER_PORT))
	# listen for upcoming connections
	s.listen(5)
	print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

	def listen_for_client(cs,address):
		"""
		This function keep listening for a message from `cs` socket
		whenever a message is received, broadcast it to all other connected clients
		"""
		while True:
			try:
				# keep listening for a message from `cs` socket
				msg = cs.recv(1024).decode()
			except Exception as e:
				# client no longer connected
				# remove it from the set
				print(f"[!] Error: {e}")
				client_sockets.remove(cs)
				client_addresses.remove(address)
			else:
				if msg == f"{separator_token}LISTCLIENT{separator_token}":
					cs.send(f'REQUEST FROM {address}: LISTCLIENTS\n{client_addresses}'.encode())
				else:
					# if we received a message, replace the <SEP>
					# token with ": " for nice printing
					msg = msg.replace(separator_token, ": ")
			# iterate over all connected sockets
			for client_socket in client_sockets:
				# and send the message
				client_socket.send(msg.encode())

	def start_transfer_server():
		import Server
		try:
			Server.main()
			round1 = True
		except Exception as e:
			print(e)
			print("error restarting transfer server") # you do know that you are not allowed jewellary at school right?

	while True:
		# we keep listening for new connections all the time
		client_socket, client_address = s.accept()
		print(f"[+] {client_address} connected.")
		# add the new connected client to connected sockets
		client_addresses.add(client_address[0])
		client_sockets.add(client_socket)
		# start a new thread that listens for each clients messages
		t = Thread(target=listen_for_client, args=(client_socket,client_address,))
		# make the thread daemon so it ends whenever the main thread ends
		t.daemon = True
		# start the thread
		t.start()

	# close client socket
	for cs in client_sockets:
		cs.close()
	# close server socket
	s.close()
except Exception as e:
	print(e)