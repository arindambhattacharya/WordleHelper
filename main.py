from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.models import BoardState, Suggestion
from app.solver import get_suggestions
import os

app = FastAPI(title="Wordle Gemini Solver")

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    static_index = os.path.join("app/static", "index.html")
    if os.path.exists(static_index):
        with open(static_index, "r") as f:
            return f.read()
    return "<h1>Wordle Gemini Solver</h1><p>Static index.html not found.</p>"

@app.post("/suggest", response_model=list[Suggestion])
async def suggest(state: BoardState):
    try:
        suggestions = get_suggestions(state.guesses)
        if not suggestions and state.guesses:
            # Check if there are truly no solutions
            from app.solver import SOLUTIONS, filter_solutions
            remaining = filter_solutions(SOLUTIONS, state.guesses)
            if not remaining:
                raise HTTPException(status_code=400, detail="No possible words match this feedback.")
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
