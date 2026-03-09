from app.solver import get_feedback, filter_solutions, SOLUTIONS
from app.models import GuessEntry

def test_repro():
    # Guess: SALET, S is yellow at index 0
    guesses = [
        GuessEntry(word="salet", feedback=["yellow", "gray", "gray", "gray", "gray"])
    ]
    
    remaining = filter_solutions(SOLUTIONS, guesses)
    
    # Check if any remaining words do NOT have 's'
    missing_s = [w for w in remaining if 's' not in w]
    print(f"Total remaining: {len(remaining)}")
    print(f"Words missing 's': {missing_s}")
    
    # Check if any remaining words have 's' at index 0
    s_at_0 = [w for w in remaining if w[0] == 's']
    print(f"Words with 's' at index 0: {s_at_0}")

    # Test another case: 'S' is green at index 0
    guesses_green = [
        GuessEntry(word="salet", feedback=["green", "gray", "gray", "gray", "gray"])
    ]
    remaining_green = filter_solutions(SOLUTIONS, guesses_green)
    not_s_at_0 = [w for w in remaining_green if w[0] != 's']
    print(f"Green test: Words NOT starting with 's': {not_s_at_0}")

if __name__ == "__main__":
    test_repro()
