import pygame
import engine

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)


# Set up fonts
font_size = 50

pygame.init()

class UI:                                                                                                    
    def __init__(self, board: engine.Board):
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
            self.unit_selected = None

            pygame.display.set_caption("Table Wars")

            # Define the size of the screen
            self.SCREEN_WIDTH = 800
            self.SCREEN_HEIGHT = 600

            # Define the size of the board on the screen. The remainder is reserved for controls and uncommitted figures
            self.BOARD_WIDTH = 600
            self.BOARD_HEIGHT = 600

            # Define the number of squares in the grid
            self.rows, self.columns = self.board.size

            # Define the size of each square
            self.square_width = self.BOARD_WIDTH // self.columns
            self.square_height = self.BOARD_HEIGHT // self.rows

            # Load the pre-saved board image
            board_image_filename = self.save_board_image()
            self.board_image = pygame.image.load(board_image_filename)
            self.reset_screen()


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

            # Update the screen
            pygame.display.flip()

    def save_board_image(self, filename="temp/board_grid.png"):

        # Create a temporary surface to draw the board and grid
        board_surface = pygame.Surface((self.BOARD_WIDTH, self.BOARD_HEIGHT))

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
        # Create the screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Draw a line to separate the board from the controls
        pygame.draw.line(self.screen, (0, 0, 0), (self.BOARD_WIDTH, 0), (self.BOARD_WIDTH, self.SCREEN_HEIGHT))

        # Blit (draw) the board image onto the screen
        self.screen.blit(self.board_image, (0, 0))

        # The control area of the screen is white
        pygame.draw.rect(self.screen, (255, 255, 255), (self.BOARD_WIDTH, 0, self.SCREEN_WIDTH - self.BOARD_WIDTH, self.SCREEN_HEIGHT))

        # Update the screen to display the changes
        pygame.display.flip()
    

    def show_pieces(self):
        """
        Places the units on the board.
        """
        # Place the units on the board
        for unit in self.board.pieces.values():
            position = unit.position
            letter = unit.basemodel[0].upper()
            self.draw_circle_with_letter(position, letter)

    def run(self):
        self.running = True
        while self.running:
            # Re-set the board
            self.reset_screen()

            # Place the units on the board
            self.show_pieces()

            # # Test highlighting
            # self.highlight_square([2,3],(255,0,0), pixel_inwards=3)
            # for piece in self.board.pieces.items():
            #     if isinstance(piece,engine.Unit):
            #         self.highlight_movement(piece)

            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()

            # Loop over each grid cell and check for collision
            for row in range(len(self.grid_rects)):
                for col in range(len(self.grid_rects[row])):
                    if self.grid_rects[row][col].collidepoint(mouse_pos):

                        # Highlight the square
                        if self.board.map[row, col] is None:
                            self.highlight_square((row, col), GREEN)
                        else:
                            self.highlight_square((row, col), YELLOW, pixel_inwards=3)
                            
                            # If clicked on the unit, select it
                            if pygame.mouse.get_pressed()[0]:
                                self.unit_selected = self.board.map[row, col]
            
            # Highlight the selected unit
            if self.unit_selected:
                self.highlight_square(self.unit_selected.position, RED, pixel_inwards=0)
                self.highlight_movement(self.unit_selected)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # update the screen
            pygame.display.flip()

            #pause for 0.1 seconds
            pygame.time.delay(100)

        pygame.quit()

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
        fields = unit.get_fields_in_range()
        for field in fields:
            self.highlight_square(field, BLUE, pixel_inwards=5)


