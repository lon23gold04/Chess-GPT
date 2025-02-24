import requests
import google.generativeai as genai

def get_ai_move(fen):
    """Get the best move from the chess API."""
    try:
        response = requests.post('https://chess-api.com/v1', 
            json={
                'fen': fen,
                'depth': 12,
                'variants': 1
            }
        )
        data = response.json()
        if 'move' in data:
            move = data['move']
            from_col = ord(move[0]) - ord('a')
            from_row = 8 - int(move[1])
            to_col = ord(move[2]) - ord('a')
            to_row = 8 - int(move[3])

            return {
                'text': data.get('text', 'No description available'),
                'win_chance': data.get('winChance', None),
                'mate': data.get('mate', None),
                'coordinates': (from_row, from_col, to_row, to_col)
            }
    except Exception as e:
        print(f"Error getting AI move: {e}")
    return None

def analyze_move(model, board, from_row, from_col, to_row, to_col, is_capture, is_check, engine_analysis=None):
    """Analyze a move using Gemini AI."""
    files = 'abcdefgh'
    ranks = '87654321'
    from_square = f"{files[from_col]}{ranks[from_row]}"
    to_square = f"{files[to_col]}{ranks[to_row]}"
    
    piece = board[from_row][from_col]
    piece_type = get_piece_type(piece)
    piece_color = get_piece_color(piece)
    
    board_str = format_board_string(board)
    move_desc = format_move_description(piece_color, piece_type, from_square, to_square, 
                                      is_capture, is_check, board, to_row, to_col)
    engine_info = format_engine_info(engine_analysis)
    
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

def format_board_string(board):
    """Format the board state as a string."""
    board_str = "\nCurrent board position:\n"
    for row in range(8):
        board_str += f"{8-row} "
        for col in range(8):
            piece = board[row][col]
            board_str += f"{piece if piece != ' ' else '.'} "
        board_str += "\n"
    board_str += "  a b c d e f g h\n"
    return board_str

def format_move_description(piece_color, piece_type, from_square, to_square, 
                          is_capture, is_check, board, to_row, to_col):
    """Format the move description."""
    move_desc = f"Move analysis request: {piece_color} {piece_type} from {from_square} to {to_square}"
    if is_capture:
        captured_piece = board[to_row][to_col]
        captured_type = get_piece_type(captured_piece)
        move_desc += f", capturing {get_piece_color(captured_piece)} {captured_type}"
    if is_check:
        move_desc += ", putting opponent in check"
    return move_desc

def format_engine_info(engine_analysis):
    """Format the engine analysis information."""
    if not engine_analysis:
        return ""
    
    engine_info = f"""
    Engine Analysis:
    - Description: {engine_analysis.get('text', 'No description available')}
    - Win Probability: {engine_analysis.get('win_chance', 'Not available')}"""
    if engine_analysis.get('mate'):
        engine_info += f"\n    - Mate in: {engine_analysis['mate']} moves"
    return engine_info

def get_piece_type(piece):
    """Get the type of a chess piece."""
    piece_types = {
        '♔': 'king', '♚': 'king',
        '♕': 'queen', '♛': 'queen',
        '♖': 'rook', '♜': 'rook',
        '♗': 'bishop', '♝': 'bishop',
        '♘': 'knight', '♞': 'knight',
        '♙': 'pawn', '♟': 'pawn'
    }
    return piece_types.get(piece)

def get_piece_color(piece):
    """Get the color of a chess piece."""
    white_pieces = '♔♕♖♗♘♙'
    black_pieces = '♚♛♜♝♞♟'
    if piece in white_pieces:
        return 'white'
    elif piece in black_pieces:
        return 'black'
    return None 