document.addEventListener('DOMContentLoaded', () => {
    const board = document.getElementById('board');
    const suggestionsList = document.getElementById('suggestions-list');
    const resetBtn = document.getElementById('reset-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    let currentRow = 0;
    let currentCol = 0;
    const boardState = Array(6).fill(null).map(() => 
        Array(5).fill(null).map(() => ({ letter: '', feedback: 'gray' }))
    );

    // Initialize board
    function initBoard() {
        board.innerHTML = '';
        for (let r = 0; r < 6; r++) {
            const rowDiv = document.createElement('div');
            rowDiv.className = 'row';
            for (let c = 0; c < 5; c++) {
                const tile = document.createElement('div');
                tile.className = 'tile'; // Start empty with just a border
                tile.id = `tile-${r}-${c}`;
                tile.textContent = boardState[r][c].letter;
                
                tile.addEventListener('click', () => {
                    if (boardState[r][c].letter !== '') {
                        cycleColor(r, c);
                    }
                });
                
                rowDiv.appendChild(tile);
            }
            board.appendChild(rowDiv);
        }
        // Fetch initial precomputed suggestion
        updateSuggestions();
    }

    function cycleColor(r, c) {
        const states = ['gray', 'yellow', 'green'];
        let currentIndex = states.indexOf(boardState[r][c].feedback);
        let nextIndex = (currentIndex + 1) % states.length;
        let nextState = states[nextIndex];
        
        boardState[r][c].feedback = nextState;
        const tile = document.getElementById(`tile-${r}-${c}`);
        tile.className = `tile ${nextState}`;
        // Removed automatic updateSuggestions() here
    }

    async function updateSuggestions() {
        const guesses = [];
        // Only consider rows that are complete and confirmed
        for (let r = 0; r < 6; r++) {
            const word = boardState[r].map(t => t.letter).join('');
            // A row is considered "submitted" if it's below the current row OR complete
            if (word.length === 5 && (r < currentRow || (r === currentRow && currentCol === 5))) {
                guesses.push({
                    word: word,
                    feedback: boardState[r].map(t => t.feedback)
                });
            }
        }

        try {
            const response = await fetch('/suggest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ guesses })
            });
            
            if (response.ok) {
                const data = await response.json();
                renderSuggestions(data);
            } else {
                const error = await response.json();
                suggestionsList.innerHTML = `<p style="color: #ff4d4d">${error.detail}</p>`;
            }
        } catch (e) {
            console.error('Failed to fetch suggestions', e);
        }
    }

    function renderSuggestions(data) {
        const solutions = data.solutions || [];
        const infoGain = data.info_gain || [];

        if (solutions.length === 0 && infoGain.length === 0) {
            suggestionsList.innerHTML = '<p>No possible words match.</p>';
            return;
        }

        suggestionsList.innerHTML = '';

        if (solutions.length > 0) {
            const header = document.createElement('div');
            header.className = 'suggestion-section-header';
            header.textContent = 'Possible Solutions';
            suggestionsList.appendChild(header);
            solutions.forEach(s => {
                suggestionsList.appendChild(createSuggestionItem(s));
            });
        }

        if (infoGain.length > 0) {
            const header = document.createElement('div');
            header.className = 'suggestion-section-header';
            header.textContent = 'Info Gain Only';
            suggestionsList.appendChild(header);
            infoGain.forEach(s => {
                suggestionsList.appendChild(createSuggestionItem(s));
            });
        }
    }

    function createSuggestionItem(s) {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        const colorClass = s.is_solution ? '' : 'not-solution';

        item.innerHTML = `
            <div>
                <span class="suggestion-word ${colorClass}">${s.word}</span>
            </div>
            <span class="suggestion-entropy">${s.entropy.toFixed(2)}</span>
        `;
        item.addEventListener('click', () => fillCurrentRow(s.word));
        return item;
    }

    function fillCurrentRow(word) {
        if (currentRow >= 6) return;
        for (let i = 0; i < 5; i++) {
            boardState[currentRow][i].letter = word[i];
            const tile = document.getElementById(`tile-${currentRow}-${i}`);
            tile.textContent = word[i];
            tile.className = 'tile typing';
            boardState[currentRow][i].feedback = 'gray';
        }
        currentCol = 5;
    }

    function submitGuess() {
        // Finalize visual state of the current row if it has letters
        for (let i = 0; i < 5; i++) {
            const tile = document.getElementById(`tile-${currentRow}-${i}`);
            if (tile && tile.textContent !== '' && tile.classList.contains('typing')) {
                tile.className = 'tile gray';
            }
        }
        
        // Always update suggestions based on all complete rows
        updateSuggestions();
        
        // Only advance to the next row if the current one is full
        if (currentCol === 5 && currentRow < 5) {
            currentRow++;
            currentCol = 0;
        }
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            submitGuess();
        } else if (e.key === 'Backspace') {
            if (currentCol > 0) {
                currentCol--;
                boardState[currentRow][currentCol].letter = '';
                boardState[currentRow][currentCol].feedback = 'gray';
                const tile = document.getElementById(`tile-${currentRow}-${currentCol}`);
                tile.textContent = '';
                tile.className = 'tile';
            }
        } else if (/^[a-zA-Z]$/.test(e.key)) {
            if (currentCol < 5) {
                const letter = e.key.toLowerCase();
                boardState[currentRow][currentCol].letter = letter;
                const tile = document.getElementById(`tile-${currentRow}-${currentCol}`);
                tile.textContent = letter;
                tile.className = 'tile typing';
                currentCol++;
            }
        }
    });

    submitBtn.addEventListener('click', submitGuess);

    resetBtn.addEventListener('click', () => {
        currentRow = 0;
        currentCol = 0;
        for (let r = 0; r < 6; r++) {
            for (let c = 0; c < 5; c++) {
                boardState[r][c] = { letter: '', feedback: 'gray' };
            }
        }
        initBoard();
    });

    initBoard();
});
