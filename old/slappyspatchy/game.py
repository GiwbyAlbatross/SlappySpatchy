import contextlib
import socket
import pygame
import stuuf
from pygame.locals import *
import slappyspatchy.networking as networking
import slappyspatchy.entities as entities

class BaseGame(contextlib.AbstractContextManager):
    # class/static attributes
    TICK: int = USEREVENT
    TICKRATE: int = 1024 // 20
    
#     # instance attributes
    flags: stuuf.Flags = None
    scr: pygame.Surface = ...
    being_rendered: pygame.sprite.Group = ...
    backdrop: pygame.Surface = ...
    def __init__(self):
        self.being_rendered = pygame.sprite.Group()
    def set_data(self, flags: stuuf.Flags):
        "set any data the game is likely to use"
        self.flags = flags
    def init(self, screen: pygame.Surface):
        "initialise game"
        self.scr = screen
        pygame.time.set_timer(self.TICK, self.TICKRATE)
    def process_events(self, events):
        "process events as returned by `pygame.events.get`"
        for event in events:
            if event.type == QUIT:
                self.flags['running'] = False
            elif event.type == self.TICK:
                # do tick. this is the game's main sense of "do something every
                # <whenever". Client uses this to sync with server and server
                # uses this to do server things.
                self.on_tick()
    def on_frame(self, dt: float, debug: bool=True):
        # render frames, etc.
        self.render_entities()
        ...
    def on_tick(self):
        "abstract method that is run on tick"
        pass
    def render_entities(self, *, prefer_render_method: bool=__debug__, **render_options):
        "render entities in `this.being_rendered` to `this.scr`"
        for sprite in self.being_rendered:
            if hasattr(sprite, 'render') and prefer_render_method:
                sprite.render(self.scr, **render_options)
            else:
                self.scr.blit(sprite.surf, sprite.rect)
    def cleanup(self):
        "free resources owned by this Game, clean up open windows, etc."
        pass
    #def __enter__(self):
    #    return self
    def __exit__(self, *exc):
        self.cleanup()
        return False
    def __del__(self):
        self.cleanup()

class Game(BaseGame):
    players: pygame.sprite.Group = ...
    spatulas:pygame.sprite.Group = ...
    player: entities.EntityPlayer
    
    def init(self, screen: pygame.Surface):
        super().init(screen)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def on_tick(self):
        self.sock.send(b'T') # has to be 'T' or server skips tick, idk what it means (i made it but i can't remember)
        if networking.Request.from_bytes(self.sock.recv(12)).type == networking.RequestTypes.PLAYER_DATA:
            # send player data
            self.sock.send(networking.packetfromentity(player))
        else:
            # something is off, this clearly isn't the vanilla server...
            pass
