# Chess Game with AI

A web-based chess game with AI opponent powered by chess-api.com and move analysis powered by Gemini AI.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your Gemini API key:
     - `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. Run the application:
   ```bash
   python app.py
   ```

## Features

- Play chess against an AI opponent (powered by chess-api.com)
- Move analysis powered by Google's Gemini AI
- Visual feedback for moves, checks, and captures
- Game state tracking and validation
- Color selection for players

## APIs Used

- [chess-api.com](https://chess-api.com) - Free chess engine API for AI opponent moves
- [Google Gemini AI](https://makersuite.google.com/app/apikey) - For move analysis and strategic insights

## Security Note

The `.env` file containing your API keys is included in `.gitignore` and should never be committed to version control. Always keep your API keys private. 