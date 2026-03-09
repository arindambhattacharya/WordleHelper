# Wordle Helper

A mathematically optimal Wordle assistant that uses Information Theory (Entropy Maximization) to suggest the best possible guesses.

![Wordle Helper Screenshot](Screenshot%202026-03-09%20at%2019.15.58.png)

## Overview

Wordle Helper is a fast, lightweight web application designed to help you solve Wordle puzzles in the fewest steps possible. It combines a high-performance Python backend (FastAPI) with a sleek, responsive vanilla JavaScript frontend.

## Features

- **Entropy-Based Suggestions:** Calculates the "Expected Information Gain" for every valid word to identify the most efficient guess.
- **Hybrid Strategy:** Uses fast letter-frequency heuristics for large search spaces and switches to exhaustive entropy calculations when they are most effective.
- **Interactive Grid:** A familiar Wordle-like interface where you can input words and toggle tile colors (Gray, Yellow, Green) to match your game state.
- **Real-time Filtering:** Automatically narrows down the pool of ~13,000 valid words as you provide feedback.
- **Precomputed Openers:** Instant optimal starting words to get you going immediately.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** Vanilla HTML5, CSS3, and JavaScript (ES6+)
- **Solver Logic:** Information Theory / Entropy Maximization
- **Package Manager:** [uv](https://github.com/astral-sh/uv)

## Getting Started

### Prerequisites

- Python 3.10+
- `uv` (recommended) or `pip`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/WordleHelper.git
    cd WordleHelper
    ```

2.  **Install dependencies:**
    Using `uv`:
    ```bash
    uv sync
    ```
    Using `pip`:
    ```bash
    pip install -e .
    ```

### Running the Application

1.  **Start the FastAPI server:**
    ```bash
    uv run python main.py
    ```
    or
    ```bash
    python main.py
    ```

2.  **Open your browser:**
    Navigate to `http://127.0.0.1:8000` to start solving!

## Usage

1.  Enter the word you guessed in the first row.
2.  Click on the tiles to change their colors based on the feedback from the actual Wordle game:
    - **Gray:** Letter is not in the word.
    - **Yellow:** Letter is in the word but in the wrong position.
    - **Green:** Letter is in the correct position.
3.  The solver will automatically suggest the top 5 next best words.
4.  Pick a suggestion and repeat until you win!

## Project Structure

- `main.py`: Entry point and FastAPI application setup.
- `app/`:
    - `solver.py`: Core logic for entropy calculation and word filtering.
    - `models.py`: API request/response models.
    - `static/`: Frontend assets (HTML, CSS, JS).
- `data/`: Word lists (solutions and valid guesses).
- `DESIGN.md`: Detailed architecture and design documentation.
- `SPECIFICATION.md`: Detailed functional requirements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
