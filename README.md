# Chess Game with AI and Move Analysis

A sophisticated web-based chess application featuring an AI opponent powered by chess-api.com and strategic move analysis powered by Google's Gemini AI. This application combines classical chess gameplay with modern AI analysis to provide an educational and engaging chess experience.

## Features

### Game Mechanics
- Play chess against an AI opponent with International Master level strength
- Choose to play as either White or Black pieces
- Real-time move validation and game state tracking
- Support for all standard chess moves and rules
- Visual feedback for moves, checks, and captures
- Automatic detection of checkmate and game over conditions

### AI Integration
- AI opponent powered by chess-api.com's chess engine
- Depth 12 analysis for strong tactical play
- Strategic move analysis by Google's Gemini AI after each move
- Detailed commentary on both player and AI moves
- Analysis of position control, piece development, and tactical opportunities

### User Interface
- Clean, modern web interface
- Drag-and-drop piece movement
- Coordinate notation display
- Turn indicator with visual state feedback
- Move status messages and error handling
- AI thinking animation during move calculation
- Responsive design for various screen sizes

### Game Controls
- New Game button to start fresh
- Resign option with confirmation
- Status bar with game controls
- Automatic game restart after resignation

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd chess-game
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the Gemini API key:
   ```bash
   # For permanent configuration (recommended)
   # Add to ~/.bashrc or ~/.zshrc:
   export GEMINI_API_KEY='your_gemini_api_key_here'
   
   # For temporary session:
   export GEMINI_API_KEY='your_gemini_api_key_here'
   ```
   
   Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Dependencies

- **Flask (3.0.2)**: Web framework for the application
- **Requests (2.31.0)**: HTTP library for API communication
- **Google Generative AI (0.3.2)**: Gemini AI integration for move analysis

## APIs Used

### Chess Engine
- **Provider**: [chess-api.com](https://chess-api.com)
- **Features**: 
  - Free chess engine API
  - Configurable analysis depth
  - Returns best moves in standard notation
  - No API key required

### Move Analysis
- **Provider**: [Google Gemini AI](https://makersuite.google.com/app/apikey)
- **Features**:
  - Strategic position analysis
  - Move quality evaluation
  - Tactical opportunity identification
  - Natural language move descriptions
  - Requires API key

## Game Flow

1. **Start**: Choose your color (White/Black)
2. **Gameplay**:
   - Drag and drop pieces to make moves
   - Valid moves are automatically detected
   - AI responds with calculated moves
   - Both player and AI moves receive analysis
3. **Analysis Display**:
   - Green border: Player move analysis
   - Blue border: AI move analysis
   - Analyses remain visible during gameplay
4. **Game End**:
   - Automatic checkmate detection
   - Resignation option
   - Winner declaration
   - Automatic restart option

## Security Notes

- Keep your Gemini API key private
- Use environment variables for sensitive data
- Never commit API keys to version control
- The application uses HTTPS for API communications

## Technical Details

- Built with Python 3.x
- Flask development server
- RESTful API architecture
- Real-time move validation
- FEN position notation for game state
- Unicode chess pieces
- Responsive CSS design

## Error Handling

- Invalid move detection
- API failure recovery
- Network error handling
- User feedback messages
- Graceful state management

## Future Enhancements

- Move history logging
- Analysis strength settings
- Multiple AI difficulty levels
- PGN game export
- Opening book integration
- Multiplayer support

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is open source and available under the MIT License. 