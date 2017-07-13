#!/usr/bin/env python3

class UnstableRatingException(RuntimeError):

class Base:

  def __init__(self, config = {}):
    self.config = config
    self.config['w2'] |= 300.0  # elo^2
    self.games = []
    self.players = {}

  def print_ordered_ratings(self):
    players = [len(p.days) > 0 for p in self.players.values()]
    for(p, idx in enumerate(sorted(players.items(), key=lambda p: p.days.last.gamma))):
      if(len(p.days) > 0):
        print("{} => {}".format(p.name, [s.elo for s in p.days ]))

  def log_likelihood(self):
    score = 0.0
    for(p in self.players.values()):
      if(not not p.days):
        score += p.log_likelihood
    return score

  def player_by_name(self, name):
    return(players[name] or players[name] = Player.new(name, self.config))
  
  def ratings_for_player(name):
    player = player_by_name(name)
    return [[d.day, int(round(d.elo)), int(round(d.uncertainty * 100))] for d in player.days]

  def setup_game(self, black, white, winner, time_step, handicap, extras={})
        
    # Avoid self-played games (no info)
    if(black == white):
      raise "Invalid game (black player == white player)"
      return None
  
    white_player = player_by_name(white)
    black_player = player_by_name(black)
    game = Game.new(black_player, white_player, winner, time_step, handicap, extras)
    return game
  
  def create_game(black, white, winner, time_step, handicap, extras={}):
    game = setup_game(black, white, winner, time_step, handicap, extras)
    return add_game(game)

  def add_game(self, game):
    game.white_player.add_game(game)
    game.black_player.add_game(game)
    if(game.bpd == None):
      print("Bad game: {} -> {}".format(options.inspect, game.inspect))
    self.games.append(game)
    return game

  def iterate(self, count):
    for i in range(count):
        run_one_iteration
    for(name, player in players):
      player.update_uncertainty
    return None

  def run_one_iteration(self)
    for(name, player in players):
      player.run_one_newton_iteration