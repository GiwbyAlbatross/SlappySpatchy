from typing import Union
from threading import Lock
from dataclasses import dataclass
from yaml import safe_load, dump

datafile_lock = Lock()

def load_info() -> dict:
    "Load the data file into memory"
    with datafile_lock:
        with open('data.yaml', encoding='utf-8') as f:
            d = safe_load(f.read())
    return d
def save_new_info(info: dict):
    "Probably don't use this."
    with datafile_lock:
        with open('data.yaml', 'wt', encoding='utf-8') as f:
            f.write(dump(info))

@dataclass
class Spatula:
    texName: str
    slapPower: Union[int, float]
    slapSpeed: Union[int, float]
    names: Union[list, tuple]

def load_spatula(spatulaId: str) -> Spatula:
    d = load_info()['spatulas'][spatulaId]
    return Spatula(d['texName'], d['slapPower'], d['slapSpeed'], d['names'])

def load_ranked_spatula(rank: int) -> Spatula:
    return load_spatula(load_info()['spatulaRanks'][rank])

def load_player_texturepack_names() -> list[str]:
    return load_info()['definedPlayers']
