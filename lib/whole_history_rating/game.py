import math
import types

class Game:
  def __init__(self, black, white, winner, time_step, handicap, extras):
    self.day = time_step
    self.white_player = white
    self.black_player = black
    self.winner = winner
    self.extras = extras
    self.handicap = handicap or 0
    self.handicap_proc = (handicap if isinstance(handicap, (types.FunctionType, types.LambdaType)) else None)

  def opponents_adjusted_gamma(self, player):
    black_advantage = (self.handicap_proc(self) if self.handicap_proc else self.handicap)   
    #print("black_advantage = {}".format(black_advantage))

    if(player == white_player):
      opponent_elo = bpd.elo + black_advantage
    elif(player == black_player):
      opponent_elo = wpd.elo - black_advantage
    else:
      raise "No opponent for {}, since they're not in this game: {}.".format(player.inspect, self.inspect)
    rval = math.pow(10, (opponent_elo / 400.0))
    if(rval == 0 or math.isinf(rval) or math.isnan(rval)):
      raise UnstableRatingException("bad adjusted gamma: {}".format(inspect))

    return rval

  def opponent(self, player):
    if(player == white_player):
      return black_player
    elif(player == black_player):
      return white_player

  def prediction_score(self):
    if(white_win_probability() == 0.5):
      return 0.5
    else:
      if((winner == "W" and white_win_probability() > 0.5) or (winner == "B" and white_win_probability() < 0.5)):
        return 1.0
      else:
        return 0.0

  def inspect(self):
    return("{}: W:{}(r={}) B:{}(r={}) winner = {}, komi = {}, handicap = {}".format(self, white_player.name, wpd.r if wpd else '?', black_player.name, bpd.r if bpd else '?', winner, self.komi, self.handicap))

  #def likelihood(self):
  #  return(white_win_probability if winner == "W" else 1 - white_win_probability)

  # This is the Bradley-Terry Model
  def white_win_probability(self):
    return(wpd.gamma/(wpd.gamma + opponents_adjusted_gamma(white_player)))

  def black_win_probability(self):
    return(bpd.gamma/(bpd.gamma + opponents_adjusted_gamma(black_player)))
