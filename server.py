import socket
import threading
import slappyspatchy
import atexit

MAX_USERS: int = 16

players_lock = threading.Lock()
printlock = threading.Lock()
players: dict[str, slappyspatchy.BasePlayer] = {}

def serve(conn: socket.socket, addr):
    request_type = conn.recv(3)
    username = conn.recv(8).decode('utf-8') # usernames MUST be 8 chars long
    with printlock:
        print(f"\033[1m{request_type.decode()!r} request from {username}\033[0m ({addr[0]} on port {addr[1]})")
    if request_type == b'JON': # JOIN request
        with players_lock:
            players[username] = slappyspatchy.BasePlayer(username)
    elif request_type == b'GET': # request data about a given player
        with players_lock:
            data = players[username].export_location()
        conn.send(data)
    elif request_type == b'SET': # set data about a given player
        data = conn.recv(slappyspatchy.network.ENTITY_POS_FRMT_LEN)
        with players_lock:
            players[username].update_location(data)
    elif request_type == b'LSP': # list players
        with players_lock:
            players_list = players.keys()
        with printlock:
            print("Players:", players_list)
        for player in players_list:
            conn.send(player.encode('utf-8'))
        conn.send(b'.' * 8)
    else:
        with printlock:
            print("Received invalid request_type {request_type!r} from {username!r}")
    conn.close()
    

def main():
    def cleanup():
        s.close()
    atexit.register(cleanup)
    with slappyspatchy.network.new_sock() as s:
        s.bind(('0.0.0.0', slappyspatchy.PORT))
        while 1:
            s.listen(MAX_USERS)
            threading.Thread(target=serve, args=s.accept()).start()

if __name__ == '__main__':
    main()