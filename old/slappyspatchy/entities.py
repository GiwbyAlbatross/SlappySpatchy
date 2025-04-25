import pygame
import stuuf
import slappyspatchy.data
import slappyspatchy.textures

class Entity(stuuf.Entity):
    # instance attributes
    #
    # rendering properties
    pos:  pygame.math.Vector2
    mv:   pygame.math.Vector2
    surf: pygame.Surface
    texName: str
    # game values
    isSlapping: bool = False
    health: int = -1 # -1 means does not apply, but health property is used for durability in spatulas
    spatulaRank: int = None # except that spatulaRank is a list index, where -1 means 'at the end'
    points: int = 0  # normally doesn't really apply, but it's there...
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.surf = pygame.Surface(kwargs['size'])
        self.rect = stuuf.FRect(kwargs['start_pos'], kwargs['size'])
        self.pos, self.mv = pygame.Vector2(kwargs['start_pos']),\
                            pygame.Vector2(*(kwargs.get('start_mv', (0,0))))
    def _update_pos(self):
        """update rect to match pos.
In subclasses this can be overrided to make `self.pos` represent other points on the rect
not just `rect.center`"""
        self.rect.center = self.pos

class EntityParticle(Entity):
    "particle class, loads arbitrary images and displays them for one tick"
    lifeexpectancy: float
    birthday: float
    was_alive: bool
    def __init__(self, pos, texName: str, life_expectancy: float=1.0):
        tex = pygame.image.load(texName)
        super().__init__(size=tex.get_size(), start_pos=pos)
        self.surf.blit(tex, (0,0))
        self.was_alive = False
        self.lifeecpectancy = life_expectancy
    def update(self, dt: float):
        super().update(dt)
        #self.aliveFor
        if self.alive() and (not self.was_alive):
            # just spawned
            self.was_alive = True
            self.birthday  = self.aliveFor
        if self.aliveFor - self.birthday > self.lifeexpectancy:
            self.kill() # past life expectancy :)

class EntityPlayer(Entity):
    textures: dict[str, slappyspatchy.textures.PlayerTexturePack] = {
        i:slappyspatchy.textures.load_texture_pack(i) for i in slappyspatchy.data.load_player_texturepack_names()
    } # class/static attribute
    
    # instance attributes
    playerId: int
    
    def __init__(self):
        pass
    def update(self, dt: float):
        super(EntityPlayer, self).update(dt)
    def update_data(self, pos: pygame.Vector2=None, mv: pygame.Vector2=None):
        "update data to match values (from network?) serves much the same purpose as .networking.update_entity_from_packet"
        # just trust any data, apparently...
        # the blind beliving-ness of this function
        # could be abused in hacked clients, maybe
        # that some day...
        if pos is not None:
            self.pos = pos
        if mv is not None:
            self.mv = mv
