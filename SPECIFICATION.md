# Wordle Gemini Solver: Design Specification

## 1. Architecture Refinement

The system is a decoupled Client-Server application.

- **Frontend:** A single-page application (SPA) using standard web technologies.
- **Backend:** A FastAPI server providing a stateless REST API.
- **Data Layer:** Flat text files containing the Wordle word lists.

### Interaction Flow
1. User enters a 5-letter word in the UI.
2. User clicks tiles to set colors (Gray, Yellow, Green).
3. User clicks the **"Submit Guess"** button or presses **Enter**.
4. The system updates suggestions based on all completed rows (even if previously submitted).
5. If the current row is newly completed (5 letters), the system advances to the next row.
6. The user can modify colors in *any* previous row and click "Submit Guess" to refresh suggestions based on the updated feedback.

## 2. Data Models

### 2.1 Backend Models (Pydantic)

```python
from pydantic import BaseModel
from typing import List, Literal

FeedbackType = Literal["gray", "yellow", "green"]

class GuessEntry(BaseModel):
    word: str  # Must be 5 characters
    feedback: List[FeedbackType]  # Must have length 5

class BoardState(BaseModel):
    guesses: List[GuessEntry]

class Suggestion(BaseModel):
    word: str
    entropy: float
    is_solution: bool  # True if word is in the common target list
```

### 2.2 Internal Data Structures
- `ALL_WORDS`: Set of ~12,972 valid guess words.
- `COMMON_WORDS`: List of ~2,315 possible solution words.
- `PATTERN_MATRIX`: (Optional Optimization) A precomputed or cached matrix of feedback patterns for every word pair.

## 3. API & Interface Definitions

### 3.1 Endpoints

#### `POST /suggest`
- **Request Body:** `BoardState`
- **Response Body:** `List[Suggestion]`
- **Status Codes:**
    - `200 OK`: Success.
    - `422 Unprocessable Entity`: Invalid input (e.g., word length != 5).
    - `400 Bad Request`: Inconsistent feedback resulting in zero possible words.

#### `GET /`
- Serves the static `index.html`.

## 4. Algorithmic Logic

### 4.1 Filtering Logic
The solver uses standard Wordle feedback rules to determine if a candidate word is consistent with previous guesses.
- **Rule:** A candidate word `s` is consistent with guess `g` and feedback `f` if and only if `get_feedback(g, s) == f`.
- **Duplicate Letters:** The filtering correctly handles duplicate letters in both the guess and the secret word (e.g., if a secret has one 'E' and a guess has two, only one 'E' will be colored yellow/green).
- **Suggestion Consistency:** All suggestions (including those labeled "Info Gain Only") are strictly consistent with all known clues (green, yellow, and gray).

### 4.2 Feedback Pattern Generation
Function `get_feedback(guess, secret)` returns a 5-tuple of colors.
- Priority: Green > Yellow > Gray.
- Correctly handle multiple occurrences of the same letter.

### 4.3 Entropy Calculation
For each potential guess $g \in ALL\_WORDS$:
1. For every possible remaining solution $s \in REMAINING\_SOLUTIONS$:
    - Calculate the feedback pattern $p = get\_feedback(g, s)$.
2. Group solutions by their patterns and calculate the probability $P(p)$ of each pattern occurring.
3. Entropy $H(g) = \sum P(p) \cdot \log_2(1/P(p))$.

### 4.4 Hybrid Strategy
- **Base Case**: If `len(REMAINING_SOLUTIONS) <= top_n`, suggest the remaining solutions directly.
- **Heuristic Phase**: If `len(REMAINING_SOLUTIONS) > 500`:
    - Use **Positional Letter Frequency**.
    - Calculate frequency of each letter at each position (0-4) across remaining solutions.
    - Score guesses by sum of positional frequencies + overall frequency for unique characters.
    - Apply a 1.1x multiplier for candidates that are also potential solutions.
- **Entropy Phase**: If `len(REMAINING_SOLUTIONS) <= 500`:
    - Calculate full Shannon Entropy for all valid guess words.
    - Use `is_solution` as a secondary sort key for tie-breaking.
- **First Move**: Hardcoded to "SALET" for instant response.

## 5. Implementation Decisions

- **FastAPI:** Chosen for its native support for Pydantic models and asynchronous capabilities.
- **Vanilla JS:** The UI state is small enough that a framework like React adds unnecessary complexity.
- **Tile States:** 
    - `typing`: Transparent with light border for entered characters.
    - `gray/yellow/green`: Filled backgrounds for confirmed feedback.
- **Suggestion Labeling:** UI explicitly labels words as "Possible Solution" or "Info Gain Only" to help user decision-making.
- **Component-based CSS:** Use Flexbox/Grid for the Wordle board to ensure responsiveness.


## 6. Error Handling & Security

- **Client Side:** Prevent submission of incomplete words or missing colors.
- **Server Side:** 
    - Validate word lengths and character sets (A-Z only).
    - Handle cases where the user provides contradictory feedback (e.g., "A" is green at index 0 and gray elsewhere, but the word actually has two "A"s).
- **Security:** Since it's a local tool, standard CSRF protection is sufficient. No sensitive data is stored.

## 7. Test Cases

### 7.1 Unit Tests (Backend)
- `test_filtering`: Verify that words are correctly excluded based on feedback.
- `test_feedback_generation`: Test complex cases like "ABBA" vs "AABC".
- `test_entropy_math`: Verify entropy for a known small word set.
- `test_heuristic`: Ensure the frequency heuristic ranks "stronger" words higher.

### 7.2 Integration Tests
- `test_suggest_endpoint`: Mock a board state and verify the API returns valid JSON.
- `test_empty_state`: Ensure the API returns the hardcoded first guess for an empty board.

### 7.3 UI Tests
- Verify tile color cycling (Gray -> Yellow -> Green -> Gray).
- Verify board state is correctly serialized to JSON for the API call.
