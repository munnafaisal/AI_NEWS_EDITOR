import socket
import time
import threading

def test_loop(a):
    global z
    for i in range(1000):
        z = i
        time.sleep(1)


def run_server():
    # create a socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = "127.0.0.1"
    port = 9000

    # bind the socket to a specific address and port
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((server_ip, port))
    # listen for incoming connections
    server.listen(0)
    print(f"Listening on {server_ip}:{port}")

    # accept incoming connections
    client_socket, client_address = server.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

    # receive data from the client
    while True:
        request = client_socket.recv(1024)
        request = request.decode("utf-8")  # convert bytes to string

        # if we receive "close" from the client, then we break
        # out of the loop and close the conneciton
        if request.lower() == "close":
            # send response to the client which acknowledges that the
            # connection should be closed and break out of the loop
            client_socket.send("closed".encode("utf-8"))
            break



        print(f"Received: {request}")

        # for i in range(10):
        #
        #     msg = str(i)+ "_" + "accepted"  # convert string to bytes
        #     response = msg.encode("utf-8")
        #     # convert and send accept response to the client
        #     client_socket.send(response)
        #     time.sleep(2)

        msg = "counter " + str(z)  # convert string to bytes
        response = msg.encode("utf-8")
        # convert and send accept response to the client
        client_socket.send(response)


    # close connection socket with the client
    client_socket.close()
    print("Connection to client closed")
    # close server socket
    server.close()


t1 = threading.Thread(target=test_loop,args=(1,),name="test")
t1.daemon=False
t1.start()

run_server()
