import math
import sys
from numpy import matrix, empty
from whole_history_rating import player_day as pd

class UnstableRatingException(Exception):
    pass

class Player:
    def __init__(self, name, **kwargs):
        self.name = name
        self.debug = kwargs.get['debug', 'None']
        self.w2 = math.pow((math.sqrt(kwargs.get['w2']) * math.log(10) / 400), 2)  # Convert from elo^2 to r^2
        self.days = []
        self.id = None

    def inspect(self):
        return "{}:({})".format(self, self.name)

    def log_likelihood(self):
        mysum = 0.0
        sigma2 = self.compute_sigma2()
        n = len(self.days)
        for i in range(0, n - 1):
            prior = 0
            if i < (n - 1):
                rd = self.days[i].r - self.days[i + 1].r
                prior += (1/(math.sqrt(2*math.pi*sigma2[i]))) * math.exp(-(math.pow(rd, 2))/2*sigma2[i])
            if i > 0:
                rd = self.days[i].r - self.days[i - 1].r
                prior += (1/(math.sqrt(2*math.pi*sigma2[i - 1]))) * math.exp(-(math.pow(rd, 2)/2*sigma2[i - 1]))
            if prior == 0:
                mysum += self.days[i].log_likelihood()
            else:
                if math.isinf(self.days[i].log_likelihood()) or math.isinf(math.log(prior)):
                    print("Infinity at {}: {} + {}: prior = {}, days = {}".format(self.inspect(),
                                                                                  self.days[i].log_likelihood,
                                                                                  math.log(prior),
                                                                                  prior,
                                                                                  repr(self.days)))
                    sys.exit()
            mysum += self.days[i].log_likelihood() + math.log(prior)
        return mysum

    def hessian(days, sigma2):
        n = len(days)
        x = empty([n, n])
        for row in range(n):
            for col in range(n):
                if row == col:
                    prior = 0
                if row < (n - 1):
                    prior += -1.0 / sigma2[row]
                if row > 0:
                    prior += -1.0 / sigma2[row - 1]
                    x = days[row].log_likelihood_second_derivative() + prior - 0.001
                elif row == col-1:
                    x[row][col] = 1.0 / sigma2[row]
                elif row == col+1:
                    x[row][col] = 1.0 / sigma2[col]
                else:
                    x[row][col] = 0
        return matrix(x)

    def gradient(self, r, days, sigma2):
        g = []
        n = len(days)
        for day, idx in enumerate(days):
            prior = 0
            if idx < (n - 1):
                prior += -(r[idx] - r[idx + 1])/sigma2[idx]
            if idx > 0:
                prior += -(r[idx] - r[idx - 1])/sigma2[idx - 1]
            if self.debug:
                print("g[{}] = {} + {}".format(idx, day.log_likelihood_derivative(), prior))
            g.append(day.log_likelihood_derivative() + prior)
        return g

    def run_one_newton_iteration(self):
        for day in self.days:
            day.clear_game_terms_cache()
        if len(self.days) == 1:
            self.days[0].update_by_1d_newtons_method()
        elif len(self.days) > 1:
            self.update_by_ndim_newton()

    #shameless copied from https://stackoverflow.com/a/12879942
    #https://stackoverflow.com/questions/5878403/python-equivalent-to-rubys-each-cons?rq=1
    def each_cons(xs, n):
        return zip(*(xs[i:] for i in range(n)))

    def compute_sigma2(self):
        sigma2 = []
        for d1, d2 in self.each_cons(self.days, 2):
            sigma2.append(abs((d2.day - d1.day))*self.w2)
        return sigma2

    def update_by_ndim_newton(self):
        # r
        r = [s.r for s in self.days]
        if self.debug:
            print("Updating {}".format(self.inspect))
            for day in self.days:
                print("day[{}] r = {}".format(day.day, day.r))
                print("day[{}] win terms = {}".format(day.day, day.won_game_terms()))
                print("day[{}] win games = {}".format(day.day, day.won_games))
                print("day[{}] lose terms = {}".format(day.day, day.lost_game_terms()))
                print("day[{}] lost games = {}".format(day.day, day.lost_games))
                print("day[{}] log(p) = {}".format(day.day, day.log_likelihood()))
                print("day[{}] dlp = {}".format(day.day, day.log_likelihood_derivative()))
                print("day[{}] dlp2 = {}".format(day.day, day.log_likelihood_second_derivative()))

        # sigma squared (used in the prior)
        sigma2 = self.compute_sigma2()

        h = self.hessian(self.days, sigma2)
        g = self.gradient(r, self.days, sigma2)

        a = []
        d = [h[0, 0]]
        b = [h[0, 1]]

        n = len(r)
        for i in range(1, n - 1):
            a[i] = h[i, i - 1] / d[i - 1]
            d[i] = h[i, i] - a[i]*b[i - 1]
            b[i] = h[i, i + 1]

        y = [g[0]]
        for i in range(1, n - 1):
            y[i] = g[i] - a[i]*y[i - 1]

        x = []
        x[n - 1] = y[n - 1] / d[n - 1]
        for i in range(n - 2, 0, -1):
            x[i] = (y[i] - b[i]*x[i + 1])/d[i]

        new_r = [ri - xi for ri, xi in zip(r, x)]

        for r in new_r:
            if r > 650:
                raise UnstableRatingException("Unstable r ({}) on player {}".format(new_r, self.inspect()))

        if self.debug:
            print("Hessian = {}").format(h)
            print("gradient = {}").format(g)
            print("a = {}").format(a)
            print("d = {}").format(d)
            print("b = {}").format(b)
            print("y = {}").format(y)
            print("x = {}").format(x)
            print("{} ({}) => ({})").format(self.inspect(), r, new_r)

        for day, idx in enumerate(self.days):
            day.r = day.r - x[idx]

    def covariance(self):
        r = [s.r for s in self.days]

        sigma2 = self.compute_sigma2()
        h = self.hessian(self.days, sigma2)
        g = self.gradient(r, self.days, sigma2)

        n = len(self.days)

        a = []
        d = [h[0, 0]]
        b = [h[0, 1]]

        n = len(r)
        for i in range(1, n - 1):
            a[i] = h[i, i - 1] / d[i - 1]
            d[i] = h[i, i] - a[i]*b[i - 1]
            b[i] = h[i, i + 1]

        dp = []
        dp[n - 1] = h[n - 1, n - 1]
        bp = []
        bp[n - 1] = h[n - 1, n - 2]
        ap = []
        for i in range(n - 2, 0, -1):
            ap[i] = h[i, i + 1] / dp[i + 1]
            dp[i] = h[i, i] - ap[i]*bp[i + 1]
            bp[i] = h[i, i - 1]

        v = []
        for i in range(0, n - 2):
            v[i] = dp[i + 1]/(b[i]*bp[i + 1] - d[i]*dp[i + 1])
        v[n - 1] = -1 / d[n - 1]

        #print("a = {}").format(a)
        #print("b = {}").format(b)
        #print("bp = {}").format(bp)
        #print("d = {}").format(d)
        #print("dp = {}").format(dp)
        #print("v = {}").format(v)

        x = empty([n, n])
        for row in range(n):
            for col in range(n):
                if row == col:
                    x[row][col] = v[row]
                elif row == col-1:
                    x[row][col] = -1 * a[col] * v[col]
                else:
                    x[row][col] = 0
        return matrix(x)

    def update_uncertainty(self):
        if len(self.days) > 0:
            c = self.covariance()
            u = [c[i, i] for i in range(0, len(self.days) - 1)] # u = variance
            for d, u in zip(self.days, u):
                d.uncertainty = u
        else:
            return 5

    def add_game(self, game):
        if not self.days[-1:] or self.days[-1].day != game.day:
            new_pday = pd.PlayerDay(self, game.day)
        if not self.days:
            new_pday.is_first_day = True
            new_pday.gamma = 1
        else:
            new_pday.gamma = self.days[-1].gamma
        self.days.append(new_pday)
        if game.white_player == self:
            game.wpd = self.days[-1]
        else:
            game.bpd = self.days[-1]
        self.days[-1].add_game(game)