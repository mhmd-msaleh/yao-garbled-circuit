import socket

from cryptography.fernet import Fernet
import random
import pickle
import RSA


def bob_program():
    with open("../input/bob_input.txt") as f: 
        bob_input = int(f.read())  # take input
    # get the hostname
    host = socket.gethostname()
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))

        # receive data stream. it won't accept data packet greater than 1024 bytes
    data = pickle.loads(conn.recv(4096)) # we have truth_table Random_string and PK
    print("Truth table, random string, input key, and RSA PK recieved from Alice")
    truth_table = data[0]
    # print(truth_table)
    alice_random = data[1]
    pk = data[2]
    alice_input = data[3]
    print("Starting Oblivious Transfer protocol: ")
    print("***** finding k")
    k = random.randint(10, 1000)
    choice = bob_input
    print("***** selected choice", choice)
    print("***** Finding v")
    v = (alice_random[choice]+pow(k, pk[1])) % pk[0]
    conn.send(pickle.dumps(v))  # send data to the client
    print("V is sent to Alice")
    data = pickle.loads(conn.recv(1024)) 
    print("m1 and m0 received from Alice")
    kyn = data[choice].decode("utf-8").split('=', 1)[0]+'='
    kyn = kyn.encode('utf-8')
    result = decrypt(kyn, alice_input, truth_table)
    print("The result is", result)
    conn.send(pickle.dumps(result))

def decrypt(kyn, kxn, truth_table): 
    print(truth_table)
    # print(kyn)
    # kyn = Fernet.base64.b64encode(kyn)
    print("*********** Decrypting the Message **************")
    index = 0 
    for i in range(len(truth_table)):
        cipher = truth_table[i]
        print(repr(kyn))
        print(repr(kxn))
        print(repr(cipher))
        try:
            pt = Fernet(kyn).decrypt(Fernet(kxn).decrypt(cipher))
            return pt
        except:
            pass

if __name__ == '__main__':
    bob_program()
