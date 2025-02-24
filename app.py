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
    # Initialize game with player's color choice
    game.player_color = color
    game.board = game.create_initial_board()
    game.current_turn = 'white'
    game.is_player_turn = color == 'white'
    
    # If player is black, make AI's first move
    if not game.is_player_turn:
        ai_analysis = get_ai_move(game.to_fen())
        if ai_analysis:
            game.make_move(*ai_analysis['coordinates'])
    
    return render_template('index.html', 
                         title='Chess GPT',
                         message=f'You are playing as {color}',
                         board=game.board,
                         player_color=color)

@app.route('/move', methods=['POST'])
def move():
    # Quick validation checks
    if game.game_over:
        return jsonify({
            'valid': False,
            'current_turn': game.current_turn,
            'game_over': True,
            'winner': game.winner,
            'message': f'Game is over! {game.winner} has won!'
        })
    
    if not game.is_player_turn:
        return jsonify({
            'valid': False,
            'message': "It's the AI's turn to move"
        })
    
    # Process player's move
    data = request.get_json()
    from_row, from_col, to_row, to_col = [data.get(k) for k in ('from_row', 'from_col', 'to_row', 'to_col')]
    
    # Validate move
    if not game.is_valid_move(from_row, from_col, to_row, to_col):
        return jsonify({
            'valid': False,
            'current_turn': game.current_turn,
            'message': 'Invalid move! Please check piece movement rules.'
        })
    
    # Save the original piece information before the move
    original_piece = game.board[from_row][from_col]
    
    # Execute player's move
    is_capture = game.board[to_row][to_col] != ' '
    game.make_move(from_row, from_col, to_row, to_col)
    
    # Check if opponent is in check
    opponent_color = 'black' if game.player_color == 'white' else 'white'
    is_check = game._is_in_check(opponent_color, game.board)
    
    # Get move analysis
    fen = game.to_fen()
    player_engine_analysis = get_ai_move(fen)
    
    # Create a temporary board with the original piece for analysis
    temp_board = [row[:] for row in game.board]  # Deep copy the current board
    temp_board[from_row][from_col] = original_piece  # Restore the original piece at the from position
    temp_board[to_row][to_col] = ' '  # Clear the to position
    
    player_move_analysis = analyze_move(
        model, temp_board, from_row, from_col, to_row, to_col,
        is_capture, is_check, player_engine_analysis
    )
    
    # Prepare response
    response = {
        'valid': True,
        'board': game.board,
        'current_turn': game.current_turn,
        'move_analysis': player_move_analysis,
        'game_over': game.game_over,
        'winner': game.winner,
        'in_check': game._is_in_check(game.current_turn, game.board),
    }
    
    # Process AI's move if game is still ongoing
    ai_move_data = None
    if not game.game_over:
        ai_analysis = get_ai_move(fen)
        if ai_analysis:
            # Extract AI move data
            ai_coords = ai_analysis['coordinates']
            ai_from_row, ai_from_col, ai_to_row, ai_to_col = ai_coords
            
            # Check if AI's move is a capture
            ai_is_capture = game.board[ai_to_row][ai_to_col] != ' '
            
            # Save the original AI piece information before the move
            ai_original_piece = game.board[ai_from_row][ai_from_col]
            
            # Make AI's move
            game.make_move(ai_from_row, ai_from_col, ai_to_row, ai_to_col)
            
            # Check if player is in check
            ai_is_check = game._is_in_check(game.player_color, game.board)
            
            # Create a temporary board with the original AI piece for analysis
            ai_temp_board = [row[:] for row in game.board]  # Deep copy the current board
            ai_temp_board[ai_from_row][ai_from_col] = ai_original_piece  # Restore the original piece
            ai_temp_board[ai_to_row][ai_to_col] = ' '  # Clear the destination
            
            # Get analysis for AI's move
            response['ai_move_analysis'] = analyze_move(
                model, ai_temp_board, ai_from_row, ai_from_col, ai_to_row, ai_to_col,
                ai_is_capture, ai_is_check, ai_analysis
            )
            
            # Prepare AI move data for frontend
            is_castling = abs(ai_to_col - ai_from_col) == 2 and game.board[ai_to_row][ai_to_col] in '♔♚'
            ai_move_data = {
                'from_row': ai_from_row,
                'from_col': ai_from_col,
                'to_row': ai_to_row,
                'to_col': ai_to_col,
                'is_castling': is_castling
            }
            
            # Add castling info if needed
            if is_castling:
                ai_move_data['castling_info'] = {
                    'row': ai_from_row,
                    'rook_from_col': 0 if ai_to_col < ai_from_col else 7,
                    'rook_to_col': ai_to_col + 1 if ai_to_col < ai_from_col else ai_to_col - 1
                }
    
    # Update response with AI move and latest game state
    response.update({
        'ai_move': ai_move_data,
        'current_turn': game.current_turn,
        'game_over': game.game_over,
        'winner': game.winner,
        'in_check': game._is_in_check(game.current_turn, game.board)
    })
    
    # Add appropriate message
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
