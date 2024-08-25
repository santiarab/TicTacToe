import os
import socket
import time

MAX_ATTEMPTS = 5
TIMEOUT = 2
PORT = 5001


def connectToServer(port:int):
    intento = 0
    while intento < MAX_ATTEMPTS:
        cs = socket.socket()
        try:
            cs.connect(("127.0.0.1", port))
            print("Socket was connected successfully")
            return cs
        except (ConnectionRefusedError, socket.gaierror) as e:
            print("Socket wasn't connected successfully, It will retry again")
            intento+=1
            time.sleep(TIMEOUT)
    raise ValueError("Could not be connected successfully")

def receive_matrix(ss):
    aux = "ok"
    ss.send(aux.encode())
    matrix_str = ss.recv(1024).decode("ascii")
    ss.send(aux.encode())
    matrix = eval(matrix_str)
    return matrix

def paintMatrix(matrix):
    os.system('clear')
    for row in matrix:
            print(row)

def play(ss):
    try:
        while True:
            try:
                msg = ss.recv(1024).decode("ascii")
                if msg == "1":
                    print("You Win")
                    break
                elif msg == "2":
                    print("You Lose")
                    break
                elif msg == "3":
                    cord = input("Enter Coordinates: ")  
                    ss.send(cord.encode())
                elif msg == "4":
                    print("The coordinates aren't valid, please try again.")
                    cord = input("Enter Coordinates: ")  
                    ss.send(cord.encode())
                elif msg == "5":
                    matrix = receive_matrix(ss)
                    paintMatrix(matrix)
                else:
                    print("There was an error!")
                    ss.close()
                    break
            except socket.error as e:
                print(f"Connection error: {e}")
    except socket.error as e:
        print(f"Connection error: {e}")
    finally:
        ss.close()  

if __name__ == '__main__':
    try:
        ss = connectToServer(PORT)
        play(ss)
    except Exception as e:
        print(e)
