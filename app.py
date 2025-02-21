from flask import Flask, render_template, jsonify, request
import copy
import requests
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini API using environment variable
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable. Please export GEMINI_API_KEY='your_key_here'")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Global variables to store game state
current_board = None
current_turn = 'white'
game_over = False
winner = None
player_color = None
is_player_turn = True

def create_initial_board():
    global game_over, winner, is_player_turn
    game_over = False
    winner = None
    is_player_turn = player_color == 'white'  # Player starts if white
    
    # Unicode pieces
    pieces = {
        'white': {
            'king': '♔', 'queen': '♕', 'rook': '♖',
            'bishop': '♗', 'knight': '♘', 'pawn': '♙'
        },
        'black': {
            'king': '♚', 'queen': '♛', 'rook': '♜',
            'bishop': '♝', 'knight': '♞', 'pawn': '♟'
        }
    }
    
    # Initialize empty board
    board = [[' ' for _ in range(8)] for _ in range(8)]
    
    # Set up black pieces
    board[0] = [pieces['black']['rook'], pieces['black']['knight'], pieces['black']['bishop'], 
                pieces['black']['queen'], pieces['black']['king'], pieces['black']['bishop'], 
                pieces['black']['knight'], pieces['black']['rook']]
    board[1] = [pieces['black']['pawn']] * 8
    
    # Set up white pieces
    board[6] = [pieces['white']['pawn']] * 8
    board[7] = [pieces['white']['rook'], pieces['white']['knight'], pieces['white']['bishop'], 
                pieces['white']['queen'], pieces['white']['king'], pieces['white']['bishop'], 
                pieces['white']['knight'], pieces['white']['rook']]
    
    return board

def get_piece_color(piece):
    white_pieces = '♔♕♖♗♘♙'
    black_pieces = '♚♛♜♝♞♟'
    if piece in white_pieces:
        return 'white'
    elif piece in black_pieces:
        return 'black'
    return None

def get_piece_type(piece):
    piece_types = {
        '♔': 'king', '♚': 'king',
        '♕': 'queen', '♛': 'queen',
        '♖': 'rook', '♜': 'rook',
        '♗': 'bishop', '♝': 'bishop',
        '♘': 'knight', '♞': 'knight',
        '♙': 'pawn', '♟': 'pawn'
    }
    return piece_types.get(piece)

def is_valid_pawn_move(from_row, from_col, to_row, to_col, board, color):
    direction = -1 if color == 'white' else 1
    start_row = 6 if color == 'white' else 1
    
    # Basic one square forward move
    if from_col == to_col and to_row == from_row + direction and board[to_row][to_col] == ' ':
        return True
    
    # Initial two square move
    if from_row == start_row and from_col == to_col and to_row == from_row + 2 * direction:
        if board[to_row][to_col] == ' ' and board[from_row + direction][from_col] == ' ':
            return True
    
    # Capture diagonally
    if to_row == from_row + direction and abs(to_col - from_col) == 1:
        if board[to_row][to_col] != ' ' and get_piece_color(board[to_row][to_col]) != color:
            return True
    
    return False

def is_valid_knight_move(from_row, from_col, to_row, to_col, board):
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

def is_valid_bishop_move(from_row, from_col, to_row, to_col, board):
    if abs(to_row - from_row) != abs(to_col - from_col):
        return False
    
    row_step = 1 if to_row > from_row else -1
    col_step = 1 if to_col > from_col else -1
    
    current_row, current_col = from_row + row_step, from_col + col_step
    while current_row != to_row:
        if board[current_row][current_col] != ' ':
            return False
        current_row += row_step
        current_col += col_step
    
    return True

def is_valid_rook_move(from_row, from_col, to_row, to_col, board):
    if from_row != to_row and from_col != to_col:
        return False
    
    if from_row == to_row:
        step = 1 if to_col > from_col else -1
        for col in range(from_col + step, to_col, step):
            if board[from_row][col] != ' ':
                return False
    else:
        step = 1 if to_row > from_row else -1
        for row in range(from_row + step, to_row, step):
            if board[row][from_col] != ' ':
                return False
    
    return True

def is_valid_queen_move(from_row, from_col, to_row, to_col, board):
    return is_valid_bishop_move(from_row, from_col, to_row, to_col, board) or \
           is_valid_rook_move(from_row, from_col, to_row, to_col, board)

def is_valid_king_move(from_row, from_col, to_row, to_col, board):
    return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1

def find_king(board, color):
    king_symbol = '♔' if color == 'white' else '♚'
    for row in range(8):
        for col in range(8):
            if board[row][col] == king_symbol:
                return row, col
    return None

def is_square_under_attack(row, col, attacking_color, board):
    # Check all squares for attacking pieces
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece != ' ' and get_piece_color(piece) == attacking_color:
                # Simulate the move to check if it's valid
                if is_valid_piece_move(i, j, row, col, board):
                    return True
    return False

def is_in_check(color, board):
    # Find the king's position
    king_pos = find_king(board, color)
    if not king_pos:
        return False
    
    # Check if the opponent can attack the king's square
    opponent_color = 'black' if color == 'white' else 'white'
    return is_square_under_attack(king_pos[0], king_pos[1], opponent_color, board)

def would_be_in_check(from_row, from_col, to_row, to_col, board):
    # Make a copy of the board
    temp_board = [row[:] for row in board]
    
    # Make the move on the temporary board
    temp_board[to_row][to_col] = temp_board[from_row][from_col]
    temp_board[from_row][from_col] = ' '
    
    # Check if the moving player's king would be in check
    moving_color = get_piece_color(board[from_row][from_col])
    return is_in_check(moving_color, temp_board)

def is_valid_piece_move(from_row, from_col, to_row, to_col, board):
    piece = board[from_row][from_col]
    if piece == ' ':
        return False
        
    piece_color = get_piece_color(piece)
    piece_type = get_piece_type(piece)
    
    # Check if target square has a piece of the same color
    target_piece = board[to_row][to_col]
    if target_piece != ' ' and get_piece_color(target_piece) == piece_color:
        return False
    
    if piece_type == 'pawn':
        return is_valid_pawn_move(from_row, from_col, to_row, to_col, board, piece_color)
    elif piece_type == 'knight':
        return is_valid_knight_move(from_row, from_col, to_row, to_col, board)
    elif piece_type == 'bishop':
        return is_valid_bishop_move(from_row, from_col, to_row, to_col, board)
    elif piece_type == 'rook':
        return is_valid_rook_move(from_row, from_col, to_row, to_col, board)
    elif piece_type == 'queen':
        return is_valid_queen_move(from_row, from_col, to_row, to_col, board)
    elif piece_type == 'king':
        return is_valid_king_move(from_row, from_col, to_row, to_col, board)
    
    return False

def is_valid_move(from_row, from_col, to_row, to_col, board):
    global current_turn
    
    # Basic boundary check
    if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
        return False
    
    # Check if there's a piece at the starting position
    piece = board[from_row][from_col]
    if piece == ' ':
        return False
    
    # Check if it's the right player's turn
    piece_color = get_piece_color(piece)
    if piece_color != current_turn:
        return False
    
    # Check if the move is valid for the piece type
    if not is_valid_piece_move(from_row, from_col, to_row, to_col, board):
        return False
    
    # Check if the move would leave the player's king in check
    if would_be_in_check(from_row, from_col, to_row, to_col, board):
        return False
    
    return True

def board_to_fen(board, current_turn):
    # Map Unicode pieces to FEN characters
    piece_to_fen = {
        '♔': 'K', '♕': 'Q', '♖': 'R', '♗': 'B', '♘': 'N', '♙': 'P',
        '♚': 'k', '♛': 'q', '♜': 'r', '♝': 'b', '♞': 'n', '♟': 'p',
        ' ': '1'
    }
    
    fen_parts = []
    for row in board:
        empty_squares = 0
        row_fen = ''
        for piece in row:
            if piece == ' ':
                empty_squares += 1
            else:
                if empty_squares > 0:
                    row_fen += str(empty_squares)
                    empty_squares = 0
                row_fen += piece_to_fen[piece]
        if empty_squares > 0:
            row_fen += str(empty_squares)
        fen_parts.append(row_fen)
    
    # Join rows with '/'
    position = '/'.join(fen_parts)
    
    # Add turn indicator
    turn = 'w' if current_turn == 'white' else 'b'
    
    # Add castling, en passant, and move counters (simplified)
    return f"{position} {turn} - - 0 1"

def get_ai_move(fen):
    try:
        # Using chess-api.com's free API
        response = requests.post('https://chess-api.com/v1', 
            json={
                'fen': fen,
                'depth': 12,  # Default depth for good play (International Master level)
                'variants': 1  # Get the best move only
            }
        )
        data = response.json()
        if 'move' in data:
            # Convert API move format (e.g., 'e2e4') to our format
            # The move is in long algebraic notation (e.g., 'e2e4' or 'b7b8q')
            move = data['move']
            from_col = ord(move[0]) - ord('a')
            from_row = 8 - int(move[1])
            to_col = ord(move[2]) - ord('a')
            to_row = 8 - int(move[3])
            return from_row, from_col, to_row, to_col
    except Exception as e:
        print(f"Error getting AI move: {e}")
    return None

def analyze_move(board, from_row, from_col, to_row, to_col, is_capture, is_check):
    # Convert board coordinates to chess notation
    files = 'abcdefgh'
    ranks = '87654321'
    from_square = f"{files[from_col]}{ranks[from_row]}"
    to_square = f"{files[to_col]}{ranks[to_row]}"
    
    # Get piece type and color
    piece = board[from_row][from_col]
    piece_type = get_piece_type(piece)
    piece_color = get_piece_color(piece)
    
    # Create a description of the move
    move_desc = f"Move analysis request: {piece_color} {piece_type} from {from_square} to {to_square}"
    if is_capture:
        captured_piece = board[to_row][to_col]
        captured_type = get_piece_type(captured_piece)
        move_desc += f", capturing {get_piece_color(captured_piece)} {captured_type}"
    if is_check:
        move_desc += ", putting opponent in check"
    
    prompt = f"""
    As a chess expert, analyze this move:
    {move_desc}
    
    Consider:
    1. Strategic value
    2. Position control
    3. Piece development
    4. Potential threats or opportunities
    
    Provide a brief, focused analysis in 2-3 sentences.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error getting move analysis: {e}")
        return "Move analysis unavailable."

@app.route('/')
def home():
    return render_template('color_select.html')

@app.route('/select_color/<color>')
def select_color(color):
    global current_board, current_turn, player_color, is_player_turn
    player_color = color
    current_board = create_initial_board()
    current_turn = 'white'
    is_player_turn = player_color == 'white'
    
    # If player is black, get first AI move
    if not is_player_turn:
        fen = board_to_fen(current_board, current_turn)
        ai_move = get_ai_move(fen)
        if ai_move:
            from_row, from_col, to_row, to_col = ai_move
            make_move(from_row, from_col, to_row, to_col)
    
    return render_template('index.html', 
                         title='Chess Board',
                         message=f'You are playing as {color}',
                         board=current_board,
                         player_color=color)

def make_move(from_row, from_col, to_row, to_col):
    global current_board, current_turn, game_over, winner, is_player_turn
    
    # Make the move
    current_board[to_row][to_col] = current_board[from_row][from_col]
    current_board[from_row][from_col] = ' '
    
    # Switch turns
    current_turn = 'black' if current_turn == 'white' else 'white'
    is_player_turn = not is_player_turn

@app.route('/move', methods=['POST'])
def move():
    global current_board, current_turn, game_over, winner, is_player_turn
    data = request.get_json()
    
    if not is_player_turn:
        return jsonify({
            'valid': False,
            'message': "It's the AI's turn to move"
        })
    
    from_row = data.get('from_row')
    from_col = data.get('from_col')
    to_row = data.get('to_row')
    to_col = data.get('to_col')
    
    if game_over:
        return jsonify({
            'valid': False,
            'current_turn': current_turn,
            'game_over': True,
            'winner': winner,
            'message': f'Game is over! {winner} has won!'
        })
    
    if is_valid_move(from_row, from_col, to_row, to_col, current_board):
        # Check if player's move is a capture
        is_capture = current_board[to_row][to_col] != ' '
        
        # Make player's move
        make_move(from_row, from_col, to_row, to_col)
        
        # Check if opponent is in check after the move
        opponent_color = 'black' if player_color == 'white' else 'white'
        is_check = is_in_check(opponent_color, current_board)
        
        # Get move analysis from Gemini for player's move
        player_move_analysis = analyze_move(
            current_board, from_row, from_col, to_row, to_col,
            is_capture, is_check
        )
        
        # Get AI's move
        fen = board_to_fen(current_board, current_turn)
        ai_move = get_ai_move(fen)
        ai_move_analysis = None
        
        if ai_move:
            ai_from_row, ai_from_col, ai_to_row, ai_to_col = ai_move
            
            # Check if AI's move is a capture before making it
            ai_is_capture = current_board[ai_to_row][ai_to_col] != ' '
            
            # Make AI's move
            make_move(ai_from_row, ai_from_col, ai_to_row, ai_to_col)
            
            # Check if player is in check after AI's move
            ai_is_check = is_in_check(player_color, current_board)
            
            # Get analysis for AI's move
            ai_move_analysis = analyze_move(
                current_board, ai_from_row, ai_from_col, ai_to_row, ai_to_col,
                ai_is_capture, ai_is_check
            )
            
            # Check if AI captured the king
            if current_board[ai_to_row][ai_to_col] in '♔♚':
                game_over = True
                winner = 'black' if player_color == 'white' else 'white'
                return jsonify({
                    'valid': True,
                    'board': current_board,
                    'current_turn': current_turn,
                    'game_over': True,
                    'winner': winner,
                    'message': f'Game Over! AI wins by capturing your king!',
                    'move_analysis': player_move_analysis,
                    'ai_move': {
                        'from_row': ai_from_row,
                        'from_col': ai_from_col,
                        'to_row': ai_to_row,
                        'to_col': ai_to_col
                    },
                    'ai_move_analysis': ai_move_analysis
                })
        
        # Check if the current player is in check
        if is_in_check(current_turn, current_board):
            return jsonify({
                'valid': True,
                'board': current_board,
                'current_turn': current_turn,
                'game_over': False,
                'winner': None,
                'in_check': True,
                'message': f'{current_turn} is in check!',
                'move_analysis': player_move_analysis,
                'ai_move': {
                    'from_row': ai_from_row,
                    'from_col': ai_from_col,
                    'to_row': ai_to_row,
                    'to_col': ai_to_col
                } if ai_move else None,
                'ai_move_analysis': ai_move_analysis
            })
        
        return jsonify({
            'valid': True,
            'board': current_board,
            'current_turn': current_turn,
            'game_over': False,
            'winner': None,
            'in_check': False,
            'move_analysis': player_move_analysis,
            'ai_move': {
                'from_row': ai_from_row,
                'from_col': ai_from_col,
                'to_row': ai_to_row,
                'to_col': ai_to_col
            } if ai_move else None,
            'ai_move_analysis': ai_move_analysis
        })
    
    return jsonify({
        'valid': False,
        'current_turn': current_turn,
        'game_over': False,
        'winner': None,
        'message': 'Invalid move! This would leave your king in check.'
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy"
    })

if __name__ == '__main__':
    app.run(debug=True) 