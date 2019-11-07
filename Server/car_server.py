#!/usr/bin/env python3
import socket
import numpy as np
import cv2

from socket_base import SocketBase

debug = True
connection = ('', 3005)
header_size = 10
encoding = 'ISO-8859-1'
socket_base = SocketBase(header_size, encoding)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(connection)
sock.listen(1)
print('Listening on port', connection[1])
client = None


while True:
	try:
		client, address = sock.accept()
	except Exception as e:
		print(e)
		if client is not None:
			client.close()
		sock.close()
		print('Server down')
		break
	else:
		print('Connected:', address)
		while True:
			try:
				client_msg = socket_base.receive_message(client)[header_size:].rstrip()
				client_msg = bytes(client_msg, encoding)
				if debug:
					print('received', len(client_msg), type(client_msg), client_msg)

				img_bytes = np.fromstring(client_msg, np.uint8)
				img = cv2.imdecode(img_bytes, cv2.IMREAD_GRAYSCALE)
				if debug:
					cv2.imshow('Vision', img)
					key = cv2.waitKey(1)
					if key == 27:
						raise KeyboardInterrupt()
					print('sending')

				socket_base.send_message(client, '<Commands>')
			except Exception as e:
				print(e)
				cv2.destroyAllWindows()
				client.close()
				sock.close()
				print('Server down')
