#!/usr/bin/env python3
from whole_history_rating import player as pl
from whole_history_rating import game as match

class Base:

    def __init__(self, **kwargs):
        kwargs.setdefault('w2', 300.0) # elo^2
        self.options = kwargs
        self.games = []
        self.players = {}

    def print_ordered_ratings(self):
        players = [len(p.days) > 0 for p in self.players.values()]
        for p, idx in enumerate(sorted(players.items(), key=lambda p: p.days.last.gamma)):
            if len(p.days) > 0:
                print("{} => {}".format(p.name, [s.elo for s in p.days]))

    def log_likelihood(self):
        score = 0.0
        for p in self.players.values():
            if p.days:
                score += p.log_likelihood()
        return score

    def player_by_name(self, name):
        if not name in self.players:
            self.players[name] = pl.Player(name, self.options)
        return self.players[name]

    def ratings_for_player(self, name):
        player = self.player_by_name(name)
        return [[d.day, int(round(d.elo)), int(round(d.uncertainty * 100))] for d in player.days]

    def setup_game(self, black, white, winner, time_step, handicap, extras={}):
        # Avoid self-played games (no info)
        if black == white:
            raise "Invalid game (black player == white player)"
            return None

        white_player = self.player_by_name(white)
        black_player = self.player_by_name(black)
        game = match.Game(black_player, white_player, winner, time_step, handicap, extras)
        return game

    def create_game(self, black, white, winner, time_step, handicap, extras={}):
        game = self.setup_game(black, white, winner, time_step, handicap, extras)
        return self.add_game(game)

    def add_game(self, game):
        game.white_player.add_game(game)
        game.black_player.add_game(game)
        if game.bpd is None:
            print("Bad game: {} -> {}".format(repr(self.kwargs), game.inspect()))
        self.games.append(game)
        return game

    def iterate(self, count):
        for i in range(count):
            self.run_one_iteration()
        for name, player in self.players:
            player.update_uncertainty()
        return None

    def run_one_iteration(self):
        for name, player in self.players.items():
            player.run_one_newton_iteration()
