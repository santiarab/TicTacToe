import socket
import queue
from typing import Tuple

MAX_PLAYERS = 2
PORT = 5001

class Board:
    def __init__(self):
        self._finish = False
        self._board = [[0,0,0],[0,0,0],[0,0,0]]
    def set(self, coordinates : Tuple[int,int], player : int) -> bool:
        x,y = coordinates
        if self._finish:
            raise ValueError("The Board is finished")
        if x < 0 or x >= len(self._board) or y < 0 or y >= len(self._board[0]):
            raise ValueError("Coordinates out of board range.")
        if self._board[x][y] != 0:
            raise ValueError("Position already set")
        if player > 2 or player < 1:
            raise ValueError("Player is incorrect") 
        self._board[x][y] = player
        self._finish = self._check_winner(x,y,player)
        return True

    def _check_winner(self, x : int, y: int, player: int) -> bool :
        if all(self._board[x][col] == player for col in range(3)):
            return True
        if all(self._board[row][y] == player for row in range(3)):
            return True
        if x == y and all(self._board[i][i] == player for i in range(3)):
            return True
        if x + y == 2 and all(self._board[i][2-i] == player for i in range(3)):
            return True
        return False
    
    def display(self):
        for row in self._board:
            print(row)
    def getFinish(self) -> bool:
        return self._finish
    def getBoard(self) -> list[list[int]]:
        return self._board

def parsingCode(code : str) -> list:
    codParse = code.split('-')
    if len(codParse) < 2:
        raise ValueError("The text must contain at least two parts separated by '-'")
    try:
        codParseToNumber = [int(codParse[0].strip()), int(codParse[1].strip())]
    except ValueError:
        raise ValueError("Text parts must be valid integers")
    return codParseToNumber


def validateCoord(conn, gameBoard:Board,player):
    msg = "3"
    while True:
        try:
            conn.send(msg.encode())
            recive = conn.recv(1024).decode("ascii")
            coor = parsingCode(recive)
            if gameBoard.set((coor[0],coor[1]),player):
                return
            msg = "4"
        except ValueError as e:
            msg = "4"


def connection(port, max_pend) -> socket.socket:
    ss = socket.socket()
    try:
        ss.bind(("127.0.0.1", port))
        ss.listen(max_pend)
    except Exception as e:
        ValueError(e)
    return ss

def addToThePlayers(ss : socket.socket) -> queue.Queue:
    queueOfPlayers = queue.Queue(MAX_PLAYERS)
    for i in range(MAX_PLAYERS):
        (conn, dir) = ss.accept()
        queueOfPlayers.put((conn, dir,i+1))
    return queueOfPlayers

def sendBoard(matrix : list[list[int]] ,conn):
    msg = "5"
    conn.send(msg.encode())
    conn.recv(1024).decode("ascii")
    matrix_str = str(matrix)
    conn.send(matrix_str.encode())
    conn.recv(1024).decode("ascii")

def play(ss, players: queue.Queue):
    gameBoard = Board()
    try:
        while not gameBoard.getFinish():
            conn, dir, player = players.get()
            players.put((conn, dir, player))

            sendBoard(gameBoard.getBoard(),conn)
            validateCoord(conn, gameBoard, player)
            sendBoard(gameBoard.getBoard(),conn)

            if gameBoard.getFinish():
                sendBoard(gameBoard.getBoard(),conn)
                msg = "1"
                conn.send(msg.encode())
                conn.close()
                conn, dir, player = players.get()
                sendBoard(gameBoard.getBoard(),conn)
                msg = "2"
                conn.send(msg.encode())
                conn.close()
    except Exception as e:
        raise socket.error(e)
    finally:
        while not players.empty():
            conn, dir, player = players.get()
            msg = "6"
            try:
                conn.send(msg.encode())
            except:
                pass
            finally:
                conn.close()
        ss.close()
           
if __name__ == "__main__":
    try:
        ss = connection(PORT,MAX_PLAYERS)
        queueOfPlayers = addToThePlayers(ss)
        play(ss, queueOfPlayers)
    except socket.error as e:
        print("There was an error: " , e)
    finally:
        ss.close()
    print("It was completed successfully")
