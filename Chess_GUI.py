import pygame as pg
import chess
import chess.svg
import cairosvg
import io
from Chess_Bot import ChessBot
import sys
import time
from PIL import Image

class ChessGame:
    def __init__(self, width=600, height=700):  # Increased height for start screen
        pg.init()
        self.width = width
        self.height = height
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption("Chess Bot")
        
        # Game states
        self.game_state = "start_screen"  # "start_screen" or "playing"
        self.selected_difficulty = 'medium'  # Default difficulty
        
        # Initialize chess board
        self.board = chess.Board()
        
        # Initialize the bot (will be set when game starts)
        self.bot = None
        
        # Game state
        self.selected_square = None
        self.player_color = chess.BLACK  # Reversed: Player plays as black (bottom)
        self.game_over = False
        self.result_message = ""
        
        # Font for rendering text
        self.font = pg.font.SysFont('Arial', 20)
        self.title_font = pg.font.SysFont('Arial', 36, bold=True)
        
        # Start screen UI elements
        self.start_button = pg.Rect(width//2 - 75, height//2 + 50, 150, 50)
        self.easy_button_start = pg.Rect(width//2 - 200, height//2 - 50, 120, 40)
        self.medium_button_start = pg.Rect(width//2 - 60, height//2 - 50, 120, 40)
        self.hard_button_start = pg.Rect(width//2 + 80, height//2 - 50, 120, 40)
        
        # In-game UI elements (will be set when game starts)
        self.new_game_button = None
        self.flip_board_button = None
        
        # Board orientation (Player at bottom - black pieces)
        self.white_at_bottom = False  # Reversed: Black at bottom
        
        # Status messages
        self.status_message = ""
        self.thinking = False
        
        # Promotion dialog state
        self.promotion_dialog_active = False
        self.promotion_move = None
        self.promotion_buttons = {}
        
    def init_game_ui(self):
        """Initialize in-game UI elements"""
        button_height = 30
        self.new_game_button = pg.Rect(10, self.height - button_height - 10, 120, button_height)
        self.flip_board_button = pg.Rect(140, self.height - button_height - 10, 120, button_height)
        
        # Initialize board image
        self.update_board_image()
        
        # Set initial status
        if self.player_color == chess.WHITE:
            self.status_message = "Your turn (White)"
        else:
            self.status_message = "Bot's turn (White)"
            # If player is black, bot moves first
            self.make_bot_move()

    def update_board_image(self):
        """Update the board image based on current state"""
        # Generate SVG of the board
        orientation = chess.WHITE if self.white_at_bottom else chess.BLACK
        last_move = self.board.peek() if self.board.move_stack else None
        check_square = self.board.king(self.board.turn) if self.board.is_check() else None
        
        # Create squares list for highlighting
        squares = []
        if self.selected_square:
            squares = [self.selected_square]
        
        svg_data = chess.svg.board(
            self.board, 
            size=min(self.width, self.height - 100),  # Leave space for UI
            orientation=orientation,
            lastmove=last_move,
            check=check_square,
            arrows=[],
            squares=squares
        )
        
        # Convert SVG to PNG
        png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'))
        
        # Convert PNG to pygame surface
        image = Image.open(io.BytesIO(png_data))
        mode = image.mode
        size = image.size
        data = image.tobytes()
        
        self.board_image = pg.image.fromstring(data, size, mode)
        
    def draw_start_screen(self):
        """Draw the start screen"""
        self.screen.fill((240, 217, 181))  # Light chess board color
        
        # Draw title
        title_text = self.title_font.render("Chess Bot", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(self.width//2, self.height//2 - 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw difficulty selection label
        diff_label = self.font.render("Select Difficulty:", True, (0, 0, 0))
        diff_rect = diff_label.get_rect(center=(self.width//2, self.height//2 - 80))
        self.screen.blit(diff_label, diff_rect)
        
        # Draw difficulty buttons
        pg.draw.rect(self.screen, (200, 200, 200), self.easy_button_start)
        pg.draw.rect(self.screen, (200, 200, 200), self.medium_button_start)
        pg.draw.rect(self.screen, (200, 200, 200), self.hard_button_start)
        
        # Highlight selected difficulty
        if self.selected_difficulty == 'easy':
            pg.draw.rect(self.screen, (150, 255, 150), self.easy_button_start, 3)
        elif self.selected_difficulty == 'medium':
            pg.draw.rect(self.screen, (150, 255, 150), self.medium_button_start, 3)
        else:
            pg.draw.rect(self.screen, (150, 255, 150), self.hard_button_start, 3)
        
        # Draw difficulty button texts
        easy_text = self.font.render('Easy', True, (0, 0, 0))
        medium_text = self.font.render('Medium', True, (0, 0, 0))
        hard_text = self.font.render('Hard', True, (0, 0, 0))
        
        easy_rect = easy_text.get_rect(center=self.easy_button_start.center)
        medium_rect = medium_text.get_rect(center=self.medium_button_start.center)
        hard_rect = hard_text.get_rect(center=self.hard_button_start.center)
        
        self.screen.blit(easy_text, easy_rect)
        self.screen.blit(medium_text, medium_rect)
        self.screen.blit(hard_text, hard_rect)
        
        # Draw start button
        pg.draw.rect(self.screen, (100, 200, 100), self.start_button)
        start_text = self.font.render("START GAME", True, (0, 0, 0))
        start_rect = start_text.get_rect(center=self.start_button.center)
        self.screen.blit(start_text, start_rect)
        
        # Draw player info
        info_text = "You will play as Black (bottom pieces)"
        info_surface = self.font.render(info_text, True, (0, 0, 0))
        info_rect = info_surface.get_rect(center=(self.width//2, self.height//2 + 120))
        self.screen.blit(info_surface, info_rect)

    def draw_promotion_dialog(self):
        """Draw the pawn promotion dialog"""
        # Draw semi-transparent overlay
        overlay = pg.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Dialog dimensions
        dialog_width = 300
        dialog_height = 200
        dialog_x = (self.width - dialog_width) // 2
        dialog_y = (self.height - dialog_height) // 2
        
        # Draw dialog background
        dialog_rect = pg.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pg.draw.rect(self.screen, (255, 255, 255), dialog_rect)
        pg.draw.rect(self.screen, (0, 0, 0), dialog_rect, 2)
        
        # Draw title
        title_text = self.font.render("Promote Pawn To:", True, (0, 0, 0))
        title_rect = title_text.get_rect(center=(dialog_x + dialog_width//2, dialog_y + 30))
        self.screen.blit(title_text, title_rect)
        
        # Draw promotion piece buttons
        button_width = 60
        button_height = 60
        button_spacing = 10
        start_x = dialog_x + (dialog_width - (4 * button_width + 3 * button_spacing)) // 2
        button_y = dialog_y + 70
        
        pieces = [
            (chess.QUEEN, "Q"),
            (chess.ROOK, "R"),
            (chess.BISHOP, "B"),
            (chess.KNIGHT, "N")
        ]
        
        self.promotion_buttons = {}
        
        for i, (piece_type, symbol) in enumerate(pieces):
            button_x = start_x + i * (button_width + button_spacing)
            button_rect = pg.Rect(button_x, button_y, button_width, button_height)
            
            # Store button for click detection
            self.promotion_buttons[piece_type] = button_rect
            
            # Draw button
            pg.draw.rect(self.screen, (200, 200, 200), button_rect)
            pg.draw.rect(self.screen, (0, 0, 0), button_rect, 2)
            
            # Draw piece symbol
            piece_text = self.font.render(symbol, True, (0, 0, 0))
            piece_rect = piece_text.get_rect(center=button_rect.center)
            self.screen.blit(piece_text, piece_rect)

    def handle_start_screen_click(self, pos):
        """Handle mouse clicks on the start screen"""
        x, y = pos
        
        # Check difficulty buttons
        if self.easy_button_start.collidepoint(x, y):
            self.selected_difficulty = 'easy'
        elif self.medium_button_start.collidepoint(x, y):
            self.selected_difficulty = 'medium'
        elif self.hard_button_start.collidepoint(x, y):
            self.selected_difficulty = 'hard'
        elif self.start_button.collidepoint(x, y):
            # Start the game
            self.bot = ChessBot(difficulty=self.selected_difficulty)
            self.game_state = "playing"
            self.init_game_ui()

    def handle_promotion_click(self, pos):
        """Handle clicks on promotion dialog"""
        for piece_type, button_rect in self.promotion_buttons.items():
            if button_rect.collidepoint(pos):
                # Create the promotion move
                move = chess.Move(
                    self.promotion_move.from_square,
                    self.promotion_move.to_square,
                    promotion=piece_type
                )
                
                # Make the move
                self.board.push(move)
                self.selected_square = None
                self.promotion_dialog_active = False
                self.promotion_move = None
                self.update_board_image()
                self.check_game_over()
                
                # If game is not over, let the bot make a move
                if not self.game_over:
                    self.thinking = True
                    self.status_message = f"Bot is thinking... ({self.selected_difficulty} difficulty)"
                    self.draw()
                    pg.display.flip()
                    self.make_bot_move()
                break

    def handle_game_click(self, pos):
        """Handle mouse click during game"""
        x, y = pos
        
        # Check if user clicked on game buttons
        if self.new_game_button and self.new_game_button.collidepoint(x, y):
            self.board = chess.Board()
            self.game_over = False
            self.result_message = ""
            self.selected_square = None
            self.promotion_dialog_active = False
            self.promotion_move = None
            self.update_board_image()
            if self.player_color == chess.WHITE:
                self.status_message = "Your turn (White)"
            else:
                self.status_message = "Bot's turn (White)"
                self.make_bot_move()
            return
        elif self.flip_board_button and self.flip_board_button.collidepoint(x, y):
            self.white_at_bottom = not self.white_at_bottom
            self.update_board_image()
            return
        
        # If game is over or thinking, ignore board clicks
        if self.game_over or self.thinking:
            return
        
        # If it's not the player's turn, ignore clicks
        if self.board.turn != self.player_color:
            return
        
        # Calculate board area
        board_size = min(self.width, self.height - 100)
        board_offset_x = (self.width - board_size) // 2
        board_offset_y = 10
        
        # Check if click is within board area
        if (x < board_offset_x or x >= board_offset_x + board_size or 
            y < board_offset_y or y >= board_offset_y + board_size):
            return
        
        # Get the square that was clicked
        file = int((x - board_offset_x) * 8 / board_size)
        rank = 7 - int((y - board_offset_y) * 8 / board_size)
        
        # If board is flipped, reverse coordinates
        if not self.white_at_bottom:
            file = 7 - file
            rank = 7 - rank
        
        square = chess.square(file, rank)
        
        # If a square was already selected
        if self.selected_square:
            # Try to make a move
            move = chess.Move(self.selected_square, square)
            
            # Check if it's a pawn promotion
            piece = self.board.piece_at(self.selected_square)
            if (piece and piece.piece_type == chess.PAWN and 
                ((self.player_color == chess.WHITE and rank == 7) or 
                 (self.player_color == chess.BLACK and rank == 0))):
                
                # Check if the move is legal (without promotion)
                if move in self.board.legal_moves:
                    # Show promotion dialog
                    self.promotion_dialog_active = True
                    self.promotion_move = move
                    return
            
            # Check if the move is legal
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.update_board_image()
                self.check_game_over()
                
                # If game is not over, let the bot make a move
                if not self.game_over:
                    self.thinking = True
                    self.status_message = f"Bot is thinking... ({self.selected_difficulty} difficulty)"
                    self.draw()
                    pg.display.flip()
                    self.make_bot_move()
            else:
                # Invalid move, select the new square if it has a piece of the player's color
                piece = self.board.piece_at(square)
                if piece and piece.color == self.player_color:
                    self.selected_square = square
                    self.update_board_image()
                else:
                    self.selected_square = None
                    self.update_board_image()
        else:
            # No square was selected yet, select the clicked square if it has a piece of the player's color
            piece = self.board.piece_at(square)
            if piece and piece.color == self.player_color:
                self.selected_square = square
                self.update_board_image()
    
    def make_bot_move(self):
        """Let the bot make a move"""
        # Add a small delay to show "thinking" status
        start_time = time.time()
        bot_move = self.bot.get_best_move(self.board)
        elapsed_time = time.time() - start_time
        
        # Ensure minimum thinking time for UI feedback
        if elapsed_time < 0.5:
            time.sleep(0.5 - elapsed_time)
        
        # Make the move
        self.board.push(bot_move)
        self.update_board_image()
        self.check_game_over()
        
        if not self.game_over:
            color_name = "White" if self.player_color == chess.WHITE else "Black"
            self.status_message = f"Your turn ({color_name})"
        
        self.thinking = False
    
    def check_game_over(self):
        """Check if the game is over"""
        if self.board.is_checkmate():
            self.game_over = True
            if self.board.turn == self.player_color:
                self.result_message = "Bot wins by checkmate!"
            else:
                self.result_message = "You win by checkmate!"
            self.status_message = self.result_message
        elif self.board.is_stalemate():
            self.game_over = True
            self.result_message = "Draw by stalemate!"
            self.status_message = self.result_message
        elif self.board.is_insufficient_material():
            self.game_over = True
            self.result_message = "Draw by insufficient material!"
            self.status_message = self.result_message
        elif self.board.is_fifty_moves():
            self.game_over = True
            self.result_message = "Draw by fifty-move rule!"
            self.status_message = self.result_message
        elif self.board.is_repetition():
            self.game_over = True
            self.result_message = "Draw by repetition!"
            self.status_message = self.result_message
    
    def draw_game(self):
        """Draw the game state"""
        self.screen.fill((240, 217, 181))
        
        # Calculate board position
        board_size = min(self.width, self.height - 100)
        board_offset_x = (self.width - board_size) // 2
        board_offset_y = 10
        
        # Draw the board
        self.screen.blit(self.board_image, (board_offset_x, board_offset_y))
        
        # Draw game buttons
        if self.new_game_button:
            pg.draw.rect(self.screen, (200, 200, 200), self.new_game_button)
            new_game_text = self.font.render('New Game', True, (0, 0, 0))
            self.screen.blit(new_game_text, (self.new_game_button.x + 10, self.new_game_button.y + 5))
        
        if self.flip_board_button:
            pg.draw.rect(self.screen, (200, 200, 200), self.flip_board_button)
            flip_text = self.font.render('Flip Board', True, (0, 0, 0))
            self.screen.blit(flip_text, (self.flip_board_button.x + 10, self.flip_board_button.y + 5))
        
        # Draw status message
        status_text = self.font.render(self.status_message, True, (0, 0, 0))
        self.screen.blit(status_text, (10, board_offset_y + board_size + 10))
        
        # Draw difficulty info
        diff_text = f"Difficulty: {self.selected_difficulty.capitalize()}"
        diff_surface = self.font.render(diff_text, True, (0, 0, 0))
        self.screen.blit(diff_surface, (10, board_offset_y + board_size + 35))
        
        # Draw player color info
        color_name = "Black" if self.player_color == chess.BLACK else "White"
        color_text = f"You are playing as: {color_name}"
        color_surface = self.font.render(color_text, True, (0, 0, 0))
        self.screen.blit(color_surface, (self.width - 200, board_offset_y + board_size + 35))
        
    def draw(self):
        """Main draw method"""
        if self.game_state == "start_screen":
            self.draw_start_screen()
        else:
            self.draw_game()
            
        # Draw promotion dialog if active
        if self.promotion_dialog_active:
            self.draw_promotion_dialog()
        
    def run(self):
        """Run the game loop"""
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.promotion_dialog_active:
                        self.handle_promotion_click(pg.mouse.get_pos())
                    elif self.game_state == "start_screen":
                        self.handle_start_screen_click(pg.mouse.get_pos())
                    else:
                        self.handle_game_click(pg.mouse.get_pos())
            
            self.draw()
            pg.display.flip()
            
        pg.quit()