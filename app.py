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

# Track if king and rook have moved
king_moved = {'white': False, 'black': False}
rook_moved = {'white': [False, False], 'black': [False, False]}  # [left rook, right rook]

def create_initial_board():
    global game_over, winner, is_player_turn, king_moved, rook_moved
    game_over = False
    winner = None
    is_player_turn = player_color == 'white'  # Player starts if white

    # Reset castling tracking
    king_moved = {'white': False, 'black': False}
    rook_moved = {'white': [False, False], 'black': [False, False]}  # [left rook, right rook]
    
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
    
    # Set up black pieces (correct order from left to right)
    board[0] = [pieces['black']['rook'], pieces['black']['knight'], pieces['black']['bishop'],
                pieces['black']['queen'], pieces['black']['king'], pieces['black']['bishop'],
                pieces['black']['knight'], pieces['black']['rook']]
    board[1] = [pieces['black']['pawn']] * 8
    
    # Set up white pieces (correct order from left to right)
    board[6] = [pieces['white']['pawn']] * 8
    board[7] = [pieces['white']['rook'], pieces['white']['knight'], pieces['white']['bishop'],
                pieces['white']['queen'], pieces['white']['king'], pieces['white']['bishop'],
                pieces['white']['knight'], pieces['white']['rook']]
    
    # Print initial rook positions for debugging
    print("Initial rook positions:")
    print(f"White rooks at: a1 ({board[7][0]}) and h1 ({board[7][7]})")
    print(f"Black rooks at: a8 ({board[0][0]}) and h8 ({board[0][7]})")
    
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

def is_valid_attack_move(from_row, from_col, to_row, to_col, board):
    """Check if a piece could theoretically move to attack a square, ignoring check and piece blocking."""
    piece = board[from_row][from_col]
    if piece == ' ':
        return False
        
    piece_type = get_piece_type(piece)
    
    # Only validate the geometric pattern of the piece's movement
    if piece_type == 'pawn':
        # Pawns can only attack diagonally
        direction = -1 if get_piece_color(piece) == 'white' else 1
        return to_row == from_row + direction and abs(to_col - from_col) == 1
    elif piece_type == 'knight':
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    elif piece_type == 'bishop':
        return abs(to_row - from_row) == abs(to_col - from_col)
    elif piece_type == 'rook':
        return from_row == to_row or from_col == to_col
    elif piece_type == 'queen':
        return from_row == to_row or from_col == to_col or abs(to_row - from_row) == abs(to_col - from_col)
    elif piece_type == 'king':
        return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
    return False

def is_square_under_attack(row, col, attacking_color, board):
    """Check if any piece of the attacking_color can attack the given square."""
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece != ' ' and get_piece_color(piece) == attacking_color:
                if is_valid_attack_move(i, j, row, col, board):
                    # For non-knight pieces, check if path is clear
                    if get_piece_type(piece) != 'knight':
                        # Get movement direction
                        row_step = 0 if row == i else (row - i) // abs(row - i)
                        col_step = 0 if col == j else (col - j) // abs(col - j)
                        
                        # Check each square along the path
                        current_row, current_col = i + row_step, j + col_step
                        path_clear = True
                        while (current_row, current_col) != (row, col):
                            if board[current_row][current_col] != ' ':
                                path_clear = False
                                break
                            current_row += row_step
                            current_col += col_step
                        
                        if path_clear:
                            return True
                    else:  # Knights can jump over pieces
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
    # For castling moves, skip simulation because intermediate checks are done in is_valid_move
    if get_piece_type(board[from_row][from_col]) == 'king' and abs(to_col - from_col) == 2:
        print('Bypassing would_be_in_check simulation for castling move.')
        return False
    else:
        # Normal move: make a copy and simulate move
        temp_board = [row[:] for row in board]
        temp_board[to_row][to_col] = temp_board[from_row][from_col]
        temp_board[from_row][from_col] = ' '
        return is_in_check(get_piece_color(board[from_row][from_col]), temp_board)

def is_valid_piece_move(from_row, from_col, to_row, to_col, board):
    piece = board[from_row][from_col]
    if piece == ' ':
        return False
        
    piece_color = get_piece_color(piece)
    piece_type = get_piece_type(piece)
    
    # Check if target square has a piece of the same color (do this check first)
    target_piece = board[to_row][to_col]
    if target_piece != ' ' and get_piece_color(target_piece) == piece_color:
        print(f"Invalid move: Cannot capture own piece ({piece_type} to {target_piece})")
        return False
    
    # Now proceed with piece-specific movement validation
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
        if abs(to_col - from_col) == 2:
            # Allow castling move. Actual castling conditions are validated in is_valid_move.
            return True
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
    
    # Get the piece type for further validation
    piece_type = get_piece_type(piece)
    
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

    # Handle castling
    if piece_type == 'king' and abs(to_col - from_col) == 2:
        rook_col = 0 if to_col < from_col else 7  # Determine rook's column
        opponent_color = 'black' if piece_color == 'white' else 'white'
        print(f'Castling attempt: {piece_color} king from col {from_col} to col {to_col}, rook at col {rook_col}')
        print(f'Castling state - King moved: {king_moved[piece_color]}, Rook moved: {rook_moved[piece_color]}')

        # Verify rook is present
        rook_piece = board[from_row][rook_col]
        expected_rook = '♖' if piece_color == 'white' else '♜'
        print(f'Checking rook presence: found {rook_piece}, expected {expected_rook}')
        if rook_piece != expected_rook:
            print('Required rook not found for castling')
            return False

        # Check path between king and rook is clear
        start_col = min(from_col, rook_col) + 1
        end_col = max(from_col, rook_col)
        print(f'Checking castling path from column {start_col} to {end_col-1}')
        for col in range(start_col, end_col):
            print(f'Checking square at row {from_row}, col {col}: {board[from_row][col]}')
            if board[from_row][col] != ' ':
                print(f'Path not clear for castling at column {col}. Found {board[from_row][col]}')
                return False

        # Check that squares king moves through are not under attack
        start_attack = is_square_under_attack(from_row, from_col, opponent_color, board)
        mid_square = (from_col + to_col) // 2
        mid_attack = is_square_under_attack(from_row, mid_square, opponent_color, board)
        dest_attack = is_square_under_attack(from_row, to_col, opponent_color, board)
        print(f'King starting square under attack: {start_attack}')
        print(f'Square at col {mid_square} under attack: {mid_attack}')
        print(f'King destination square under attack: {dest_attack}')
        if start_attack:
            print('King starting square is under attack.')
            return False
        if mid_attack:
            print('Square king passes through is under attack.')
            return False
        if dest_attack:
            print('King destination square is under attack.')
            return False

        if has_king_moved(piece_color) or has_rook_moved(piece_color, rook_col):
            print('King or rook has already moved. Castling not allowed.')
            return False

        print('Castling is allowed.')

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
    
    # Add castling availability
    castling = ''
    if not king_moved['white']:
        if not rook_moved['white'][1]:  # Kingside
            castling += 'K'
        if not rook_moved['white'][0]:  # Queenside
            castling += 'Q'
    if not king_moved['black']:
        if not rook_moved['black'][1]:  # Kingside
            castling += 'k'
        if not rook_moved['black'][0]:  # Queenside
            castling += 'q'
    if not castling:
        castling = '-'
    
    # Add castling, en passant, and move counters
    return f"{position} {turn} {castling} - 0 1"

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

            # Extract additional analysis data
            analysis = {
                'text': data.get('text', 'No description available'),
                'win_chance': data.get('winChance', None),
                'mate': data.get('mate', None),
                'coordinates': (from_row, from_col, to_row, to_col)
            }
            return analysis
    except Exception as e:
        print(f"Error getting AI move: {e}")
    return None

def analyze_move(board, from_row, from_col, to_row, to_col, is_capture, is_check, engine_analysis=None):
    # Convert board coordinates to chess notation
    files = 'abcdefgh'
    ranks = '87654321'
    from_square = f"{files[from_col]}{ranks[from_row]}"
    to_square = f"{files[to_col]}{ranks[to_row]}"
    
    # Get piece type and color
    piece = board[from_row][from_col]
    piece_type = get_piece_type(piece)
    piece_color = get_piece_color(piece)
    
    # Create a board representation
    board_str = "\nCurrent board position:\n"
    for row in range(8):
        board_str += f"{8-row} "
        for col in range(8):
            piece = board[row][col]
            board_str += f"{piece if piece != ' ' else '.'} "
        board_str += "\n"
    board_str += "  a b c d e f g h\n"
    
    # Create a description of the move
    move_desc = f"Move analysis request: {piece_color} {piece_type} from {from_square} to {to_square}"
    if is_capture:
        captured_piece = board[to_row][to_col]
        captured_type = get_piece_type(captured_piece)
        move_desc += f", capturing {get_piece_color(captured_piece)} {captured_type}"
    if is_check:
        move_desc += ", putting opponent in check"
    
    # Add engine analysis to the prompt if available
    engine_info = ""
    if engine_analysis:
        engine_info = f"""
        Engine Analysis:
        - Description: {engine_analysis.get('text', 'No description available')}
        - Win Probability: {engine_analysis.get('win_chance', 'Not available')}"""
        if engine_analysis.get('mate'):
            engine_info += f"\n        - Mate in: {engine_analysis['mate']} moves"

    prompt = f"""
    As a chess expert, analyze this move:
    {move_desc}
    {engine_info}
    
    {board_str}
    
    Consider:
    1. Strategic value
    2. Position control
    3. Piece development
    4. Potential threats or opportunities
    
    Provide a brief, focused analysis incorporating the engine's evaluation if available.
    Include concrete tactical or positional advantages, and if there's a forced mate sequence.
    Aim for 2-3 clear, informative sentences.
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
        print(f"Initial position FEN (AI to move): {fen}")
        print(f"Castling rights - White: K={'K' in fen} Q={'Q' in fen}, Black: k={'k' in fen} q={'q' in fen}")
        ai_analysis = get_ai_move(fen)
        if ai_analysis:
            from_row, from_col, to_row, to_col = ai_analysis['coordinates']
            make_move(from_row, from_col, to_row, to_col)
    
    return render_template('index.html', 
                         title='Chess Board',
                         message=f'You are playing as {color}',
                         board=current_board,
                         player_color=color)

def has_king_moved(color):
    return king_moved[color]

def has_rook_moved(color, rook_col):
    if color == 'white':
        return rook_moved['white'][0] if rook_col == 0 else rook_moved['white'][1]
    else:
        return rook_moved['black'][0] if rook_col == 0 else rook_moved['black'][1]

def make_move(from_row, from_col, to_row, to_col):
    global current_board, current_turn, game_over, winner, is_player_turn
    
    piece = current_board[from_row][from_col]
    piece_type = get_piece_type(piece)
    piece_color = get_piece_color(piece)

    # Log the move in chess notation
    files = 'abcdefgh'
    ranks = '87654321'
    from_square = f'{files[from_col]}{ranks[from_row]}'
    to_square = f'{files[to_col]}{ranks[to_row]}'
    print(f'Moving {piece} ({piece_type}) from {from_square} to {to_square}')
    
    if piece_type == 'rook':
        print(f'Rook move: Color={piece_color}, From col={from_col}')
        print(f'Current rook moved state: {rook_moved[piece_color]}')

    is_castling = piece_type == 'king' and abs(to_col - from_col) == 2
    rook_col = None
    new_rook_col = None

    # Set up castling move if applicable
    if is_castling:
        rook_col = 0 if to_col < from_col else 7  # Determine rook's column (a-file or h-file)
        new_rook_col = 3 if to_col < from_col else 5  # Fixed rook columns: d-file (3) for queenside, f-file (5) for kingside
        rook = current_board[from_row][rook_col]

    # Make the moves in the correct order
    if is_castling:
        # Move king first
        current_board[to_row][to_col] = piece
        current_board[from_row][from_col] = ' '
        # Then move rook
        current_board[from_row][new_rook_col] = rook
        current_board[from_row][rook_col] = ' '
        # Mark pieces as moved after successful castling
        king_moved[current_turn] = True
        rook_moved[current_turn][0 if rook_col == 0 else 1] = True
    else:
        # Make normal move
        current_board[to_row][to_col] = piece
        current_board[from_row][from_col] = ' '
        # Mark pieces as moved after successful normal move
        if piece_type == 'king':
            king_moved[current_turn] = True
            print(f'King moved - updated state: {king_moved[current_turn]}')
        elif piece_type == 'rook':
            rook_moved[current_turn][0 if from_col == 0 else 1] = True
            print(f'Rook moved from col {from_col} - updated state: {rook_moved[current_turn]}')
    
    # Switch turns
    current_turn = 'black' if current_turn == 'white' else 'white'
    is_player_turn = not is_player_turn

    # Log the current board state
    print('Current board state:')
    for row in current_board:
        print(' '.join(row))

    # Return the move in chess notation for AI analysis
    return from_square, to_square

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
    
    piece = current_board[from_row][from_col]
    piece_type = get_piece_type(piece)

    # Check if we're attempting castling
    is_castling_attempt = piece_type == 'king' and abs(to_col - from_col) == 2
    if is_castling_attempt:
        # Verify basic castling conditions before trying the move
        piece_color = get_piece_color(piece)
        if has_king_moved(piece_color):
            error_message = 'Invalid move! Cannot castle after king has moved.'
        elif has_rook_moved(piece_color, 0 if to_col < from_col else 7):
            error_message = 'Invalid move! Cannot castle with rook that has moved.'
        else:
            error_message = 'Invalid castling move! Check that path is clear and king is not in check.'
    else:
        error_message = 'Invalid move! Please check piece movement rules and king safety.'
    
    if not is_valid_move(from_row, from_col, to_row, to_col, current_board):
        print(error_message)  # Log to server console
        return jsonify({
            'valid': False,
            'current_turn': current_turn,
            'game_over': False,
            'winner': None,
            'message': error_message
        })
    
    # Check if player's move is a capture
    is_capture = current_board[to_row][to_col] != ' '
    
    # Get piece type before making the move
    piece_type = get_piece_type(current_board[from_row][from_col])
    is_castling = piece_type == 'king' and abs(to_col - from_col) == 2
    castling_info = None
    if is_castling:
        castling_info = {
            'is_castling': True,
            'rook_from_col': 0 if to_col < from_col else 7,
            'rook_to_col': to_col + 1 if to_col < from_col else to_col - 1,
            'row': from_row
        }
    
    # Make player's move
    from_square, to_square = make_move(from_row, from_col, to_row, to_col)
    
    # Check if opponent is in check after the move
    opponent_color = 'black' if player_color == 'white' else 'white'
    is_check = is_in_check(opponent_color, current_board)
    
    # Get move analysis from Gemini for player's move with engine feedback
    # We make a copy of the board to get the position after the player's move but before AI's move
    board_copy = [row[:] for row in current_board]
    fen = board_to_fen(board_copy, opponent_color)
    player_engine_analysis = get_ai_move(fen)
    player_move_analysis = analyze_move(
        current_board, from_row, from_col, to_row, to_col,
        is_capture, is_check, player_engine_analysis
    )
    
    # Get AI's move and analysis
    fen = board_to_fen(current_board, current_turn)
    print(f"Position FEN before AI move: {fen}")
    print(f"Castling rights - White: K={'K' in fen} Q={'Q' in fen}, Black: k={'k' in fen} q={'q' in fen}")
    ai_analysis = get_ai_move(fen)
    ai_move_analysis = None

    # Pre-analyze AI move if available
    if ai_analysis:
        files = 'abcdefgh'
        ranks = '87654321'
        ai_from_row, ai_from_col, ai_to_row, ai_to_col = ai_analysis['coordinates']
        ai_piece = current_board[ai_from_row][ai_from_col]
        ai_piece_type = get_piece_type(ai_piece)
        ai_piece_color = get_piece_color(ai_piece)
        
        if ai_piece_type == 'king' and abs(ai_to_col - ai_from_col) == 2:
            print(f"AI attempting castling - {ai_piece_color} king from {files[ai_from_col]}{ranks[ai_from_row]} "
                  f"to {files[ai_to_col]}{ranks[ai_to_row]}")
            print("Board coordinates reference:")
            print("   a b c d e f g h")
            for i in range(8):
                print(f"{8-i} {'.' * 15}")
    
    if ai_analysis:
        ai_from_row, ai_from_col, ai_to_row, ai_to_col = ai_analysis['coordinates']
    
        # Check if AI's move is a capture before making it
        ai_is_capture = current_board[ai_to_row][ai_to_col] != ' '
        
        # Make AI's move
        ai_from_square, ai_to_square = make_move(ai_from_row, ai_from_col, ai_to_row, ai_to_col)
        
        # Check if player is in check after AI's move
        ai_is_check = is_in_check(player_color, current_board)
        
        # Get analysis for AI's move
        ai_move_analysis = analyze_move(
            current_board, ai_from_row, ai_from_col, ai_to_row, ai_to_col,
            ai_is_capture, ai_is_check, ai_analysis
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
                'castling_info': castling_info,
                'ai_move': {
                    'from_row': ai_from_row,
                    'from_col': ai_from_col,
                    'to_row': ai_to_row,
                    'to_col': ai_to_col,
                    'is_castling': piece_type == 'king' and abs(ai_to_col - ai_from_col) == 2,
                    'castling_info': {
                        'rook_from_col': 0 if ai_to_col < ai_from_col else 7,
                        'rook_to_col': ai_to_col + 1 if ai_to_col < ai_from_col else ai_to_col - 1,
                        'row': ai_from_row
                    } if piece_type == 'king' and abs(ai_to_col - ai_from_col) == 2 else None
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
            'castling_info': castling_info,
            'ai_move': {
                'from_row': ai_from_row,
                'from_col': ai_from_col,
                'to_row': ai_to_row,
                'to_col': ai_to_col,
                'is_castling': piece_type == 'king' and abs(ai_to_col - ai_from_col) == 2,
                'castling_info': {
                    'rook_from_col': 0 if ai_to_col < ai_from_col else 7,
                    'rook_to_col': ai_to_col + 1 if ai_to_col < ai_from_col else ai_to_col - 1,
                    'row': ai_from_row
                } if piece_type == 'king' and abs(ai_to_col - ai_from_col) == 2 else None
            } if ai_move else None,
            'ai_move_analysis': ai_move_analysis
        })
    
    # Construct AI move data if available
    ai_move_data = None
    if ai_analysis:
        ai_move_data = {
            'from_row': ai_from_row,
            'from_col': ai_from_col,
            'to_row': ai_to_row,
            'to_col': ai_to_col,
            'is_castling': piece_type == 'king' and abs(ai_to_col - ai_from_col) == 2
        }
        if ai_move_data['is_castling']:
            ai_move_data['castling_info'] = {
                'rook_from_col': 0 if ai_to_col < ai_from_col else 7,
                'rook_to_col': ai_to_col + 1 if ai_to_col < ai_from_col else ai_to_col - 1,
                'row': ai_from_row
            }

    return jsonify({
        'valid': True,
        'board': current_board,
        'current_turn': current_turn,
        'game_over': False,
        'winner': None,
        'in_check': False,
        'move_analysis': player_move_analysis,
        'castling_info': castling_info,
        'ai_move': ai_move_data,
        'ai_move_analysis': ai_move_analysis
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy"
    })

if __name__ == '__main__':
    app.run(debug=True)
