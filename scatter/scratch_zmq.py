import zmq
import zmq.decorators as zmqd


@zmqd.socket(zmq.PUSH)
def send(sock):
    sock.bind('tcp://*:5555')
    sock.send(b'hello')


# in another process
@zmqd.socket(zmq.PULL)
def recv(sock):
    sock.connect('tcp://localhost:5555')
    print(sock.recv())  # shows b'hello'
