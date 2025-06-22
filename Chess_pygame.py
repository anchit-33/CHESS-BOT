import pygame as pg
import chess
import sys
import os
from Chess_Bot import ChessBot

# Constants
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Game states
MENU_STATE = 0
GAME_STATE = 1
PROMOTION_STATE = 2

def load_images():
    """Load the chess piece images"""
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        # Use the path to the images folder
        image_path = os.path.join("images", piece + ".png")
        IMAGES[piece] = pg.transform.scale(pg.image.load(image_path), (SQ_SIZE, SQ_SIZE))

def draw_board(screen):
    """Draw the chess board"""
    colors = [pg.Color("white"), pg.Color("pink")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pg.draw.rect(screen, color, pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    """Draw the pieces on the board"""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def convert_chess_piece_to_pygame(piece):
    """Convert a chess.py piece to the corresponding image key"""
    if piece is None:
        return "--"
    
    piece_symbol = piece.symbol()
    color_prefix = "w" if piece_symbol.isupper() else "b"
    piece_type = piece_symbol.upper()
    
    # Map chess.py piece symbols to our image keys
    if piece_type == "P":
        return color_prefix + "p"
    elif piece_type == "R":
        return color_prefix + "R"
    elif piece_type == "N":
        return color_prefix + "N"
    elif piece_type == "B":
        return color_prefix + "B"
    elif piece_type == "Q":
        return color_prefix + "Q"
    elif piece_type == "K":
        return color_prefix + "K"
    
    return "--"

def convert_board_to_pygame_format(chess_board):
    """Convert a chess.py board to a 2D array for pygame rendering"""
    board_2d = []
    # Reversed the board to show player at bottom and bot at top
    for r in range(7, -1, -1):  # Start from rank 7 and go to rank 0
        row = []
        for c in range(8):
            square = chess.square(c, r)
            piece = chess_board.piece_at(square)
            row.append(convert_chess_piece_to_pygame(piece))
        board_2d.append(row)
    return board_2d

def draw_start_menu(screen, font, selected_difficulty):
    """Draw the starting menu"""
    screen.fill(pg.Color("white"))
    
    # Title
    title_font = pg.font.SysFont('Arial', 48, bold=True)
    title_text = title_font.render('Chess Bot', True, pg.Color("black"))
    title_rect = title_text.get_rect(center=(WIDTH//2, 100))
    screen.blit(title_text, title_rect)
    
    # Subtitle
    subtitle_font = pg.font.SysFont('Arial', 24)
    subtitle_text = subtitle_font.render('Choose your difficulty level', True, pg.Color("gray"))
    subtitle_rect = subtitle_text.get_rect(center=(WIDTH//2, 150))
    screen.blit(subtitle_text, subtitle_rect)
    
    # Difficulty buttons
    button_width = 150
    button_height = 60
    button_spacing = 30
    start_y = 220
    
    easy_button = pg.Rect((WIDTH - button_width) // 2, start_y, button_width, button_height)
    medium_button = pg.Rect((WIDTH - button_width) // 2, start_y + button_height + button_spacing, button_width, button_height)
    hard_button = pg.Rect((WIDTH - button_width) // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)
    
    # Draw difficulty buttons
    difficulties = ['Easy', 'Medium', 'Hard']
    buttons = [easy_button, medium_button, hard_button]
    colors = ['easy', 'medium', 'hard']
    
    for i, (button, difficulty, color_key) in enumerate(zip(buttons, difficulties, colors)):
        if selected_difficulty == color_key:
            pg.draw.rect(screen, pg.Color("lightblue"), button)
            pg.draw.rect(screen, pg.Color("blue"), button, 3)
        else:
            pg.draw.rect(screen, pg.Color("lightgray"), button)
            pg.draw.rect(screen, pg.Color("black"), button, 2)
        
        text = font.render(difficulty, True, pg.Color("black"))
        text_rect = text.get_rect(center=button.center)
        screen.blit(text, text_rect)
    
    # Start button
    start_button = pg.Rect((WIDTH - button_width) // 2, start_y + 3 * (button_height + button_spacing), button_width, button_height)
    pg.draw.rect(screen, pg.Color("green"), start_button)
    pg.draw.rect(screen, pg.Color("darkgreen"), start_button, 3)
    
    start_text = font.render('START GAME', True, pg.Color("white"))
    start_text_rect = start_text.get_rect(center=start_button.center)
    screen.blit(start_text, start_text_rect)
    
    return easy_button, medium_button, hard_button, start_button

def draw_promotion_dialog(screen, font, player_color):
    """Draw promotion piece selection dialog"""
    # Semi-transparent overlay
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(pg.Color("black"))
    screen.blit(overlay, (0, 0))
    
    # Dialog box
    dialog_width = 400
    dialog_height = 200
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = (HEIGHT - dialog_height) // 2
    dialog_rect = pg.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    
    pg.draw.rect(screen, pg.Color("white"), dialog_rect)
    pg.draw.rect(screen, pg.Color("black"), dialog_rect, 3)
    
    # Title
    title_text = font.render('Choose promotion piece:', True, pg.Color("black"))
    title_rect = title_text.get_rect(center=(WIDTH//2, dialog_y + 30))
    screen.blit(title_text, title_rect)
    
    # Piece buttons
    piece_size = 60
    piece_spacing = 20
    total_width = 4 * piece_size + 3 * piece_spacing
    start_x = (WIDTH - total_width) // 2
    piece_y = dialog_y + 80
    
    # Color prefix for pieces
    color_prefix = "w" if player_color == chess.WHITE else "b"
    
    # Create buttons for Queen, Rook, Bishop, Knight
    pieces = ['Q', 'R', 'B', 'N']
    piece_names = ['Queen', 'Rook', 'Bishop', 'Knight']
    buttons = []
    
    for i, (piece, name) in enumerate(zip(pieces, piece_names)):
        x = start_x + i * (piece_size + piece_spacing)
        button_rect = pg.Rect(x, piece_y, piece_size, piece_size)
        buttons.append(button_rect)
        
        # Draw button
        pg.draw.rect(screen, pg.Color("lightgray"), button_rect)
        pg.draw.rect(screen, pg.Color("black"), button_rect, 2)
        
        # Draw piece image if available
        piece_key = color_prefix + piece
        if piece_key in IMAGES:
            piece_image = pg.transform.scale(IMAGES[piece_key], (piece_size - 10, piece_size - 10))
            screen.blit(piece_image, (x + 5, piece_y + 5))
        
        # Draw piece name below
        name_text = pg.font.SysFont('Arial', 12).render(name, True, pg.Color("black"))
        name_rect = name_text.get_rect(center=(x + piece_size//2, piece_y + piece_size + 15))
        screen.blit(name_text, name_rect)
    
    return buttons

def main():
    """Main function to run the game"""
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT + 100))  # Extra space for status
    clock = pg.time.Clock()
    
    # Game state
    game_state = MENU_STATE
    selected_difficulty = 'medium'  # Default difficulty
    
    # Font for text
    font = pg.font.SysFont('Arial', 20)
    
    # Game variables (initialized when game starts)
    chess_board = None
    pygame_board = None
    bot = None
    selected_square = None
    player_color = chess.WHITE  # Player plays as white (bottom)
    game_over = False
    status_message = ""
    
    # Promotion variables
    promotion_move = None
    promotion_buttons = []
    
    # Load images
    load_images()
    
    # Main game loop
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()
                
                if game_state == MENU_STATE:
                    # Handle menu clicks
                    easy_button, medium_button, hard_button, start_button = draw_start_menu(screen, font, selected_difficulty)
                    
                    if easy_button.collidepoint(location):
                        selected_difficulty = 'easy'
                    elif medium_button.collidepoint(location):
                        selected_difficulty = 'medium'
                    elif hard_button.collidepoint(location):
                        selected_difficulty = 'hard'
                    elif start_button.collidepoint(location):
                        # Start the game
                        chess_board = chess.Board()
                        pygame_board = convert_board_to_pygame_format(chess_board)
                        bot = ChessBot(difficulty=selected_difficulty)
                        selected_square = None
                        game_over = False
                        status_message = "Your turn (White)"
                        game_state = GAME_STATE
                
                elif game_state == PROMOTION_STATE:
                    # Handle promotion piece selection
                    for i, button in enumerate(promotion_buttons):
                        if button.collidepoint(location):
                            pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
                            selected_piece = pieces[i]
                            
                            # Create the promotion move
                            final_move = chess.Move(promotion_move.from_square, promotion_move.to_square, promotion=selected_piece)
                            
                            # Make the move
                            chess_board.push(final_move)
                            pygame_board = convert_board_to_pygame_format(chess_board)
                            selected_square = None
                            promotion_move = None
                            game_state = GAME_STATE
                            
                            # Check if the game is over
                            if chess_board.is_checkmate():
                                status_message = "Checkmate! You win!"
                                game_over = True
                            elif chess_board.is_stalemate() or chess_board.is_insufficient_material():
                                status_message = "Draw!"
                                game_over = True
                            else:
                                # Bot's turn
                                status_message = f"Bot is thinking... ({selected_difficulty} difficulty)"
                                
                                # Update display before bot moves
                                screen.fill(pg.Color("white"))
                                draw_board(screen)
                                draw_pieces(screen, pygame_board)
                                status_text = font.render(status_message, True, pg.Color("black"))
                                screen.blit(status_text, (10, HEIGHT + 10))
                                pg.display.flip()
                                
                                # Get bot's move
                                bot_move = bot.get_best_move(chess_board)
                                
                                # Make bot's move
                                chess_board.push(bot_move)
                                pygame_board = convert_board_to_pygame_format(chess_board)
                                
                                # Check if the game is over after bot's move
                                if chess_board.is_checkmate():
                                    status_message = "Checkmate! Bot wins!"
                                    game_over = True
                                elif chess_board.is_stalemate() or chess_board.is_insufficient_material():
                                    status_message = "Draw!"
                                    game_over = True
                                else:
                                    status_message = "Your turn"
                            break
                
                elif game_state == GAME_STATE:
                    # Handle game clicks
                    if not game_over and chess_board.turn == player_color and location[1] < HEIGHT:
                        col = location[0] // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        
                        # Convert pygame coordinates to chess coordinates (reversed board)
                        chess_row = 7 - row
                        chess_col = col
                        
                        # If the same square is selected, deselect it
                        if selected_square == (row, col):
                            selected_square = None
                        else:
                            # Check if a piece was selected previously
                            if selected_square:
                                # Try to make a move
                                start_chess_row = 7 - selected_square[0]
                                start_chess_col = selected_square[1]
                                start_square = chess.square(start_chess_col, start_chess_row)
                                end_square = chess.square(chess_col, chess_row)
                                
                                # Check for pawn promotion
                                piece = chess_board.piece_at(start_square)
                                if (piece is not None and piece.piece_type == chess.PAWN and 
                                    ((chess_row == 7 and player_color == chess.WHITE) or 
                                     (chess_row == 0 and player_color == chess.BLACK))):
                                    # This is a promotion move
                                    promotion_move = chess.Move(start_square, end_square)
                                    if promotion_move in chess_board.legal_moves:
                                        game_state = PROMOTION_STATE
                                    else:
                                        # Illegal move, try to select new square
                                        square = chess.square(chess_col, chess_row)
                                        piece = chess_board.piece_at(square)
                                        if piece is not None and piece.color == player_color:
                                            selected_square = (row, col)
                                        else:
                                            selected_square = None
                                else:
                                    # Regular move
                                    move = chess.Move(start_square, end_square)
                                    
                                    # Check if the move is legal
                                    if move in chess_board.legal_moves:
                                        # Make the move
                                        chess_board.push(move)
                                        pygame_board = convert_board_to_pygame_format(chess_board)
                                        selected_square = None
                                        
                                        # Check if the game is over
                                        if chess_board.is_checkmate():
                                            status_message = "Checkmate! You win!"
                                            game_over = True
                                        elif chess_board.is_stalemate() or chess_board.is_insufficient_material():
                                            status_message = "Draw!"
                                            game_over = True
                                        else:
                                            # Bot's turn
                                            status_message = f"Bot is thinking... ({selected_difficulty} difficulty)"
                                            
                                            # Update display before bot moves
                                            screen.fill(pg.Color("white"))
                                            draw_board(screen)
                                            draw_pieces(screen, pygame_board)
                                            status_text = font.render(status_message, True, pg.Color("black"))
                                            screen.blit(status_text, (10, HEIGHT + 10))
                                            pg.display.flip()
                                            
                                            # Get bot's move
                                            bot_move = bot.get_best_move(chess_board)
                                            
                                            # Make bot's move
                                            chess_board.push(bot_move)
                                            pygame_board = convert_board_to_pygame_format(chess_board)
                                            
                                            # Check if the game is over after bot's move
                                            if chess_board.is_checkmate():
                                                status_message = "Checkmate! Bot wins!"
                                                game_over = True
                                            elif chess_board.is_stalemate() or chess_board.is_insufficient_material():
                                                status_message = "Draw!"
                                                game_over = True
                                            else:
                                                status_message = "Your turn"
                                    else:
                                        # Illegal move, try to select new square
                                        square = chess.square(chess_col, chess_row)
                                        piece = chess_board.piece_at(square)
                                        if piece is not None and piece.color == player_color:
                                            selected_square = (row, col)
                                        else:
                                            selected_square = None
                            else:
                                # No piece was selected previously
                                square = chess.square(chess_col, chess_row)
                                piece = chess_board.piece_at(square)
                                if piece is not None and piece.color == player_color:
                                    selected_square = (row, col)
        
        # Drawing
        if game_state == MENU_STATE:
            draw_start_menu(screen, font, selected_difficulty)
        
        elif game_state == GAME_STATE:
            screen.fill(pg.Color("white"))
            draw_board(screen)
            
            # Highlight selected square
            if selected_square:
                s = pg.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(100)
                s.fill(pg.Color('blue'))
                screen.blit(s, (selected_square[1] * SQ_SIZE, selected_square[0] * SQ_SIZE))
            
            draw_pieces(screen, pygame_board)
            
            # Draw status message
            status_text = font.render(status_message, True, pg.Color("black"))
            screen.blit(status_text, (10, HEIGHT + 10))
            
            # Draw new game button
            new_game_button = pg.Rect(10, HEIGHT + 40, 100, 30)
            pg.draw.rect(screen, pg.Color("light gray"), new_game_button)
            pg.draw.rect(screen, pg.Color("black"), new_game_button, 2)
            new_game_text = font.render('New Game', True, pg.Color("black"))
            screen.blit(new_game_text, (new_game_button.x + 10, new_game_button.y + 5))
            
            # Handle new game button click
            if pg.mouse.get_pressed()[0]:
                mouse_pos = pg.mouse.get_pos()
                if new_game_button.collidepoint(mouse_pos):
                    game_state = MENU_STATE
        
        elif game_state == PROMOTION_STATE:
            # Draw the game board first
            screen.fill(pg.Color("white"))
            draw_board(screen)
            draw_pieces(screen, pygame_board)
            
            # Draw promotion dialog
            promotion_buttons = draw_promotion_dialog(screen, font, player_color)
        
        # Update display
        pg.display.flip()
        clock.tick(MAX_FPS)
    
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()