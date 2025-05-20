from . import entity as _entity
import struct
import socket

ENTITY_POS_FRMT = _entity.ENTITY_POS_FRMT
ENTITY_POS_FRMT_LEN = struct.calcsize(ENTITY_POS_FRMT)

def new_sock() -> socket.socket:
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_event(username: bytes, type: str):
    with new_sock() as s:
        s.send(b'EVT') # 'event'
        s.send(username)
        s.send(type.encode('ascii'))