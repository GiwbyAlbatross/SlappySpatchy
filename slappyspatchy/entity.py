import pygame
from pygame.locals import *
import struct
from .util import render_text

ENTITY_POS_FRMT = '!hhffH?'

class BasePlayer(pygame.sprite.Sprite):
    "Base player class, with logic and no graphics"
    username: bytes=b'Herobrine'
    MAX_HEALTH: int=150
    slapping_hitbox: pygame.rect.Rect
    slapping: bool=False
    rect: pygame.rect.FRect
    mv: pygame.math.Vector2
    hp: int
    ip: str # IP address of this player
    def __init__(self, username: str='Harry', pos: tuple[int,int] = (100,100)):
        super().__init__()
        self.username = username.encode('utf-8')
        self.rect = pygame.FRect(pos, (50,50))
        self.slapping_hitbox = pygame.Rect(self.rect)
        self.mv = pygame.Vector2(0)
        self.hp = self.MAX_HEALTH
    def update_location(self, packet: bytes, *, update_pos: bool=True, update_stats: bool=False):
        left, top, mvx, mvy, hp, slapping = struct.unpack(ENTITY_POS_FRMT, packet)
        if update_pos:
            self.rect.left = left
            self.rect.top  = top
            self.mv.x = mvx
            self.mv.y = mvy
            self.slapping = slapping
        if update_stats:
            self.hp = hp
    def export_location(self) -> bytes:
        left = int(self.rect.left)
        top  = int(self.rect.top)
        mvx = self.mv.x
        mvy = self.mv.y
        return struct.pack(ENTITY_POS_FRMT, left, top, mvx, mvy, self.hp, self.slapping)
    def update_pos(self, dt: float=1000/60):
        mv = self.mv * (dt / 1000)
        self.rect.move_ip(mv)
        self.slapping_hitbox = self.rect.move(mv*8) # slapping hitbox is always offset by mv*8

class RenderedPlayer(BasePlayer):
    surf: pygame.surface.Surface
    slapping_for: int=0
    def __init__(self, username: str='Harry', pos: tuple[int,int] = (100,100)):
        super().__init__(username, pos)
        self.surf = pygame.Surface(self.rect.size)
        self.surf.fill([200,200,200])
    def update_keypresses(self, keys, mods):
        speed = 90 if mods & KMOD_SHIFT else (200 if mods & KMOD_CTRL else 145) # pixels per second
        mv = pygame.Vector2(0)
        if keys[K_w]:
            mv.y -= speed
        if keys[K_s]:
            mv.y += speed
        if keys[K_a]:
            mv.x -= speed
        if keys[K_d]:
            mv.x += speed
        self.mv = mv
    def update_pos(self, dt: float=1000/60):
        super().update_pos(dt)
        if self.slapping:
            self.slapping_for += dt
        else:
            self.slapping_for = 0
    def render_nametag(self, surf: pygame.Surface):
        s = render_text(self.username.decode('utf-8'))
        r = s.get_rect(bottom=self.rect.top, centerx=self.rect.centerx)
        surf.blit(s,r)
    def render_slap_anim(self, surf: pygame.Surface):
        return NotImplemented # yet :)
