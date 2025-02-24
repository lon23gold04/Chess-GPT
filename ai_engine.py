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
    # Get coordinates and piece information
    files, ranks = 'abcdefgh', '87654321'
    from_square = f"{files[from_col]}{ranks[from_row]}"
    to_square = f"{files[to_col]}{ranks[to_row]}"
    piece = board[from_row][from_col]
    
    # Handle castling edge case
    piece_type = get_piece_type(piece) if piece != ' ' else 'king'
    piece_color = get_piece_color(piece) if piece != ' ' else ('white' if from_row == 7 else 'black')
    is_castling = piece_type == 'king' and abs(ord(from_square[0]) - ord(to_square[0])) == 2
    
    # Build the move analysis prompt
    prompt = f"""
    As a chess expert, analyze this move:
    {_get_move_description(piece_color, piece_type, from_square, to_square, is_castling, is_capture, is_check, board, to_row, to_col)}
    {_format_engine_info(engine_analysis)}
    
    {_format_board(board)}
    
    Consider:
    1. Strategic value
    2. Position control
    3. Piece development
    4. Potential threats or opportunities
    
    Provide a brief, focused analysis (2-3 sentences) with concrete tactical or positional advantages.
    """
    
    # Get response from model
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error getting move analysis: {e}")
        return "Move analysis unavailable."

def _get_move_description(color, type, from_sq, to_sq, is_castling, is_capture, is_check, board, to_row, to_col):
    """Create a descriptive string of the move for analysis."""
    if is_castling:
        castling_type = "O-O" if ord(to_sq[0]) > ord(from_sq[0]) else "O-O-O"
        desc = f"Move analysis request: {color} {castling_type} (castling)"
    else:
        desc = f"Move analysis request: {color} {type} from {from_sq} to {to_sq}"
        if is_capture:
            captured = board[to_row][to_col]
            desc += f", capturing {get_piece_color(captured)} {get_piece_type(captured)}"
    
    return desc + (", putting opponent in check" if is_check else "")

def _format_board(board):
    """Format the board state as a string."""
    result = "\nCurrent board position:\n"
    for row in range(8):
        result += f"{8-row} "
        for col in range(8):
            piece = board[row][col]
            result += f"{piece if piece != ' ' else '.'} "
        result += "\n"
    return result + "  a b c d e f g h\n"

def _format_engine_info(engine_analysis):
    """Format the engine analysis information."""
    if not engine_analysis:
        return ""
    
    info = f"""
    Engine Analysis:
    - Description: {engine_analysis.get('text', 'No description available')}
    - Win Probability: {engine_analysis.get('win_chance', 'Not available')}"""
    
    if engine_analysis.get('mate'):
        info += f"\n    - Mate in: {engine_analysis['mate']} moves"
    return info

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