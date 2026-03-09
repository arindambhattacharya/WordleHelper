from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.models import BoardState, SuggestionsResponse
from app.solver import get_suggestions
import os

app = FastAPI(title="Wordle Helper")

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    static_index = os.path.join("app/static", "index.html")
    if os.path.exists(static_index):
        with open(static_index, "r") as f:
            return f.read()
    return "<h1>Wordle Helper</h1><p>Static index.html not found.</p>"

@app.post("/suggest", response_model=SuggestionsResponse)
async def suggest(state: BoardState):
    try:
        result = get_suggestions(state.guesses)
        if not result["solutions"] and not result["info_gain"] and state.guesses:
            from app.solver import SOLUTIONS, filter_solutions
            remaining = filter_solutions(SOLUTIONS, state.guesses)
            if not remaining:
                raise HTTPException(status_code=400, detail="No possible words match this feedback.")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
