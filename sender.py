import zmq

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect('tcp://127.0.0.1:5558')


for number in range(1, 100):
    socket.send_string("message: {}".format(number))
