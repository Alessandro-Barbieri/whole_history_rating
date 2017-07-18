import math
import types
from whole_history_rating import player as pl
from whole_history_rating import player_day as pd

class Game:
    def __init__(self, black, white, winner, time_step, handicap, extras):
        self.day = time_step
        self.white_player = white
        self.black_player = black
        self.winner = winner
        self.bpd = None
        self.wpd = None
        self.winner = None
        self.extras = extras
        self.handicap = handicap or 0
        self.handicap_proc = (handicap if
                              isinstance(handicap,
                                         (types.FunctionType,
                                          types.LambdaType))
                              else None)

    def opponents_adjusted_gamma(self, player):
        black_advantage = (self.handicap_proc(self)
                           if self.handicap_proc
                           else self.handicap)
        #print("black_advantage = {}".format(black_advantage))

        if player == self.white_player:
            opponent_elo = self.bpd.elo + black_advantage
        elif player == self.black_player:
            opponent_elo = self.wpd.elo - black_advantage
        else:
            raise "No opponent for {}, since they're not in this game: {}.".format(player.inspect(), self.inspect())
        rval = math.pow(10, (opponent_elo / 400.0))
        if rval == 0 or math.isinf(rval) or math.isnan(rval):
            raise pl.UnstableRatingException("bad adjusted gamma: {}".format(self.inspect()))

        return rval

    def opponent(self, player):
        if player == self.white_player:
            return self.black_player
        elif player == self.black_player:
            return self.white_player

    def prediction_score(self):
        if self.white_win_probability() == 0.5:
            return 0.5
        else:
            if (self.winner == "W" and self.white_win_probability() > 0.5) \
            or (self.winner == "B" and self.white_win_probability() < 0.5):
                return 1.0
            else:
                return 0.0

    def inspect(self):
        return("{}: W:{}(r={}) B:{}(r={}) winner = {}, komi = {}, handicap = {}".format(
            self,
            self.white_player.name,
            self.wpd.r if self.wpd else '?',
            self.black_player.name,
            self.bpd.r if self.bpd else '?',
            self.winner,
            self.komi,
            self.handicap))

    #def likelihood(self):
        #return(white_win_probability
        #       if self.winner == "W"
        #       else 1 - self.white_win_probability)

    #This is the Bradley-Terry Model
    def white_win_probability(self):
        return self.wpd.gamma / (self.wpd.gamma + self.opponents_adjusted_gamma(self.white_player))

    def black_win_probability(self):
        return self.bpd.gamma / (self.bpd.gamma + self.opponents_adjusted_gamma(self.black_player))