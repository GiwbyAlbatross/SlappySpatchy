import pygame

def rendertext(surf: pygame.Surface, text: str, pos, size: int=20, colour=(255,255,255)):
    font = pygame.font.Font(None, size)
    #font.align = pygame.FONT_CENTER
    return surf.blit(font.render(text, True, colour), pos)