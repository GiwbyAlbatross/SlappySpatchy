from typing import Union, Optional
import pathlib
import pygame
from pygame import Surface
from pygame.image import load

def render_text(text: str, line: int=0, font_size: int=16, **kwargs) -> Surface:
    "render text"
    #pos = [10, 8 + font_size*line]
    font = pygame.font.Font(kwargs.get('font_id', None), font_size)
    surf = font.render(text, True, (155,255,200))
    return surf

img_cache: dict[str, Surface] = {}
def cached_loadimg(path: Union[str, pathlib.Path], caching_name: Optional[str]=None) -> Surface:
    if caching_name in img_cache:
        return img_cache[caching_name]
    caching_path = str(path)
    if caching_path in img_cache:
        return img_cache[caching_path]
    r = load(caching_path)
    if caching_name is None: img_cache[caching_path] = r
    else: img_cache[caching_name] = r
    return r