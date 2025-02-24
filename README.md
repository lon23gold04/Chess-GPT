# Chess GPT

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/EN10/Chess)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

An elegant web-based chess application featuring an AI opponent and real-time move analysis powered by Google's Gemini AI. Play against a strong chess engine while receiving strategic insights about your moves.

<div align="center">
  <img src="https://raw.githubusercontent.com/EN10/Chess/main/screenshot.png" width="400" alt="Chess Game Screenshot">
</div>

## Table of Contents
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [How to Play](#how-to-play)
- [Technical Details](#technical-details)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Key Features

### Chess Gameplay
- Play as White or Black against a sophisticated AI opponent
- Intuitive drag-and-drop or click-based piece movement
- Real-time move validation with legal move checking
- Visual feedback for selected pieces and AI moves
- Automatic detection of check, checkmate, and game over states
- Castling support with animated visual feedback
- Responsive design that works across devices

### AI Integration
- **Chess Engine**: Powered by external chess API
  - Strong tactical play with depth 12 analysis
  - Fast move calculation
  - Supports all chess rules including castling

- **Move Analysis**: Powered by Google's Gemini AI
  - Tactical and strategic evaluation of every move
  - Natural language insights that explain chess concepts
  - Context-aware game state analysis
  - Personalized feedback for both player and AI moves

### User Interface
- Clean, modern responsive design
- Smooth animations for piece movement and captures
- Visual move highlighting for both player and AI moves
- Board coordinates display
- Turn indicator with AI thinking animation
- Move analysis display panel
- Game status messages
- Optimized for both portrait and landscape orientations

## Quick Start

1. **Clone the Repository**
   ```bash
   git clone https://github.com/EN10/Chess.git
   cd Chess
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Gemini API**
   ```bash
   # Linux/Mac: Add to ~/.bashrc or ~/.zshrc
   export GEMINI_API_KEY='your_key_here'
   
   # Windows PowerShell
   $env:GEMINI_API_KEY='your_key_here'
   ```
   Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Open in Browser**
   ```
   http://localhost:5000
   ```

## How to Play

1. **Start a Game**
   - Visit the homepage
   - Choose to play as White or Black
   - If you choose Black, the AI will make the first move

2. **Make Moves**
   - **Drag and Drop**: Click and drag pieces to move them
   - **Click-Based**: Click a piece then click destination
   - Invalid moves are automatically rejected with feedback
   - Visual highlights show selected pieces and most recent moves

3. **Game Features**
   - AI generated move analysis appears after each move
   - AI thinking status is shown during calculations
   - Check status is indicated in the turn display
   - Start a new game anytime with the New Game button

## Technical Details

### Dependencies
- **Flask** (3.0.2): Web application framework
- **Requests** (2.31.0): HTTP client for API communication
- **Google Generative AI** (0.3.2): Gemini AI integration

### Architecture
- Python backend with Flask for server-side logic
- Chess logic implemented in a dedicated module
- RESTful API design for move validation and AI interaction
- Vanilla JavaScript frontend with modular design
- Pure CSS for responsive styling and animations
- Vercel-ready for serverless deployment

### Core Components
- `app.py`: Main application with Flask routes
- `chess_logic.py`: Chess rules implementation
- `ai_engine.py`: AI move generation and analysis
- `static/chess.js`: Client-side game interaction
- `static/styles.css`: Responsive styling
- `templates/`: HTML templates for game interface

## Development

### Project Structure
```
Chess/
├── app.py              # Main application logic
├── chess_logic.py      # Chess rules and game state
├── ai_engine.py        # AI integration
├── requirements.txt    # Python dependencies
├── static/
│   ├── chess.js        # Client-side game logic
│   └── styles.css      # UI styling
├── templates/         
│   ├── index.html      # Game interface
│   └── color_select.html # Color selection page
├── vercel.json         # Vercel deployment config
└── README.md
```

### Adding Features
1. Fork the repository
2. Create a feature branch
3. Implement changes following the existing code structure
4. Test thoroughly on different devices
5. Submit a pull request with detailed description

## Troubleshooting

### Common Issues
1. **API Key Error**
   - Ensure GEMINI_API_KEY is properly exported
   - Check for typos in the key
   - Verify API key is active in Google AI Studio

2. **Move Validation**
   - All standard chess rules are enforced
   - Kings cannot move into check
   - Special moves like castling require proper conditions

3. **Display Issues**
   - For responsive display problems, try different orientations
   - Clear browser cache if animations aren't displaying properly
   - Ensure JavaScript is enabled in your browser

## Future Enhancements

- [ ] Multiple AI difficulty levels
- [ ] PGN game export and import
- [ ] Opening book recognition
- [ ] Multiplayer support with WebSockets
- [ ] Game history and replay functionality
- [ ] Custom board themes and piece designs
- [ ] Sound effects for moves and captures
- [ ] Advanced touch device optimizations

## Version History

### v1.1.0
- Improved move animations
- Enhanced AI analysis with Gemini 2.0
- Responsive design improvements
- Bug fixes for castling and UI interactions

### v1.0.0
- Initial release
- Complete chess game implementation
- AI opponent integration
- Gemini-powered move analysis

## Contributing

Contributions are welcome! Here's how you can help:
- Report bugs by opening issues
- Suggest features or improvements
- Submit pull requests with code improvements
- Improve documentation or examples

## License

This project is licensed under [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](LICENSE).

## Acknowledgments

- Chess Engine provided by external chess API
- Move analysis powered by [Google Gemini AI](https://makersuite.google.com)
- Chess piece Unicode characters for the game board
- The Python Chess community for inspiration
