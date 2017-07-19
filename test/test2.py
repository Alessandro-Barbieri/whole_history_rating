import sys,os,os.path
import unittest

sys.path.append(os.path.expanduser('../lib/'))

from whole_history_rating import base
from whole_history_rating import player as pl

whr = base.Base()

for game in range(1, 10):
    whr.create_game("anchor", "player", "B", 1, 0)
    whr.create_game("anchor", "player", "W", 1, 0)
    for game in range(1, 10):
        whr.create_game("anchor", "player", "B", 180, 600)
        whr.create_game("anchor", "player", "W", 180, 600)
    try:
        whr.iterate(10)
    except pl.UnstableRatingException:
        print('errore')
