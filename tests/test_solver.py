import unittest
from app.solver import get_feedback, filter_solutions
from app.models import GuessEntry

class TestWordleSolver(unittest.TestCase):
    def test_feedback_basic(self):
        self.assertEqual(get_feedback("apple", "apple"), ("green", "green", "green", "green", "green"))
        self.assertEqual(get_feedback("apple", "birth"), ("gray", "gray", "gray", "gray", "gray"))
        self.assertEqual(get_feedback("stone", "tonal"), ("gray", "yellow", "yellow", "yellow", "gray"))

    def test_feedback_duplicates(self):
        # Secret has 1 'e', guess has 2. Second 'e' should be gray.
        self.assertEqual(get_feedback("speed", "abide"), ("gray", "gray", "yellow", "gray", "yellow"))
        # Secret has 2 'e', guess has 2. Both should be yellow if not in correct position.
        self.assertEqual(get_feedback("speed", "erase"), ("yellow", "gray", "yellow", "yellow", "gray"))

    def test_filter_solutions(self):
        solutions = ["apple", "apply", "ample", "basic"]
        guesses = [
            GuessEntry(word="apply", feedback=["green", "green", "green", "green", "gray"])
        ]
        remaining = filter_solutions(solutions, guesses)
        self.assertEqual(remaining, ["apple"])

    def test_filter_solutions_no_match(self):
        solutions = ["apple", "apply"]
        # 'basic' vs 'apple' has a yellow 'a'. So all gray won't match.
        guesses = [
            GuessEntry(word="basic", feedback=["gray", "gray", "gray", "gray", "gray"])
        ]
        remaining = filter_solutions(solutions, guesses)
        self.assertEqual(remaining, [])

if __name__ == '__main__':
    unittest.main()
