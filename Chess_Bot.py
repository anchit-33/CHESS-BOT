import chess
import random
import time
from collections import OrderedDict

class LRUCache:
    """Limited-size LRU cache for transposition table"""
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

class ChessBot:
    def __init__(self, difficulty='medium'):
        """
        Initialize chess bot with difficulty level
        :param difficulty: 'easy', 'medium', or 'hard'
        """
        self.difficulty = difficulty
        # Set search depth based on difficulty
        if difficulty == 'easy':
            self.max_depth = 2
        elif difficulty == 'medium':
            self.max_depth = 3
        else:  # hard
            self.max_depth = 4
            
        # Initialize transposition table with appropriate size for each difficulty
        if difficulty == 'easy':
            self.transposition_table = LRUCache(10000)  # Smaller cache for easy
        elif difficulty == 'medium':
            self.transposition_table = LRUCache(100000)  # Medium-sized cache
        else:  # hard
            self.transposition_table = LRUCache(1000000)  # Large cache for hard
            
        # Piece values
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Piece-square tables for positional evaluation
        self.pawn_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        self.knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50,
        ]
        
        self.bishop_table = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5,  5,  5,  5,  5,-10,
            -10,  0,  5,  0,  0,  5,  0,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,
        ]
        
        self.rook_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            0,  0,  0,  5,  5,  0,  0,  0
        ]
        
        self.queen_table = [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -5,  0,  5,  5,  5,  5,  0, -5,
            0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]
        
        self.king_table_middlegame = [
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
            20, 20,  0,  0,  0,  0, 20, 20,
            20, 30, 10,  0,  0, 10, 30, 20
        ]
        
        self.king_table_endgame = [
            -50,-40,-30,-20,-20,-30,-40,-50,
            -30,-20,-10,  0,  0,-10,-20,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-30,  0,  0,  0,  0,-30,-30,
            -50,-30,-30,-30,-30,-30,-30,-50
        ]
        
        self.piece_tables = {
            chess.PAWN: self.pawn_table,
            chess.KNIGHT: self.knight_table,
            chess.BISHOP: self.bishop_table,
            chess.ROOK: self.rook_table,
            chess.QUEEN: self.queen_table,
            chess.KING: self.king_table_middlegame
        }
        
        # Statistics for performance monitoring
        self.nodes_evaluated = 0
        self.cache_hits = 0
        self.start_time = 0
    
    def get_best_move(self, board):
        """Find the best move using minimax with alpha-beta pruning and transposition table"""
        self.nodes_evaluated = 0
        self.cache_hits = 0
        self.start_time = time.time()
        
        # For easy difficulty, sometimes make a random legal move
        if self.difficulty == 'easy' and random.random() < 0.3:
            legal_moves = list(board.legal_moves)
            return random.choice(legal_moves)
        
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        max_eval = float('-inf')
        
        # Order moves to improve alpha-beta pruning efficiency
        moves = self.order_moves(board)
        
        for move in moves:
            board.push(move)
            eval = self.minimax(board, self.max_depth - 1, alpha, beta, False)
            board.pop()
            
            if eval > max_eval:
                max_eval = eval
                best_move = move
            
            alpha = max(alpha, eval)
        
        end_time = time.time()
        print(f"Bot Move Analysis ({self.difficulty} difficulty):")
        print(f"- Nodes evaluated: {self.nodes_evaluated}")
        print(f"- Cache hits: {self.cache_hits}")
        print(f"- Time taken: {end_time - self.start_time:.2f} seconds")
        print(f"- Nodes per second: {self.nodes_evaluated / (end_time - self.start_time):.0f}")
        
        return best_move if best_move else random.choice(list(board.legal_moves))
    
    def minimax(self, board, depth, alpha, beta, is_maximizing):
        """Minimax algorithm with alpha-beta pruning and transposition table"""
        self.nodes_evaluated += 1
        
        # Check for terminal state
        if board.is_checkmate():
            return -10000 if is_maximizing else 10000
        elif board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        # Transposition table lookup
        board_hash = self.get_board_hash(board)
        cached_entry = self.transposition_table.get(board_hash)
        if cached_entry and cached_entry[0] >= depth:
            self.cache_hits += 1
            return cached_entry[1]
        
        # Leaf node evaluation
        if depth == 0:
            evaluation = self.evaluate_board(board)
            self.transposition_table.put(board_hash, (depth, evaluation))
            return evaluation
        
        # Order moves to improve alpha-beta pruning efficiency
        moves = self.order_moves(board)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            self.transposition_table.put(board_hash, (depth, max_eval))
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            self.transposition_table.put(board_hash, (depth, min_eval))
            return min_eval
    
    def order_moves(self, board):
        """Order moves to improve alpha-beta pruning efficiency"""
        # Simple move ordering: captures first, then other moves
        moves = list(board.legal_moves)
        move_scores = []
        
        for move in moves:
            score = 0
            # Prioritize captures by MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
            if board.is_capture(move):
                victim_piece = board.piece_at(move.to_square)
                if victim_piece:
                    victim_value = self.piece_values.get(victim_piece.piece_type, 0)
                    aggressor = board.piece_at(move.from_square)
                    if aggressor:
                        aggressor_value = self.piece_values.get(aggressor.piece_type, 0)
                        score = 10 * victim_value - aggressor_value
                else:
                    # En passant capture
                    score = 100  # Pawn value
            
            # Prioritize promotions
            if move.promotion:
                score += self.piece_values[move.promotion]
            
            # Check and checkmate threats (simple approximation)
            board.push(move)
            if board.is_check():
                score += 50
            board.pop()
            
            move_scores.append((move, score))
        
        # Sort moves by score in descending order
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]
    
    def get_board_hash(self, board):
        """Generate a unique hash for the board position"""
        return board.fen()
    
    def evaluate_board(self, board):
        """
        Evaluate the board position
        Positive score favors white, negative score favors black
        """
        if board.is_checkmate():
            # If checkmate, return a high score favoring the winner
            return -10000 if board.turn else 10000
            
        if board.is_stalemate() or board.is_insufficient_material():
            return 0  # Draw
            
        # Material evaluation
        material_score = self.evaluate_material(board)
        
        # Positional evaluation
        positional_score = self.evaluate_position(board)
        
        # Mobility evaluation (number of legal moves)
        mobility_score = self.evaluate_mobility(board)
        
        # King safety evaluation
        king_safety_score = self.evaluate_king_safety(board)
        
        # Pawn structure evaluation
        pawn_structure_score = self.evaluate_pawn_structure(board)
        
        total_score = (
            material_score +
            positional_score +
            0.1 * mobility_score +
            0.2 * king_safety_score +
            0.1 * pawn_structure_score
        )
        
        # Perspective adjustment - positive is good for the current player
        return total_score if board.turn == chess.WHITE else -total_score
    
    def evaluate_material(self, board):
        """Evaluate material balance"""
        score = 0
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values[piece.piece_type]
                score += value if piece.color == chess.WHITE else -value
                
        return score
    
    def evaluate_position(self, board):
        """Evaluate piece positions using piece-square tables"""
        score = 0
        
        # Determine game phase for king table selection
        is_endgame = self.is_endgame(board)
        king_table = self.king_table_endgame if is_endgame else self.king_table_middlegame
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Get appropriate piece-square table
                if piece.piece_type == chess.KING:
                    table = king_table
                else:
                    table = self.piece_tables[piece.piece_type]
                
                # Get position value
                if piece.color == chess.WHITE:
                    position_value = table[63 - square]
                else:
                    position_value = table[square]
                
                score += position_value if piece.color == chess.WHITE else -position_value
                
        return score
    
    def evaluate_mobility(self, board):
        """Evaluate mobility (number of legal moves)"""
        # Save the current turn
        original_turn = board.turn
        
        # Count white's moves
        board.turn = chess.WHITE
        white_moves = len(list(board.legal_moves))
        
        # Count black's moves
        board.turn = chess.BLACK
        black_moves = len(list(board.legal_moves))
        
        # Restore original turn
        board.turn = original_turn
        
        return white_moves - black_moves
    
    def evaluate_king_safety(self, board):
        """Evaluate king safety"""
        score = 0
        
        # Find king positions
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        
        # Evaluate pawn shield for white king
        if white_king_square:
            white_king_file = chess.square_file(white_king_square)
            white_king_rank = chess.square_rank(white_king_square)
            
            # Check pawns in front of the king (for white)
            if white_king_rank < 7:  # Not on the last rank
                for file_offset in [-1, 0, 1]:
                    if 0 <= white_king_file + file_offset <= 7:
                        pawn_square = chess.square(white_king_file + file_offset, white_king_rank + 1)
                        if board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.WHITE):
                            score += 10  # Bonus for each pawn shielding the king
        
        # Evaluate pawn shield for black king
        if black_king_square:
            black_king_file = chess.square_file(black_king_square)
            black_king_rank = chess.square_rank(black_king_square)
            
            # Check pawns in front of the king (for black)
            if black_king_rank > 0:  # Not on the first rank
                for file_offset in [-1, 0, 1]:
                    if 0 <= black_king_file + file_offset <= 7:
                        pawn_square = chess.square(black_king_file + file_offset, black_king_rank - 1)
                        if board.piece_at(pawn_square) == chess.Piece(chess.PAWN, chess.BLACK):
                            score -= 10  # Bonus for each pawn shielding the king
        
        return score
    
    def evaluate_pawn_structure(self, board):
        """Evaluate pawn structure"""
        score = 0
        
        # Evaluate doubled pawns
        for file in range(8):
            white_pawns_on_file = 0
            black_pawns_on_file = 0
            
            for rank in range(8):
                square = chess.square(file, rank)
                piece = board.piece_at(square)
                
                if piece and piece.piece_type == chess.PAWN:
                    if piece.color == chess.WHITE:
                        white_pawns_on_file += 1
                    else:
                        black_pawns_on_file += 1
            
            # Penalty for doubled pawns
            if white_pawns_on_file > 1:
                score -= 20 * (white_pawns_on_file - 1)
            if black_pawns_on_file > 1:
                score += 20 * (black_pawns_on_file - 1)
        
        # Evaluate isolated pawns
        for file in range(8):
            has_white_pawn_on_file = False
            has_black_pawn_on_file = False
            
            for rank in range(8):
                square = chess.square(file, rank)
                piece = board.piece_at(square)
                
                if piece and piece.piece_type == chess.PAWN:
                    if piece.color == chess.WHITE:
                        has_white_pawn_on_file = True
                    else:
                        has_black_pawn_on_file = True
            
            # Check for isolated pawns
            has_white_pawn_on_adjacent_file = False
            has_black_pawn_on_adjacent_file = False
            
            for adjacent_file in [file - 1, file + 1]:
                if 0 <= adjacent_file <= 7:
                    for rank in range(8):
                        square = chess.square(adjacent_file, rank)
                        piece = board.piece_at(square)
                        
                        if piece and piece.piece_type == chess.PAWN:
                            if piece.color == chess.WHITE:
                                has_white_pawn_on_adjacent_file = True
                            else:
                                has_black_pawn_on_adjacent_file = True
            
            # Penalty for isolated pawns
            if has_white_pawn_on_file and not has_white_pawn_on_adjacent_file:
                score -= 20
            if has_black_pawn_on_file and not has_black_pawn_on_adjacent_file:
                score += 20
        
        return score
    
    def is_endgame(self, board):
        """Determine if the position is an endgame"""
        # Simple endgame detection: no queens or at most one minor piece per side
        white_queens = len(board.pieces(chess.QUEEN, chess.WHITE))
        black_queens = len(board.pieces(chess.QUEEN, chess.BLACK))
        
        white_minors = (
            len(board.pieces(chess.KNIGHT, chess.WHITE)) +
            len(board.pieces(chess.BISHOP, chess.WHITE))
        )
        black_minors = (
            len(board.pieces(chess.KNIGHT, chess.BLACK)) +
            len(board.pieces(chess.BISHOP, chess.BLACK))
        )
        
        return (white_queens + black_queens == 0) or (white_minors <= 1 and black_minors <= 1)