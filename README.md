# AI Chess Game

A sophisticated web-based chess application featuring an AI opponent and real-time move analysis. Play against a strong chess engine while receiving strategic insights from Google's Gemini AI.

![Chess Game Screenshot]

## Key Features

### Chess Gameplay
- Play as White or Black against an International Master level AI
- Intuitive drag-and-drop or click-based piece movement
- Real-time move validation and legal move checking
- Visual feedback for selected pieces and AI moves
- Automatic detection of check, checkmate, and game over
- Resign option with confirmation

### AI Integration
- **Chess Engine**: Powered by chess-api.com
  - International Master playing strength
  - Depth 12 analysis for strong tactical play
  - Fast move calculation
  - No API key required

- **Move Analysis**: Powered by Google's Gemini AI
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

## Contributing

Contributions are welcome! Please feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Chess API provided by [chess-api.com](https://chess-api.com)
- Move analysis powered by [Google Gemini AI](https://makersuite.google.com)
- Chess piece Unicode characters for the game board 