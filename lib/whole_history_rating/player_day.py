import math

class PlayerDay:
  def __init__(self, player, day):
    self.day = day
    self.player = player
    self.is_first_day = false
    self.won_games = []
    self.lost_games = []

  @property
  def gamma(self):
    return math.exp(self.r)
  @gamma.setter
  def gamma(self, gamma):
    self.r = math.log(gamma)

  @property
  def elo(self):
    return (self.r*400.0) / (math.log(10))
  @elo.setter   
  def elo(self, elo):
    self.r = elo * (math.log(10)/400.0)
    
  def clear_game_terms_cache(self):
    self.won_game_terms = None
    self.lost_game_terms = None
  
  def won_game_terms(self):
    if self.won_game_terms is None:
      for g in self.won_games:
        other_gamma = g.opponents_adjusted_gamma(player)
        if (other_gamma == 0 or math.isnan(other_gamma) or math.isinf(other_gamma)):
          print("other_gamma ({}) = {}".format(repr(g.opponent(player)), other_gamma))
        self.won_game_terms.append([1.0, 0.0, 1.0, other_gamma])
        if is_first_day:
          self.won_game_terms.append([1.0, 0.0, 1.0, 1.0])  # win against virtual player ranked with gamma = 1.0
    return self.won_game_terms

  def lost_game_terms(self):
    if self.lost_game_terms is None:
      for g in self.lost_games.map:
        other_gamma = g.opponents_adjusted_gamma(player)
        if (other_gamma == 0 or math.isnan(other_gamma) or math.isinf(other_gamma)):
          print("other_gamma ({}) = {}".format(repr(g.opponent(player)), other_gamma))
      self.lost_game_terms.append([0.0, other_gamma, 1.0, other_gamma])
      if is_first_day:
        self.lost_game_terms.append([0.0, 1.0, 1.0, 1.0])  # loss against virtual player ranked with gamma = 1.0
    return lost_game_terms
  
  def log_likelihood_second_derivative(self):
    sum = 0.0
    for a, b, c, d in map(sum, zip(won_game_terms ,lost_game_terms)):
      sum += (c*d) / math.pow(c*gamma + d, 2))
    if (math.isnan(gamma) or math.isnan(sum)):
      print("won_game_terms = {}".format(won_game_terms))
      print("lost_game_terms = {}".format(lost_game_terms))
    return(-1 * gamma * sum)

  def log_likelihood_derivative(self):
    tally = 0.0
    for a, b, c, d in map(sum, zip(won_game_terms + lost_game_terms))
      tally += c / (c*gamma + d)
    return(len(won_game_terms) - gamma*tally)
  
  def log_likelihood(self):
    tally = 0.0
    for a, b, c, d in won_game_terms:
      tally += math.log(a * gamma)
      tally -= math.log(c*gamma + d)
    for i in lost_game_terms:
      tally += math.log(b)
      tally -= math.log(c*gamma + d)
    return tally

  def add_game(self, game):
    if ((game.winner == "W" and game.white_player == self.player) or
       (game.winner == "B" and game.black_player == self.player)):
      self.won_games.append(game)
    else:
      self.lost_games.append(game)

  def update_by_1d_newtons_method(self):
    dlogp = log_likelihood_derivative
    d2logp = log_likelihood_second_derivative
    dr = (log_likelihood_derivative / log_likelihood_second_derivative)
    new_r = self.r - dr
    #new_r = max([0, self.r - dr])
    #print("({}) {} = {} - ({}/{})".format(player.name,new_r,self.r,log_likelihood_derivative,log_likelihood_second_derivative))
    self.r = new_r
