from cryptography.fernet import Fernet
import random
import socket
import pickle
import RSA
import numpy as np

def garbled_circuit(Alice_input):
    
    # Step1: Pick Random Keys For Each Wire
    keyX0 = Fernet.generate_key()
    keyX1 = Fernet.generate_key()

    keyY0 = Fernet.generate_key()
    keyY1 = Fernet.generate_key()

    keyZ0 = Fernet.generate_key()
    keyZ1 = Fernet.generate_key()
    # Step 2: Create Truth Table (AND gate)
    outputs=[] # output of the AND gate

    for x in range(0,2):
        for y in range(0,2):
            if x == 1 and y == 1:
                outputs.append(keyZ1)
            else:
                outputs.append(keyZ0)
    
                
    # Step 3: Encrypt Truth Table
    encrypted00 = Fernet(keyX0).encrypt(Fernet(keyY0).encrypt(outputs[0]))
    encrypted01 = Fernet(keyX0).encrypt(Fernet(keyY1).encrypt(outputs[1]))
    encrypted10 = Fernet(keyX1).encrypt(Fernet(keyY0).encrypt(outputs[2]))
    encrypted11 = Fernet(keyX1).encrypt(Fernet(keyY1).encrypt(outputs[3]))
    
    table = [encrypted00, 
            encrypted01, 
            encrypted10, 
            encrypted11]
    # print(table[0])
    # Step 4: Permutes Garbled Truth Table
    truth_table = np.array(table)
    np.random.shuffle(truth_table)
    print(repr(keyX0))
    print(repr(keyY1))
    print(repr(encrypted01))
    print(repr(outputs[1]))
    
    # Step 5: Send Garbled Truth Table & Key For Alice’s Input
    input_key = keyX0 if Alice_input == 0 else keyX1
    return truth_table, input_key, keyY0, keyY1, [keyZ0, keyZ1]

def gen_randoms(): 
    r1 = random.randint(100, 1000) 
    r2 = random.randint(100, 1000)
    while (r2 == r1): 
        r2 = random.randint(100, 1000)
    return [r1, r2]
    
def alice_program():
    with open("../input/alice_input.txt") as f: 
        alice_input = int(f.read())  # take input
    host = socket.gethostname()  # as both code is running on same pc
    port = 5000  # socket server port number
    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server
    print("Connection to Bob is established")
    

    # garbling the table
    truth_table, input_key, keyY0, keyY1, output= garbled_circuit(alice_input)
    random_string = gen_randoms()
    sk, pk = RSA.rsa_genKeys()

    client_socket.send(pickle.dumps([truth_table, random_string, pk, input_key]))  # send to bob
    print("Truth table, random string, input key, and RSA PK is sent to Bob")
    v = pickle.loads(client_socket.recv(1024))  # receive response
    print("V is received from bob")
    k0 = ((v-random_string[0])**sk[1]) % sk[0]
    k1 = ((v-random_string[1])**sk[1]) % sk[0]

    m0 = keyY0 + str(k0).encode()
    m1 = keyY1 + str(k1).encode()

    client_socket.send(pickle.dumps([m0, m1]))
    print("m0 and m1 is send to Bob")
    result = pickle.loads(client_socket.recv(1024))
    if output[0] == result:
        result = 0
    else:
        result = 1
    print("The result is", result)
    # client_socket.close()  # close the connection


if __name__ == '__main__':
    alice_program()