import math
from typing import List, Tuple, Dict, Set
from collections import Counter
from app.models import GuessEntry, FeedbackType

def load_word_list(file_path: str) -> List[str]:
    with open(file_path, "r") as f:
        return [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]

SOLUTIONS = load_word_list("data/solutions.txt")
ALLOWED_GUESSES = load_word_list("data/allowed_guesses.txt")
ALL_WORDS = set(SOLUTIONS + ALLOWED_GUESSES)

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

def get_suggestions(guesses: List[GuessEntry], top_n: int = 5) -> List[dict]:
    """Provides the top N suggestions based on the board state."""
    remaining_solutions = filter_solutions(SOLUTIONS, guesses)
    
    if not remaining_solutions:
        return []
        
    # First move optimization
    if not guesses:
        return [{"word": "salet", "entropy": 5.836, "is_solution": True}]

    # Filter candidates to only include words consistent with all previous feedback
    # This ensures suggestions "respect the yellow/green/gray colors".
    consistent_candidates = filter_solutions(list(ALL_WORDS), guesses)
    
    # If no consistent candidates found (shouldn't happen with valid feedback), 
    # fall back to all words to avoid returning nothing.
    if not consistent_candidates:
        consistent_candidates = list(ALL_WORDS)

    # If only a few solutions remain, suggest them directly.
    if len(remaining_solutions) <= top_n:
        return [
            {"word": s, "entropy": calculate_entropy(s, remaining_solutions), "is_solution": True}
            for s in sorted(remaining_solutions)
        ]

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
            
            if word in remaining_solutions:
                score *= 1.1 
            
            scored_candidates.append((word, score))
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
    else:
        # Full entropy calculation
        for word in consistent_candidates:
            entropy = calculate_entropy(word, remaining_solutions)
            is_sol = 1 if word in remaining_solutions else 0
            scored_candidates.append((word, (entropy, is_sol)))
        scored_candidates.sort(key=lambda x: (x[1][0], x[1][1]), reverse=True)

    top_results = scored_candidates[:top_n]
    
    return [
        {
            "word": word, 
            "entropy": round(score[0] if isinstance(score, tuple) else score / 1000.0, 3), 
            "is_solution": word in remaining_solutions
        }
        for word, score in top_results
    ]
