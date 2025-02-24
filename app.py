from flask import Flask, render_template, jsonify, request
import os
import google.generativeai as genai
from chess_logic import ChessGame
from ai_engine import get_ai_move, analyze_move

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize game state
game = ChessGame()

@app.route('/')
def home():
    return render_template('color_select.html')

@app.route('/select_color/<color>')
def select_color(color):
    game.player_color = color
    game.board = game.create_initial_board()
    game.current_turn = 'white'
    game.is_player_turn = color == 'white'
    
    # If player is black, get first AI move
    if not game.is_player_turn:
        fen = game.to_fen()
        ai_analysis = get_ai_move(fen)
        if ai_analysis:
            from_row, from_col, to_row, to_col = ai_analysis['coordinates']
            game.make_move(from_row, from_col, to_row, to_col)
    
    return render_template('index.html', 
                         title='Chess GPT',
                         message=f'You are playing as {color}',
                         board=game.board,
                         player_color=color)

@app.route('/move', methods=['POST'])
def move():
    if not game.is_player_turn:
        return jsonify({
            'valid': False,
            'message': "It's the AI's turn to move"
        })
    
    data = request.get_json()
    from_row = data.get('from_row')
    from_col = data.get('from_col')
    to_row = data.get('to_row')
    to_col = data.get('to_col')
    
    if game.game_over:
        return jsonify({
            'valid': False,
            'current_turn': game.current_turn,
            'game_over': True,
            'winner': game.winner,
            'message': f'Game is over! {game.winner} has won!'
        })
    
    # Validate and make player's move
    if not game.is_valid_move(from_row, from_col, to_row, to_col):
        return jsonify({
            'valid': False,
            'current_turn': game.current_turn,
            'game_over': False,
            'winner': None,
            'message': 'Invalid move! Please check piece movement rules.'
        })
    
    # Process player's move
    is_capture = game.board[to_row][to_col] != ' '
    from_square, to_square = game.make_move(from_row, from_col, to_row, to_col)
    
    # Check if opponent is in check
    opponent_color = 'black' if game.player_color == 'white' else 'white'
    is_check = game._is_in_check(opponent_color, game.board)
    
    # Get move analysis
    fen = game.to_fen()
    player_engine_analysis = get_ai_move(fen)
    player_move_analysis = analyze_move(
        model, game.board, from_row, from_col, to_row, to_col,
        is_capture, is_check, player_engine_analysis
    )
    
    # Get AI's move
    ai_analysis = get_ai_move(fen)
    ai_move_analysis = None
    ai_move_data = None

    if ai_analysis:
        ai_from_row, ai_from_col, ai_to_row, ai_to_col = ai_analysis['coordinates']
        
        # Check if AI's move is a capture
        ai_is_capture = game.board[ai_to_row][ai_to_col] != ' '
        
        # Make AI's move
        game.make_move(ai_from_row, ai_from_col, ai_to_row, ai_to_col)
        
        # Check if player is in check
        ai_is_check = game._is_in_check(game.player_color, game.board)
        
        # Get analysis for AI's move
        ai_move_analysis = analyze_move(
            model, game.board, ai_from_row, ai_from_col, ai_to_row, ai_to_col,
            ai_is_capture, ai_is_check, ai_analysis
        )
        
        # Check if AI captured the king
        if game.board[ai_to_row][ai_to_col] in '♔♚':
            game.game_over = True
            game.winner = 'black' if game.player_color == 'white' else 'white'
        
        # Prepare AI move data for frontend
        ai_move_data = {
            'from_row': ai_from_row,
            'from_col': ai_from_col,
            'to_row': ai_to_row,
            'to_col': ai_to_col,
            'is_castling': abs(ai_to_col - ai_from_col) == 2
        }
        
        if ai_move_data['is_castling']:
            ai_move_data['castling_info'] = {
                'rook_from_col': 0 if ai_to_col < ai_from_col else 7,
                'rook_to_col': ai_to_col + 1 if ai_to_col < ai_from_col else ai_to_col - 1,
                'row': ai_from_row
            }

    # Prepare response
    response = {
        'valid': True,
        'board': game.board,
        'current_turn': game.current_turn,
        'game_over': game.game_over,
        'winner': game.winner,
        'in_check': game._is_in_check(game.current_turn, game.board),
        'move_analysis': player_move_analysis,
        'ai_move': ai_move_data,
        'ai_move_analysis': ai_move_analysis
    }
    
    if game.game_over:
        response['message'] = f'Game Over! {game.winner} wins!'
    elif response['in_check']:
        response['message'] = f'{game.current_turn} is in check!'

    return jsonify(response)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(debug=True)
