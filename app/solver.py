import math
import random
from typing import List, Tuple, Dict
from collections import Counter
from app.models import GuessEntry, FeedbackType

def load_word_list(file_path: str) -> List[str]:
    with open(file_path, "r") as f:
        return [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]

SOLUTIONS = load_word_list("data/solutions.txt")
ALLOWED_GUESSES = load_word_list("data/allowed_guesses.txt")
ALL_WORDS = set(SOLUTIONS + ALLOWED_GUESSES)

# Top entropy-equivalent opening words (all score ~5.8 bits)
TOP_OPENERS = ["salet", "reast", "crate", "trace", "slate"]

def get_feedback(guess: str, secret: str) -> Tuple[FeedbackType, ...]:
    """Generates the feedback pattern for a guess against a secret word."""
    result: List[FeedbackType] = ["gray"] * 5
    secret_counts = Counter(secret)
    
    # First pass for greens
    for i in range(5):
        if guess[i] == secret[i]:
            result[i] = "green"
            secret_counts[secret[i]] -= 1
            
    # Second pass for yellows
    for i in range(5):
        if result[i] != "green" and secret_counts[guess[i]] > 0:
            result[i] = "yellow"
            secret_counts[guess[i]] -= 1
            
    return tuple(result)

def filter_solutions(solutions: List[str], guesses: List[GuessEntry]) -> List[str]:
    """Filters the list of solutions based on the feedback from guesses."""
    remaining = solutions
    for guess_entry in guesses:
        word = guess_entry.word.lower()
        pattern = tuple(guess_entry.feedback)
        remaining = [s for s in remaining if get_feedback(word, s) == pattern]
    return remaining

def calculate_entropy(guess: str, possible_solutions: List[str]) -> float:
    """Calculates the expected entropy of a guess against possible solutions."""
    if not possible_solutions:
        return 0.0
    
    patterns: Dict[Tuple[FeedbackType, ...], int] = {}
    total = len(possible_solutions)
    
    for solution in possible_solutions:
        pattern = get_feedback(guess, solution)
        patterns[pattern] = patterns.get(pattern, 0) + 1
        
    entropy = 0.0
    for count in patterns.values():
        p = count / total
        entropy -= p * math.log2(p)
        
    return entropy

def get_letter_frequency_score(word: str, remaining_solutions: List[str]) -> float:
    """Calculates a score based on how many unique characters in the word are in remaining solutions."""
    letter_counts = Counter("".join(remaining_solutions))
    unique_chars = set(word)
    score = sum(letter_counts.get(char, 0) for char in unique_chars)
    return float(score)

def get_suggestions(guesses: List[GuessEntry], top_n: int = 5) -> dict:
    """Provides separate solution and info-gain suggestions based on the board state."""
    remaining_solutions = filter_solutions(SOLUTIONS, guesses)
    remaining_set = set(remaining_solutions)
    
    if not remaining_solutions:
        return {"solutions": [], "info_gain": []}
        
    # First move optimization: pick a random top opener
    if not guesses:
        opener = random.choice(TOP_OPENERS)
        return {
            "solutions": [{"word": opener, "entropy": 5.836, "is_solution": True}],
            "info_gain": []
        }

    # Filter candidates to only include words consistent with all previous feedback
    consistent_candidates = filter_solutions(list(ALL_WORDS), guesses)
    
    if not consistent_candidates:
        consistent_candidates = list(ALL_WORDS)

    # If only a few solutions remain, suggest them directly.
    if len(remaining_solutions) <= top_n:
        return {
            "solutions": [
                {"word": s, "entropy": calculate_entropy(s, remaining_solutions), "is_solution": True}
                for s in sorted(remaining_solutions)
            ],
            "info_gain": []
        }

    scored_candidates = []
    THRESHOLD = 500 
    
    if len(remaining_solutions) > THRESHOLD:
        # Faster heuristic: Positional letter frequency
        positional_freq = [Counter() for _ in range(5)]
        overall_freq = Counter()
        for s in remaining_solutions:
            for i, char in enumerate(s):
                positional_freq[i][char] += 1
                overall_freq[char] += 1
        
        for word in consistent_candidates:
            score = 0
            seen_chars = set()
            for i, char in enumerate(word):
                if char not in seen_chars:
                    score += overall_freq[char]
                    seen_chars.add(char)
                score += positional_freq[i][char]
            
            if word in remaining_set:
                score *= 1.1 
            
            # Add random jitter for tie-breaking
            scored_candidates.append((word, score, random.random()))
        scored_candidates.sort(key=lambda x: (x[1], x[2]), reverse=True)
    else:
        # Full entropy calculation
        for word in consistent_candidates:
            entropy = calculate_entropy(word, remaining_solutions)
            is_sol = 1 if word in remaining_set else 0
            # Add random jitter for tie-breaking
            scored_candidates.append((word, entropy, is_sol, random.random()))
        scored_candidates.sort(key=lambda x: (x[1], x[2], x[3]), reverse=True)

    # Split into solutions and info-gain-only
    solution_results = []
    info_gain_results = []

    for entry in scored_candidates:
        word = entry[0]
        if len(remaining_solutions) > THRESHOLD:
            entropy_val = round(entry[1] / 1000.0, 3)
        else:
            entropy_val = round(entry[1], 3)

        item = {"word": word, "entropy": entropy_val, "is_solution": word in remaining_set}

        if word in remaining_set:
            if len(solution_results) < top_n:
                solution_results.append(item)
        else:
            if len(info_gain_results) < top_n:
                info_gain_results.append(item)

        if len(solution_results) >= top_n and len(info_gain_results) >= top_n:
            break

    return {"solutions": solution_results, "info_gain": info_gain_results}
