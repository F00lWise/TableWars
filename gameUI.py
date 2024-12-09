import pygame
import engine
import asyncio
import logging

DEBUG = True

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
DARKGREEN = (0, 128, 0)
DARKGRAY = (169, 169, 169)
DARKRED = (139, 0, 0)


# Set up fonts
font_size = 40

pygame.init()

class UI:                                                                                                    
    def __init__(self, board: engine.Board, api: engine.API):
            """
            Initializes the game UI and generates Rect objects for each grid coordinate.
            Args:
                board (engine.Board): The game board object containing the size of the board.
            Attributes:
                SCREEN_WIDTH (int): The width of the game screen.
                SCREEN_HEIGHT (int): The height of the game screen.
                BOARD_WIDTH (int): The width of the game board on the screen.
                BOARD_HEIGHT (int): The height of the game board on the screen.
                screen (pygame.Surface): The Pygame surface representing the game screen.
                grid_rects (list of list of pygame.Rect): A 2D list storing Rect objects for each grid cell.
            """
            self.board = board
            self.running = False            
            self.unit_clicked = None
            self.api = api
            self.logger = logging.getLogger('ui logger')

            pygame.display.set_caption("Table Wars")


            # Set up the game screen (make it resizable)
            self.screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
            # Track screen dimensions
            self.screen_width, self.screen_height = pygame.display.get_surface().get_size()

            # Define the size of the board on the screen. The remainder is reserved for controls and uncommitted figures
            self.board_width = self.screen_height
            self.board_height = self.screen_height
            # Define the number of squares in the grid
            self.rows, self.columns = self.board.size
            # Define the size of each square
            self.square_width = self.board_width // self.columns
            self.square_height = self.board_height // self.rows

            # Load the pre-saved board image
            board_image_filename = self.save_board_image()
            self.board_image = pygame.image.load(board_image_filename)
            self.reset_screen()

            self.create_grid_rects()
            self.update_unit_rects()

            # Set up font for displaying text
            self.font = pygame.font.SysFont(None, 30)

            # Action buttons
            self.buttons = []

            # Update the screen
            pygame.display.flip()

            self.logger.debug('UI initialized')

    def create_grid_rects(self):
        #self.logger.debug('Creating grid rects')
        # Initialize grid_rects to store the Rect objects for each grid cell
        self.grid_rects = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        # Generate Rect objects for each grid cell
        for row in range(self.rows):
            for col in range(self.columns):
                # Calculate the top-left corner of each grid square
                top_left_x = col * self.square_width
                top_left_y = row * self.square_height
                # Create the Rect object
                self.grid_rects[row][col] = pygame.Rect(top_left_x, top_left_y, self.square_width, self.square_height)

    def update_unit_rects(self):
        """
        Generates Rect objects for each unit on the board.
        """
        #self.logger.debug('Updating unit rects')
        # Generate Rect objects for each unit
        for unit in self.board.pieces.values():
            unit.rect = None
            if unit.clickable:
                row, col = unit.position
                # Calculate the top-left corner of the grid square
                top_left_x = col * self.square_width
                top_left_y = row * self.square_height
                # Create the Rect object
                unit.rect = pygame.Rect(top_left_x, top_left_y, self.square_width, self.square_height)

    def relpos_to_pix(self, x_ratio, y_ratio):
        """
        Get a position on the screen relative to the screen width and height.
        x_ratio and y_ratio are the percentage positions (0.0 to 1.0).
        """
        return (int(self.screen_width * x_ratio), int(self.screen_height * y_ratio))

    def save_board_image(self, filename="temp/board_grid.png"):
        self.logger.debug('Saving board image')
        # Create a temporary surface to draw the board and grid
        board_surface = pygame.Surface((self.board_width, self.board_height))

        # Set the background color (olive green for the board)
        board_surface.fill((128, 128, 0))

        # Draw the grid on the board surface
        for i in range(self.rows):
            for j in range(self.columns):
                pygame.draw.rect(board_surface, (255, 255, 255), 
                                (j * self.square_width, i * self.square_height, self.square_width, self.square_height), 1)

        # Save the board image to a file (PNG format)
        pygame.image.save(board_surface, filename)
        return filename

    def reset_screen(self):
        """
        Resets the screen by loading the pre-saved board image.
        """
        self.logger.debug('Resetting screen')
        # Create the screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)

        # Draw a line to separate the board from the controls
        pygame.draw.line(self.screen, (0, 0, 0), (self.board_width, 0), (self.board_width, self.screen_height))

        # Blit (draw) the board image onto the screen
        self.screen.blit(self.board_image, (0, 0))

        # The control area of the screen is white
        pygame.draw.rect(self.screen, (255, 255, 255), (self.board_width, 0, self.screen_width - self.board_width, self.screen_height))

        # Update the screen to display the changes
        pygame.display.flip()
    
    def show_pieces(self):
        """
        Places the units on the board.
        """
        # Place the units on the board
        for unit in self.board.pieces.values():
            position = unit.position
            letter = unit.name[0].upper()
            match unit.player:
                case 1:
                    color = DARKGREEN
                case 2:
                    color = DARKRED
                case _:
                    color = BLACK
            
            self.draw_circle_with_letter(position, letter, color=color)

    async def run(self):
        self.logger.info('Running UI')
        self.running = True
        while self.running:
            # Re-set the board
            self.reset_screen()

            # Place the units on the board
            self.show_pieces()

            # Display game info and action buttons
            self.draw_game_info()
            self.draw_option_buttons()

            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()

            self.highlight_hovered_square(mouse_pos)
            self.update_unit_rects()
            
            # Highlight the selected unit
            if self.unit_clicked:
                self.highlight_square(self.unit_clicked.position, RED, pixel_inwards=0)
                self.highlight_movement(self.unit_clicked)

            # Check for mouse clicks on buttons
            for event in pygame.event.get():
                match event.type:
                    case  pygame.MOUSEBUTTONDOWN:
                        self.handle_mouse_click(pygame.mouse.get_pos())
                    case pygame.QUIT:
                        self.running = False
                    case pygame.VIDEORESIZE:
                        self.handle_resize(event)
            # update the screen
            pygame.display.flip()

            #pause for 0.1 seconds
            pygame.time.delay(50)
            await asyncio.sleep(0.05)
        pygame.quit()

    def highlight_hovered_square(self, mouse_pos):
        self.logger.debug('Highlighting hovered square')
                # Loop over each grid cell and check for collision
        for row in range(len(self.grid_rects)):
            for col in range(len(self.grid_rects[row])):
                if self.grid_rects[row][col].collidepoint(mouse_pos):

                    # Highlight the square
                    if self.board.map[row, col] is None:
                        self.highlight_square((row, col), GREEN)
                    else:
                        self.highlight_square((row, col), YELLOW, pixel_inwards=3)

    # Function to draw a circle with a letter in a specific grid square
    def draw_circle_with_letter(self,  grid_position, letter,
                                 font=pygame.font.SysFont(None, font_size),
                                 color=BLACK, textcolor=WHITE):
        """
        Draws a circle with a letter in a specific grid square.
        
        Args:
            color (tuple): The color of the circle.
            grid_position (tuple): The (row, column) position in the grid.
            grid_size (tuple): The (width, height) size of each grid square.
            letter (str): The letter to draw inside the circle.
            font (pygame.font.Font): The font to use for the letter.
        """
        row, col = grid_position
        
        # Calculate the center of the grid square
        center_x = col * self.square_width + self.square_width // 2
        center_y = row * self.square_height + self.square_height // 2
        position = (center_x, center_y)
        
        # Calculate the radius of the circle to fit inside the square
        radius = min(self.square_width, self.square_height) // 2 - 5  # Subtracting 5 for padding
        
        # Draw the circle
        pygame.draw.circle(self.screen, color, position, radius)
        
        # Render the text
        text_surface = font.render(letter, True, textcolor)
        
        # Get the rectangle of the text surface
        text_rect = text_surface.get_rect(center=position)
        
        # Blit the text onto the circle
        self.screen.blit(text_surface, text_rect)

    def highlight_square(self, grid_position, color, pixel_inwards=0):
        """
        Highlights a grid square with a specific color.
        
        Args:
            grid_position (tuple): The (row, column) position in the grid.
            color (tuple): The color to use for highlighting.
        """

        row, col = grid_position
        
        # Calculate the top-left corner of the grid square
        top_left = (col * self.square_width + pixel_inwards, row * self.square_height + pixel_inwards)
        
        # Draw a rectangle to highlight the square
        pygame.draw.rect(self.screen, color, (*top_left, self.square_width-2*pixel_inwards, self.square_height-2*pixel_inwards), 3)

    def highlight_movement(self, unit:engine.Unit):
        self.logger.debug('Highlighting movement')
        fields = unit.get_fields_in_range()
        for field in fields:
            self.highlight_square(field, BLUE, pixel_inwards=5)

    def draw_text(self, text, pos, color=BLACK):
        """
        Draw text on the screen at the specified position.
        """
        display = text if type(text) == str else text.__repr__()
        text_surface = self.font.render(display, True, color)
        self.screen.blit(text_surface, pos)

    def create_button(self, text, rect, callback):
        """
        Create a button with a callback when clicked.
        """
        self.logger.debug('Creating button')
        pygame.draw.rect(self.screen, GREEN, rect)
        self.draw_text(text, (rect.x + 5, rect.y + 5))
        self.buttons.append((rect, callback))

    def draw_game_info(self):
        """
        Display the current game turn, active player, and selected unit.
        Position the text relative to the screen size.
        """
        self.logger.debug('Drawing game info')
        # Get relative positions for the text
        aspect_ratio = self.screen_height / self.screen_width

        w = aspect_ratio + 0.01
        turn_pos = self.relpos_to_pix(w, 0.05)  # 80% width, 5% height
        player_pos = self.relpos_to_pix(w, 0.1)  # 80% width, 10% height
        unit_pos = self.relpos_to_pix(w, 0.15)   # 80% width, 15% height
        api_state_pos = self.relpos_to_pix(w, 0.2)   # 80% width, 20% height

        # Display game turn
        self.draw_text(f"Turn: {self.api.rules.game_turn}", turn_pos)
        
        # Display active player
        self.draw_text(f"Player: {self.api.get_active_player()}", player_pos)
        
        # Display selected unit if any
        if self.unit_clicked:
            self.draw_text(f"Selected Unit: {self.unit_clicked.name}", unit_pos)
        else:
            self.draw_text("Selected Unit: None", unit_pos)

        # Display API state
        self.draw_text(f"API State: {self.api.state}", api_state_pos)

    def draw_option_buttons(self):
        """
        Draw the available action buttons based on the game state.
        The buttons are positioned relative to the screen size.
        """
        self.logger.debug('Drawing option buttons')
        self.buttons.clear()

        # Start y position at 20% of the screen height, and increment by 5% for each button
        y_offset = 0.3

        for action in self.api.current_options:
            if isinstance(action, str): # exclude coordinates
                button_rect = pygame.Rect(
                    int(self.screen_width * 0.75),     # 75% of the screen width
                    int(self.screen_height * y_offset), # Start y offset, increasing
                    int(self.screen_width * 0.2),      # Button width (20% of screen width)
                    int(self.screen_height * 0.05)     # Button height (5% of screen height)
                )
                def callback(self=self,act=action):
                    self.api.selection_done(act)
                self.create_button(action, button_rect, callback)
                y_offset += 0.06  # Move down by 6% for the next button

    def handle_resize(self, event):
        """
        Handle screen resize events.
        """
        self.logger.info('Handling screen resize')
        self.screen_width, self.screen_height = event.size

        # Define the size of the board on the screen. The remainder is reserved for controls and uncommitted figures
        self.board_width = self.screen_height
        self.board_height = self.screen_height
        # Define the number of squares in the grid
        self.rows, self.columns = self.board.size
        # Define the size of each square
        self.square_width = self.board_width // self.columns
        self.square_height = self.board_height // self.rows

        # Load the pre-saved board image
        board_image_filename = self.save_board_image()
        self.board_image = pygame.image.load(board_image_filename)
        self.reset_screen()

        self.create_grid_rects()
        self.update_unit_rects()

    def handle_mouse_click(self, pos):
        """
        Check if any buttons are clicked.
        """
        self.logger.debug('Handling mouse click')
        if self.api.state == 'wait_for_option_sel':
            # Check if a button is clicked
            for button, callback in self.buttons:
                if button.collidepoint(pos):
                    callback()
        
        if self.api.state == 'wait_for_unit_sel':
            # Check if a unit is clicked
            for unit in self.board.pieces.values():
                if unit.clickable and unit.rect.collidepoint(pos):
                    self.unit_clicked = unit
                    self.api.selection_done(unit)
                    print(f'Selected unit: {unit}')
        
        if self.api.state == 'wait_for_tile_sel':
            # Check if a grid square is clicked
            for row in range(len(self.grid_rects)):
                for col in range(len(self.grid_rects[row])):
                    if self.grid_rects[row][col].collidepoint(pos):
                        self.api.selection_done((row, col))
                        print(f'Selected tile: {row}, {col}')
