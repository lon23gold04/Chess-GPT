from ai_engine import get_piece_type, get_piece_color

class ChessGame:
    def __init__(self):
        self.board = None
        self.current_turn = 'white'
        self.game_over = False
        self.winner = None
        self.player_color = None
        self.is_player_turn = True
        self.king_moved = {'white': False, 'black': False}
        self.rook_moved = {'white': [False, False], 'black': [False, False]}  # [left rook, right rook]

    def create_initial_board(self):
        """Initialize the chess board with pieces in starting positions."""
        pieces = {
            'white': {'king': '♔', 'queen': '♕', 'rook': '♖',
                     'bishop': '♗', 'knight': '♘', 'pawn': '♙'},
            'black': {'king': '♚', 'queen': '♛', 'rook': '♜',
                     'bishop': '♝', 'knight': '♞', 'pawn': '♟'}
        }
        
        self.board = [[' ' for _ in range(8)] for _ in range(8)]
        
        # Set up black pieces
        self.board[0] = [pieces['black']['rook'], pieces['black']['knight'], pieces['black']['bishop'],
                        pieces['black']['queen'], pieces['black']['king'], pieces['black']['bishop'],
                        pieces['black']['knight'], pieces['black']['rook']]
        self.board[1] = [pieces['black']['pawn']] * 8
        
        # Set up white pieces
        self.board[6] = [pieces['white']['pawn']] * 8
        self.board[7] = [pieces['white']['rook'], pieces['white']['knight'], pieces['white']['bishop'],
                        pieces['white']['queen'], pieces['white']['king'], pieces['white']['bishop'],
                        pieces['white']['knight'], pieces['white']['rook']]
        
        return self.board

    def is_valid_move(self, from_row, from_col, to_row, to_col):
        """Check if a move is valid according to chess rules."""
        # Basic boundary check
        if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
            return False
        
        piece = self.board[from_row][from_col]
        if piece == ' ':
            return False
        
        piece_color = get_piece_color(piece)
        if piece_color != self.current_turn:
            return False
        
        if not self._is_valid_piece_move(from_row, from_col, to_row, to_col):
            return False
        
        if self._would_be_in_check(from_row, from_col, to_row, to_col):
            return False

        return True

    def _is_valid_piece_move(self, from_row, from_col, to_row, to_col):
        """Validate move based on piece-specific rules."""
        piece = self.board[from_row][from_col]
        piece_color = get_piece_color(piece)
        piece_type = get_piece_type(piece)
        
        target_piece = self.board[to_row][to_col]
        if target_piece != ' ' and get_piece_color(target_piece) == piece_color:
            return False
        
        if piece_type == 'pawn':
            return self._is_valid_pawn_move(from_row, from_col, to_row, to_col, piece_color)
        elif piece_type == 'knight':
            return self._is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'bishop':
            return self._is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'rook':
            return self._is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'queen':
            return self._is_valid_bishop_move(from_row, from_col, to_row, to_col) or \
                   self._is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece_type == 'king':
            if abs(to_col - from_col) == 2:  # Castling
                return True
            return abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1
        return False

    def _is_valid_pawn_move(self, from_row, from_col, to_row, to_col, color):
        """Validate pawn move."""
        direction = -1 if color == 'white' else 1
        start_row = 6 if color == 'white' else 1
        
        # Forward move
        if from_col == to_col and to_row == from_row + direction and self.board[to_row][to_col] == ' ':
            return True
        
        # Initial two-square move
        if from_row == start_row and from_col == to_col and to_row == from_row + 2 * direction:
            if self.board[to_row][to_col] == ' ' and self.board[from_row + direction][from_col] == ' ':
                return True
        
        # Capture
        if to_row == from_row + direction and abs(to_col - from_col) == 1:
            if self.board[to_row][to_col] != ' ' and get_piece_color(self.board[to_row][to_col]) != color:
                return True
        
        return False

    def _is_valid_knight_move(self, from_row, from_col, to_row, to_col):
        """Validate knight move."""
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def _is_valid_bishop_move(self, from_row, from_col, to_row, to_col):
        """Validate bishop move."""
        if abs(to_row - from_row) != abs(to_col - from_col):
            return False
        
        row_step = 1 if to_row > from_row else -1
        col_step = 1 if to_col > from_col else -1
        
        current_row, current_col = from_row + row_step, from_col + col_step
        while current_row != to_row:
            if self.board[current_row][current_col] != ' ':
                return False
            current_row += row_step
            current_col += col_step
        
        return True

    def _is_valid_rook_move(self, from_row, from_col, to_row, to_col):
        """Validate rook move."""
        if from_row != to_row and from_col != to_col:
            return False
        
        if from_row == to_row:
            step = 1 if to_col > from_col else -1
            for col in range(from_col + step, to_col, step):
                if self.board[from_row][col] != ' ':
                    return False
        else:
            step = 1 if to_row > from_row else -1
            for row in range(from_row + step, to_row, step):
                if self.board[row][from_col] != ' ':
                    return False
        
        return True

    def _would_be_in_check(self, from_row, from_col, to_row, to_col):
        """Check if move would leave king in check."""
        temp_board = [row[:] for row in self.board]
        temp_board[to_row][to_col] = temp_board[from_row][from_col]
        temp_board[from_row][from_col] = ' '
        return self._is_in_check(get_piece_color(self.board[from_row][from_col]), temp_board)

    def _is_in_check(self, color, board):
        """Check if the given color's king is in check."""
        king_pos = self._find_king(board, color)
        if not king_pos:
            return False
        
        opponent_color = 'black' if color == 'white' else 'white'
        return self._is_square_under_attack(king_pos[0], king_pos[1], opponent_color, board)

    def _find_king(self, board, color):
        """Find the position of the king of given color."""
        king_symbol = '♔' if color == 'white' else '♚'
        for row in range(8):
            for col in range(8):
                if board[row][col] == king_symbol:
                    return row, col
        return None

    def _is_square_under_attack(self, row, col, attacking_color, board):
        """Check if a square is under attack by any piece of the attacking color."""
        for i in range(8):
            for j in range(8):
                piece = board[i][j]
                if piece != ' ' and get_piece_color(piece) == attacking_color:
                    if self._is_valid_attack_move(i, j, row, col, board):
                        return True
        return False

    def _is_valid_attack_move(self, from_row, from_col, to_row, to_col, board):
        """Check if a piece could theoretically move to attack a square."""
        piece = board[from_row][from_col]
        piece_type = get_piece_type(piece)
        
        if piece_type == 'pawn':
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

    def make_move(self, from_row, from_col, to_row, to_col):
        """Make a move on the board and update game state."""
        piece = self.board[from_row][from_col]
        piece_type = get_piece_type(piece)
        
        is_castling = piece_type == 'king' and abs(to_col - from_col) == 2
        
        if is_castling:
            rook_col = 0 if to_col < from_col else 7
            new_rook_col = 3 if to_col < from_col else 5
            rook = self.board[from_row][rook_col]
            
            # Move king
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = ' '
            # Move rook
            self.board[from_row][new_rook_col] = rook
            self.board[from_row][rook_col] = ' '
            
            # Update castling flags
            self.king_moved[self.current_turn] = True
            self.rook_moved[self.current_turn][0 if rook_col == 0 else 1] = True
        else:
            # Make normal move
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = ' '
            
            # Update castling flags
            if piece_type == 'king':
                self.king_moved[self.current_turn] = True
            elif piece_type == 'rook':
                self.rook_moved[self.current_turn][0 if from_col == 0 else 1] = True
        
        # Switch turns
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.is_player_turn = not self.is_player_turn
        
        # Convert move to chess notation
        files = 'abcdefgh'
        ranks = '87654321'
        from_square = f'{files[from_col]}{ranks[from_row]}'
        to_square = f'{files[to_col]}{ranks[to_row]}'
        
        return from_square, to_square

    def to_fen(self):
        """Convert current board position to FEN notation."""
        piece_to_fen = {
            '♔': 'K', '♕': 'Q', '♖': 'R', '♗': 'B', '♘': 'N', '♙': 'P',
            '♚': 'k', '♛': 'q', '♜': 'r', '♝': 'b', '♞': 'n', '♟': 'p',
            ' ': '1'
        }
        
        fen_parts = []
        for row in self.board:
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
        
        position = '/'.join(fen_parts)
        turn = 'w' if self.current_turn == 'white' else 'b'
        
        castling = ''
        if not self.king_moved['white']:
            if not self.rook_moved['white'][1]:
                castling += 'K'
            if not self.rook_moved['white'][0]:
                castling += 'Q'
        if not self.king_moved['black']:
            if not self.rook_moved['black'][1]:
                castling += 'k'
            if not self.rook_moved['black'][0]:
                castling += 'q'
        if not castling:
            castling = '-'
        
        return f"{position} {turn} {castling} - 0 1" 