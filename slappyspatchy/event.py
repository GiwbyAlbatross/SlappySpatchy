from __future__ import annotations
import slappyspatchy

EVENTIDS_BY_EVENT_TYPE = {'slap':1}
EVENT_TYPES_BY_EVENTID = {v:k for k,v in EVENTIDS_BY_EVENT_TYPE.items()}

def process(username: str, event_id: int, players: dict[str, slappyspatchy.BasePlayer]):
    event_type = EVENT_TYPES_BY_EVENTID[event_id]
    print("\033[1mEVENT:", event_type, end='\033[0m\n')
    if event_type == 'slap':
        slapper = players[username]
        for uname, player in players.items():
            if uname == username:
                continue
            if slapper.rect.colliderect(player.rect):
                player.hp -= 10
                print("Slapping", uname, "who's HP is now", player.hp)
def send_event(username: str, event_type: str, host: tuple[str, int]=('0.0.0.0', slappyspatchy.PORT)):
    eventid = EVENTIDS_BY_EVENT_TYPE[event_type]
    with slappyspatchy.network.new_sock() as s:
        s.connect(host)
        s.sendall(b'EVT')
        s.sendall(username)
        s.sendall(eventid.to_bytes(2, 'big'))