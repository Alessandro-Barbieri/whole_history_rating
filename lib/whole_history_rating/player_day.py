import math

class PlayerDay:
    def __init__(self, player, day):
        self.day = day
        self.name = None
        self.player = player
        self.is_first_day = False
        self.won_games = []
        self.lost_games = []
        self.won_game_terms_var = None
        self.lost_game_terms_var = None
        self.r = None
        self.uncertainty = None

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
        self.won_game_terms_var = None
        self.lost_game_terms_var = None

    def won_game_terms(self):
        if self.won_game_terms_var is None:
            self.won_game_terms_var = []
            for g in self.won_games:
                other_gamma = g.opponents_adjusted_gamma(self.player)
                if other_gamma == 0 or math.isnan(other_gamma) or math.isinf(other_gamma):
                    print("other_gamma ({}) = {}".format(g.opponent(self.player).inspect, other_gamma))
                self.won_game_terms_var.append([1.0, 0.0, 1.0, other_gamma])
                if self.is_first_day:
                    self.won_game_terms_var.append([1.0, 0.0, 1.0, 1.0])  # win against virtual player ranked with gamma = 1.0
        return self.won_game_terms_var

    def lost_game_terms(self):
        if self.lost_game_terms_var is None:
            self.lost_game_terms_var = []
            for g in self.lost_games:
                other_gamma = g.opponents_adjusted_gamma(self.player)
                if other_gamma == 0 or math.isnan(other_gamma) or math.isinf(other_gamma):
                    print("other_gamma ({}) = {}".format(g.opponent(self.player).inspect, other_gamma))
            self.lost_game_terms_var.append([0.0, other_gamma, 1.0, other_gamma])
            if self.is_first_day:
                self.lost_game_terms_var.append([0.0, 1.0, 1.0, 1.0])  # loss against virtual player ranked with gamma = 1.0
        return self.lost_game_terms_var

    def log_likelihood_second_derivative(self):
        mysum = 0.0
        for a, b, c, d in map(mysum, zip(self.won_game_terms(), self.lost_game_terms())):
            mysum += (c*d) / math.pow(c*self.gamma + d, 2)
        if math.isnan(self.gamma) or math.isnan(mysum):
            print("won_game_terms = {}".format(self.won_game_terms()))
            print("lost_game_terms = {}".format(self.lost_game_terms()))
        return -1 * self.gamma * mysum

    def log_likelihood_derivative(self):
        tally = 0.0
        for a, b, c, d in map(sum, zip(self.won_game_terms() + self.lost_game_terms())):
            tally += c / (c*self.gamma + d)
        return len(self.won_game_terms()) - self.gamma*tally

    def log_likelihood(self):
        tally = 0.0
        for a, b, c, d in self.won_game_terms():
            tally += math.log(a * self.gamma)
            tally -= math.log(c*self.gamma + d)
        for a, b, c, d in self.lost_game_terms():
            tally += math.log(b)
            tally -= math.log(c*self.gamma + d)
        return tally

    def add_game(self, game):
        if((game.winner == "W" and game.white_player == self.player) or
           (game.winner == "B" and game.black_player == self.player)):
            self.won_games.append(game)
        else:
            self.lost_games.append(game)

    def update_by_1d_newtons_method(self):
        dlogp = self.log_likelihood_derivative()
        d2logp = self.log_likelihood_second_derivative()
        dr = (self.log_likelihood_derivative() / self.log_likelihood_second_derivative())
        new_r = self.r - dr
        #new_r = max([0, self.r - dr])
        #print("({}) {} = {} - ({}/{})".format(
        #                                       player.name,
        #                                       new_r,
        #                                       self.r,
        #                                       self.log_likelihood_derivative(),
        #                                       self.log_likelihood_second_derivative()))
        self.r = new_r
