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
        print(f"{request_type.decode()!r} request from {username}\033[2m ({addr[0]} on port {addr[1]})\033[0m")
    if request_type == b'JON': # JOIN request
        with players_lock:
            players[username] = slappyspatchy.BasePlayer(username)
    elif request_type == b'GET': # request data about a given player
        try:
            with players_lock:
                if players[username].hp <= 0:
                    del players[username]
                    conn.close()
                    return 
                data = players[username].export_location()
            conn.sendall(data)
        except KeyError: pass
    elif request_type == b'SET': # set data about a given player
        try:
            data = conn.recv(slappyspatchy.network.ENTITY_POS_FRMT_LEN)
            with players_lock:
                players[username].update_location(data)
        except KeyError:
            conn.close()
    elif request_type == b'LSP': # list players
        with players_lock:
            players_list = players.keys()
            #with printlock:
            #    print("Players:", players_list)
            for player in players_list:
                conn.sendall(player.encode('utf-8'))
        conn.sendall(b'.' * 8)
    elif request_type == b'EVT': # process event
        event_id = int.from_bytes(conn.recv(2), 'big') # two-byte event ID, big-endian
        slappyspatchy.event.process(username, event_id, players)
    else:
        with printlock:
            print("Received invalid request_type {request_type!r} from {username!r}")
    conn.close()
    

def main():
    def cleanup():
        s.close()
    atexit.register(cleanup)
    with slappyspatchy.network.new_sock() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', slappyspatchy.PORT))
        print("SlappySpatchy server up on port", slappyspatchy.PORT)
        while 1:
            s.listen(MAX_USERS)
            try:
                threading.Thread(target=serve, args=s.accept()).start()
            except KeyboardInterrupt:
                s.close()
                break

if __name__ == '__main__':
    main()
