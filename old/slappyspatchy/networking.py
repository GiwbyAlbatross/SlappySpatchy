import enum
import stuuf
import struct
import socket
import pygame.math
import slappyspatchy.entities
from stuuf import packetfromvector, vectorfrompacket
from slappyspatchy.utils import SlappingError

settings = stuuf.Flags(loc_pin='center')

packetfromentity_frmt = '!9sx9sh8pH?HHI'
packetfromentity_len: int = struct.calcsize(packetfromentity_frmt)

# packet from <obj> and <obj> from packet functions
def packetfromentity(entity: slappyspatchy.entities.Entity) -> bytes:
    loc = packetfromvector(entity.pos) # or perhaps send Rect data?
    mv  = packetfromvector(entity.mv)
    return struct.pack(packetfromentity_frmt,
                       loc, mv, # location and movement-vector
                       entity.state, # state number
                       entity.texName.encode('utf-8'), # send texName even if it's not used
                       entity.health, # health value
                       entity.isSlapping, # is slapping (very important)
                       entity.spatulaRank, # used to identify spatula
                       entity.points, # only decoded when the current player is being decoded
                       (entity.playerId if hasattr(entity, 'playerId') else 0),
        )

def getplayerId(packet: bytes) -> int:
    loc, mv, state, texName, hp, slapping, spatRank, xp, playerId = struct.unpack(packetfromentity_frmt, packet)
    return playerId

# update <obj> from packet functions
def update_entity_from_packet(packet: bytes, entity: slappyspatchy.entities.Entity, **options) -> None:
    # works in-place, should be done before texture update
    
    # just trust any data, apparently...
    # the blind beliving-ness of this function
    # could be abused in hacked clients, maybe
    # fix that some day... (see issue 0x00)
    loc, mv, state, texName, hp, slapping, spatRank, xp, playerId = struct.unpack(packetfromentity_frmt, packet)
    
    entity.state = state
    entity.mv = vectorfrompacket(mv) # perhaps check this vector's length() to test for teleporting players... (see issue 0x00)
    update_rect_from_packet(loc, entity.rect)
    entity.isSlapping = slapping # always true for spatulas
    entity.spatulaRank= spatRank
    
    if options.get('update_score', False):
        entity.health = hp
        entity.points = xp
    
    if options.get('update_texName', True):
        entity.texName = texName.decode('utf-8')
def update_rect_from_packet(packet: bytes, rect: stuuf.FRect):
    loc_pin = settings['loc_pin']
    
    loc = vectorfrompacket(packet)
    
    if loc_pin == 'center':
        rect.center = loc
    if loc_pin == 'topleft':
        rect.topleft = loc

# request IDs and so on
REQUEST = b'REQ '

class RequestTypes(enum.Enum):
    PLAYER_DATA = b'PLYR'
    OTHERENTITIES_DATA = b'NTTs'

class Request:
    type: RequestTypes
    def __init__(self, type_: RequestTypes, *data):
        self.type = type_
        self.data = ('-'.join(d.decode('utf-8') for d in data)).encode('utf-8')
    def __bytes__(self) -> bytes:
        return REQUEST + self.type + self.data
    def get_data(self) -> list[bytes]:
        return [d.encode('utf-8') for d in self.data.decode('utf-8').split()]
    @classmethod
    def from_bytes(cls, b: bytes):
        if b[:4] != REQUEST:
            raise SlappingError(f"Non Request packet: {b!r}")
        return cls(b[4:8], b[9:])
