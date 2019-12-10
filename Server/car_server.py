#!/usr/bin/env python3
import socket
import numpy as np
import cv2

from socket_base import SocketBase
from RoadLaneVision import RoadLaneVision
from RoadSignsVision import RoadSignsVision

debug = True
connection = ('', 3005)
header_size = 10
encoding = 'ISO-8859-1'

socket_base = SocketBase(header_size, encoding)
lane_vision = RoadLaneVision(corners=((0, 300), (85, 205), (555, 205), (640, 300)))
sign_vision = RoadSignsVision()

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
					print('Received', len(client_msg), 'bytes')

				img_bytes = np.fromstring(client_msg, np.uint8)
				img = cv2.imdecode(img_bytes, cv2.IMREAD_GRAYSCALE)

				detected = {}
				detected['stop'] = sign_vision.find_stop_sign(img, debug)
				detected['degree'] = lane_vision.get_angle(img, debug)

				
				if debug:
					cv2.imshow('Stop signs', detected['stop'][1])
					cv2.imshow('Road lane', detected['degree'][1])
					cv2.imshow('Vision', img);
					key = cv2.waitKey(1)
					if key == 27:
						raise KeyboardInterrupt()

					

				detected['stop'] = detected['stop'][0]
				detected['degree'] = detected['degree'][0]
				

				# commands - string that you will send to the client
				commands = 'your_class.your_method(detected)' # !!!!!!!!!!!!!!!!!!


				print('Sending', commands)
				socket_base.send_message(client, commands)
			except Exception as e:
				print(e)
				cv2.destroyAllWindows()
				client.close()
				sock.close()
				print('Server down')
