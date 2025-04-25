from __future__ import annotations

import pygame
from pygame.locals import *
import pygame.event as events
import slappyspatchy.networking as networking
from slappyspatchy.graphics_utils import rendertext
import slappyspatchy.game
import slappyspatchy.entities
import socket
import threading
import queue

globallock = threading.Lock()

# main server for slappy spatchy
class Server(slappyspatchy.game.BaseGame):
    # static/class attributes
    HOST = '0.0.0.0'
    PORT = 8686 # completely arbitrary
    BIND_PAIR = (HOST, PORT)
    MAX_PLAYERS: int = 8
    
    # instance attributes
    serversocket: socket.socket
    clients: dict[Client] # lookup by clientId
    players: dict[slappyspatchy.entities.EntityPlayer] # lookup by playerId
    entity_lock: threading.Lock
    mainServerThread: threading.Thread
    updates: queue.SimpleQueue
    
    # private or 'protected' methods
    def _render_status_text(self, text, lineno:int=0):
        rendertext(self.scr, text, (96,500 + lineno*50), size=50, colour=(1,1,1))
    
    # runs in threads
    def server(self):
        threadName = "server_client-handler_%08d" # name client-handling theads take
        with self.serversocket as s:
            s.bind(self.BIND_PAIR)
            s.listen(self.MAX_PLAYERS)
            clientId = 42
            while 1:
                client = Client(s.accept()) # blocks, but server loop should 
                with self.entity_lock:
                    client.clientId = clientId
                    client.playerId = playerId
                    self.clients[clientId] = client
                    #self.clients.append(client)
                    clientId += id(client) // 1000
                t = threading.Thread(target=self.serve, name=threadName%clientId, args=(client.clientId))
                t.start()
    def serve(self, clientId: int):
        with self.entity_lock:
            client = self.clients[clientId]
        with client.sock as sock:
            # do main stuff
            
            # add this player
            ...
            
            # do auth here when we add auth (see issue 0x02)
            ...
            
            while self.flags['running']:
                # 'game loop'
                
                # await first tick on client side
                d = sock.recv(1) # BLOCKING CALL, waits for next next client tick, also ives other sockets a go
                if d != b'T':
                    # something is wrong
                    continue # wait for next tick
                # start receiving tick data
                sock.send(
                    bytes(
                        networking.Request(
                            networking.RequestTypes.PLAYER_DATA
                        )
                    )
                ) # request player state and mv
                d = sock.recv(networking.packetfromentity_len)
                with self.entity_lock:
                    networking.update_entity_from_packet(d,
                                self.players[client.playerId],
                                update_score=True)
                    event = pygame.event.Event(self.user_updated_event,
                                               entity=self.players[client.playerId],
                                               playerId=client.playerId)
                    pygame.event.post(event)
                # send (other) player state(s)
                for player in self.players.values():
                    d = networking.packetfromentity(player)
        
    # overrides normal slappyspatchy.game.BaseGame methods
    def set_data(self, flags):
        super().set_data(flags)
        
        # also get event handler IDs
        self.user_updated_event = events.custom_type()
    def init(self, *args, **kwargs):
        super().init(*args, *kwargs)
        # graphics stuff
        self.backdrop = pygame.image.load('logo.png')
        self.flags.target_fps =  1024 / self.TICKRATE
        print('Target FPS:', self.flags.target_fps)
        self.entity_lock = threading.Lock()
        self.scr.blit(self.backdrop, (0,0))
        self._render_status_text("SlappySpatchy server is starting", 1)
        pygame.display.flip()
        # server stuff
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.mainServerThread = threading.Thread(target=self.server, name='server_dispatcher')
        self.mainServerThread.start()
        self.scr.blit(self.backdrop, (0,0))
        self._render_status_text("SlappySpatchy server is up!", 1)
        pygame.display.flip()
    
    def process_events(self, events):
        for event in events:
            if event.type == QUIT:
                self.flags['running'] = False
                # run server shutdown and stuff
                self.cleanup()
            elif event.type == self.user_updated_event:
                entity = event.entity
                with self.entity_lock:
                    # update entity
                    pass
    
    def render_entities(self):
        # overrides slappyspatchy.game.BaseGame.render_entities
        # do nothing, this is a rendering stage and, as a server,
        # we're not wasting our time rendering something that
        # probably won't be seen. In `init` we blit logo and some text
        
        if self.flags['do_debug']:
            # render logo
            self.scr.blit(pygame.image.load('logo.png'), (0,0))
            # render text (TODO)
            self._render_status_text("SlappySpatchy server is up!", 1)
            pygame.display.flip()
    
    def on_tick(self):
        pass

class Client:
    " a class to store and represent the a client "
    # instance attributes
    addr: str
    port: int
    sock: socket.socket
    username: str = 'guest'
    clientId: int
    playerId: int
    
    def __init__(self, conn, addr):
        self.sock = conn
        self.addr = addr[0]
        self.port = addr[1]
    def __hash__(self) -> int:
        return self.clientId
    #def resolve
    def resolveusername(self) -> str:
        "get the username of this client"
        if self.username is not None:
            return self.username
        else:
            # actually query this...
            pass
