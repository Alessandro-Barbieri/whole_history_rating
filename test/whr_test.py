import sys,os,os.path

sys.path.append(os.path.expanduser('../lib/'))

import unittest
from whole_history_rating import base

class WholeHistoryRatingTest(unittest.TestCase):
  def setUp(self):
    self.whr = base.Base()
    return self.whr

  def setup_game_with_elo(self, white_elo, black_elo, handicap):
    game = self.whr.create_game("black", "white", "W", 1, handicap)
    game.black_player.days[0].elo = black_elo
    game.white_player.days[0].elo = white_elo
    return game

  def test_even_game_between_equal_strength_players_should_have_white_winrate_of_50_percent(self):
    game = self.setup_game_with_elo(500, 500, 0)
    return self.assertAlmostEqual(0.5, game.white_win_probability, delta=0.0001)

  def test_handicap_should_confer_advantage(self):
    game = self.setup_game_with_elo(500, 500, 1)
    return self.assertGreater(game.black_win_probability, 0.5)

  def test_higher_rank_should_confer_advantage(self):
    game = self.setup_game_with_elo(600, 500, 0)
    return self.assertGreater(game.white_win_probability, 0.5)

  def test_winrates_are_equal_for_same_elo_delta(self):
    game = self.setup_game_with_elo(100, 200, 0)
    game2 = self.setup_game_with_elo(200, 300, 0)
    return self.assertAlmostEqual(game.white_win_probability, game2.white_win_probability, delta=0.0001)

  def test_winrates_for_twice_as_strong_player(self):
    game = self.setup_game_with_elo(100, 200, 0)
    return self.assertAlmostEqual(0.359935, game.white_win_probability, delta=0.001)

  def test_winrates_should_be_inversely_proportional_with_unequal_ranks(self):
    game = self.setup_game_with_elo(600, 500, 0)
    return self.assertAlmostEqual(game.white_win_probability, 1 - game.black_win_probability, delta=0.0001)
  
  def test_winrates_should_be_inversely_proportional_with_handicap(self):
    game = self.setup_game_with_elo(500, 500, 4)
    return self.assertAlmostEqual(game.white_win_probability, 1 - game.black_win_probability, delta=0.0001)
    
  def test_output(self):
    self.whr.create_game("shusaku", "shusai", "B", 1, 0)
    self.whr.create_game("shusaku", "shusai", "W", 2, 0)
    self.whr.create_game("shusaku", "shusai", "W", 3, 0)
    self.whr.create_game("shusaku", "shusai", "W", 4, 0)
    self.whr.create_game("shusaku", "shusai", "W", 4, 0)
    self.whr.iterate(50)
    self.assertListEqual([[1, -92, 71], [2, -94, 71], [3, -95, 71], [4, -96, 72]], self.whr.ratings_for_player("shusaku"))
    self.assertListEqual([[1, 92, 71], [2, 94, 71], [3, 95, 71], [4, 96, 72]], self.whr.ratings_for_player("shusai"))
  
  def test_unstable_exception_raised_in_certain_cases(self):
    for game in range(1, 10):
       self.whr.create_game("anchor", "player", "B", 1, 0)
       self.whr.create_game("anchor", "player", "W", 1, 0)
    for game in range(1, 10):
       self.whr.create_game("anchor", "player", "B", 180, 600)
       self.whr.create_game("anchor", "player", "W", 180, 600)
    with self.assertRaises(base.UnstableRatingException):
      self.whr.iterate(10)
