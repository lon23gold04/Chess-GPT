# Chess Game with AI

A web-based chess game with AI opponent powered by chess-api.com and move analysis powered by Gemini AI.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variable:
   ```bash
   # Add this to your ~/.bashrc or ~/.zshrc for persistence
   export GEMINI_API_KEY='your_gemini_api_key_here'
   
   # Or set it temporarily for the current session
   export GEMINI_API_KEY='your_gemini_api_key_here'
   ```
   
   Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

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

Keep your API keys private and never commit them to version control. Using environment variables helps keep sensitive information secure. 