# Chess GPT

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/EN10/Chess/releases)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Commit](https://img.shields.io/badge/commit-0de07d5-orange.svg)](https://github.com/EN10/Chess/commit/0de07d5)

A sophisticated web-based chess application featuring an AI opponent and real-time move analysis. Play against a strong chess engine while receiving strategic insights from both Stockfish analysis and Google's Gemini AI.

[🎮 Play Now](https://chess-gpt.vercel.app) | [📖 Documentation](https://github.com/EN10/Chess/wiki)

<div align="center">
  <img src="https://raw.githubusercontent.com/EN10/Chess-GPT/refs/heads/main/image.png" width="400" alt="Chess Game Screenshot">
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
- Play as White or Black against an International Master level AI
- Intuitive drag-and-drop or click-based piece movement
- Real-time move validation and legal move checking
- Visual feedback for selected pieces and AI moves
- Automatic detection of check, checkmate, and game over
- Resign option with confirmation

### AI Integration
- **Chess Engine**: Powered by chess-api.com using Stockfish
  - International Master playing strength
  - Stockfish 17 NNUE with 32 vCore computing power
  - Depth 12 analysis for strong tactical play
  - Fast move calculation
  - No API key required

- **Move Analysis**: Powered by Stockfish & Google's Gemini AI
  - Stockfish engine for deep tactical analysis
  - Gemini AI for natural language insights
  - Strategic evaluation of every move
  - Tactical opportunity identification
  - Clear natural language explanations
  - Context-aware game state analysis

### User Interface
- Clean, modern responsive design
- Works on desktop and mobile devices
- Visual move highlighting
- Coordinates display
- Turn indicator with AI thinking animation
- Move analysis display panel
- Game status messages
- Landscape mode optimization for tablets

## Quick Start

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd chess-game
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
   - White moves first

2. **Make Moves**
   - **Drag and Drop**: Click and drag pieces to move them
   - **Click-Based**: Click a piece then click destination
   - Invalid moves are automatically rejected
   - Visual feedback shows selected pieces and valid moves

3. **Game Features**
   - Move analysis appears after each move
   - AI thinking status is shown during calculations
   - Check is indicated with a yellow highlight
   - Resign button available for ending the game
   - New Game button to start fresh

## Technical Details

### Dependencies
- **Flask** (3.0.2): Web application framework
- **Requests** (2.31.0): HTTP client for API communication
- **Google Generative AI** (0.3.2): Gemini AI integration

### Architecture
- Python backend with Flask
- RESTful API design
- Vanilla JavaScript frontend
- Responsive CSS with flexbox/grid
- WebSocket-ready for future real-time features
- Vercel serverless deployment

### Deployment
- Automatic deployment via Vercel
- Serverless Python runtime
- Auto-scaling and high availability
- Global CDN distribution
- Zero-configuration setup

### Security
- Environment-based API key management
- HTTPS for API communications
- Input validation on all moves
- Safe error handling

## Development

### Code Structure
```
chess-game/
├── app.py              # Main application logic
├── requirements.txt    # Python dependencies
├── templates/         
│   ├── index.html     # Game interface
│   └── color_select.html # Color selection page
├── vercel.json        # Vercel deployment config
└── README.md
```

### Adding Features
1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues
1. **API Key Error**
   - Ensure GEMINI_API_KEY is properly exported
   - Check for typos in the key
   - Verify API key is active

2. **Move Validation**
   - All standard chess rules are enforced
   - Kings cannot move into check
   - Pawns promote automatically to queens

3. **Connection Issues**
   - Check internet connection
   - Verify chess-api.com is accessible
   - Ensure port 5000 is available

## Future Enhancements

- [ ] Multiple AI difficulty levels
- [ ] PGN game export
- [ ] Opening book integration
- [ ] Multiplayer support
- [ ] Game history and analysis
- [ ] Custom board themes
- [ ] Sound effects
- [ ] Touch device optimizations

## Version History

### v1.0.0
- Initial release
- Complete chess game implementation
- AI opponent integration
- Gemini-powered move analysis
- Vercel deployment setup

## Contributing

We welcome contributions! Here's how you can help:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Chess Engine provided by [chess-api.com](https://chess-api.com) (powered by Stockfish)
- Move analysis powered by [Stockfish](https://stockfishchess.org/) and [Google Gemini AI](https://makersuite.google.com)
- Chess piece Unicode characters for the game board
