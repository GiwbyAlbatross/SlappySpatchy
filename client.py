import pygame
import socket
import slappyspatchy
import time
import sys

pygame.init()

HOST = ('0.0.0.0', slappyspatchy.PORT)

scr_w = 400
scr_h = 400
username = ('user' + str(hash('hello world')))[:8] # generate username or
if len(sys.argv) > 1: username = sys.argv[-1][:8]  # use supplied username

def update_status(*args): # for debugging
    #print(*args, ' '*24, end='\r', flush=True)
    #time.sleep(0.1)
    pass
def setdead():
    global run
    run = 0
    print("\033[1;31mYOU DIED\033[0m")

update_status("Loading")

scr = pygame.display.set_mode([scr_w, scr_h])

players = pygame.sprite.Group()
player_usernames = [username.encode('utf-8')]
me = slappyspatchy.entity.RenderedPlayer(username)
players.add(me)

TICK = pygame.event.custom_type()
pygame.time.set_timer(TICK, 200)

run = 1
clk = pygame.time.Clock()
username = username.encode('utf-8')

update_status("Joining")

try:
    with slappyspatchy.network.new_sock() as sock:
        sock.connect(HOST)
        sock.send(b'JON')
        sock.send(username)
except ConnectionRefusedError:
    print("\033[1mCONNECTION REFUSED\033[0m", file=sys.stderr)
    print("Server probably isn't up. Quitting")
    update_status("Quitting")
    run = 0

while run:
    dt = clk.tick(60)
    for event in pygame.event.get():
        if event.type == TICK:
            try:
                update_status("LSPing")
                with slappyspatchy.network.new_sock() as sock:
                    sock.connect(HOST)
                    sock.send(b'LSP')
                    sock.send(username) # important part of protocol
                    d = username
                    while d != b'.'*8:
                        #update_status("LSPing:", d)
                        if d not in player_usernames:
                            players.add(slappyspatchy.entity.RenderedPlayer(d.decode('utf-8')))
                            player_usernames.append(d)
                        d = sock.recv(8)
                update_status("Beaming state to server")
                with slappyspatchy.network.new_sock() as sock:
                    sock.connect(HOST)
                    sock.send(b'SET')
                    sock.send(username)
                    sock.send(me.export_location())
                update_status("Fetching state from server")
                for player in players:
                    #if player is me: continue # optmisation and so on
                    with slappyspatchy.network.new_sock() as sock:
                        sock.connect(HOST)
                        sock.send(b'GET')
                        sock.send(player.username)
                        try:
                            player.update_location(sock.recv(slappyspatchy.network.ENTITY_POS_FRMT_LEN),
                                                   update_pos=player is not me, update_stats=True)
                        except slappyspatchy.entity.struct.error:
                            if player is me:
                                # probably means we're dead
                                setdead()
            except BrokenPipeError:
                print("\033[1mBROKEN PIPE\033[0m, skipping tick...", file=sys.stderr)
            except ConnectionResetError:
                print("\033[1mCONNECTION RESET\033[0m, skipping tick...", file=sys.stderr)
            if me.hp <= 0:
                setdead()
        elif event.type == pygame.QUIT:
            update_status("Quitting")
            run = 0
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = 0
            elif event.key == pygame.K_r:
                update_status("Respawning")
                # respawn
                me.kill()
                me = slappyspatchy.entity.RenderedPlayer(username.decode('utf-8'))
                players.add(me)
            elif event.key in {pygame.K_q, pygame.K_SPACE}:
                # send slap event
                slappyspatchy.send_event(username, 'slap', HOST)
    update_status("Rendering")
    scr.fill((0,0,0))
    me.update_keypresses(pygame.key.get_pressed(), pygame.key.get_mods())
    for player in players:
        player.update_pos(dt)
        scr.blit(player.surf, player.rect)
        player.render_nametag(scr)
        scr.blit(slappyspatchy.util.render_text("Health: "+str(me.hp)), (0,0))
        # render slapping hitbox
        pygame.draw.rect(scr, (255,25,250), player.slapping_hitbox, 1)
    pygame.display.flip()

pygame.quit()