#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  untitled.py
#  
#  Copyright 2024  <giwby@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR ANY PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details. If you can find one :)
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
# 

from typing import Union
import contextlib
import argparse
import pygame
import slappyspatchy.game
import stuuf

class GameRunner(contextlib.AbstractContextManager):
    game: slappyspatchy.game.Game
    flags: stuuf.Flags
    scr: pygame.Surface
    def __init__(self,
                 game: slappyspatchy.game.Game,
                 scr_size: tuple[int, int],
                 flags: stuuf.Flags={
                     '...':...
                 },
        ):
        self.game = game
        if 'do_debug' not in flags: flags['do_debug'] = False
        if 'displayflags' not in flags: flags['displayflags'] = 0
        self.flags= stuuf.Flags(**flags, running=False, scr_size=scr_size)
        #self.settings = settings
        self.game.set_data(self.flags)
    def init(self):
        pygame.init()
        self.flags.clock = pygame.time.Clock()
        self.scr = pygame.display.set_mode(self.flags.scr_size, self.flags.displayflags)
        self.game.init(self.scr)
        self.flags.running = True
    def cleanup(self):
        self.game.cleanup()
        pygame.quit()
    def mainloop(self):
        fps = self.flags.target_fps
        debug = self.flags.do_debug and __debug__
        frames = 0
        while self.flags['running']:
            # do self.game's running loop stuff
            dt = self.flags['clock'].tick(fps)
            if debug and (frames % 20) == 0:
                print(
                    "FPS: %02f" % (
                        self.flags['clock'].get_fps()
                    ), end='\r')
            self.game.process_events(pygame.event.get())
            self.game.on_frame(dt / 1000, debug=debug) # supply dt in seconds not ms
            pygame.display.flip()
            frames += 1
    def __exit__(self, *exc):
        self.cleanup()
        return False
    def __del__(self):
        self.cleanup()
        del self.game

if __name__ == '__main__':
    runner = GameRunner(slappyspatchy.game.Game(), (1024,768), stuuf.Flags())
    runner.init()
    # yaassssssssssss homemade context manager :)
    with runner:
        runner.mainloop()
        runner.cleanup()
