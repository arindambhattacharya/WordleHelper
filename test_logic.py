from app.solver import get_feedback, filter_solutions
from app.models import GuessEntry

def test_yellow():
    solutions = ["abbey", "babes", "basic"]
    # If guess is 'abbey' and feedback is 'yellow' at index 0, 
    # then secret must contain 'a' but not at index 0.
    # 'babes' has 'a' at index 1.
    # 'basic' has 'a' at index 1.
    guesses = [
        GuessEntry(word="abbey", feedback=["yellow", "green", "green", "green", "gray"])
    ]
    # Feedback for 'abbey' against 'babes' is:
    # green: b at 2, e at 3 -> gray, gray, green, green, gray
    # yellow pass: a at 0 -> yellow.
    # result: (yellow, gray, green, green, gray)
    # Wait, 'abbey' has 'b' at 1 and 2. 'babes' has 'b' at 0 and 2.
    # Green at 2. 
    # Yellow at 0 (a).
    # Remaining: 'b' at 1 (abbey) vs 'b' at 0 (babes).
    # So index 1 is yellow.
    # result: (yellow, yellow, green, green, gray)
    
    print(f"Feedback for abbey vs babes: {get_feedback('abbey', 'babes')}")
    print(f"Feedback for abbey vs basic: {get_feedback('abbey', 'basic')}")
    
    filtered = filter_solutions(solutions, guesses)
    print(f"Filtered: {filtered}")

if __name__ == "__main__":
    test_yellow()
