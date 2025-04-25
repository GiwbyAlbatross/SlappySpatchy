from dataclasses import dataclass
import pygame
import slappyspatchy.data as _data

@dataclass
class PlayerTexturePack:
    base: pygame.Surface
    lookingAway: pygame.Surface

def load_texture_pack(prefix: str, /) -> PlayerTexturePack:
    return PlayerTexturePack(base=pygame.image.load(prefix+'Base.png'), lookingAway=pygame.image.load(prefix+'lookingAway.png'))
