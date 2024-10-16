import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Mouse Interaction Example')

# Set up colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
LIGHT_GREEN = (144, 238, 144)
BLACK = (0, 0, 0)

# Create a rectangle (Pygame Rect object)
rect_width, rect_height = 100, 100
rect = pygame.Rect(350, 250, rect_width, rect_height)  # Rect(x, y, width, height)

# Variables to track selection
selected = False

# Game loop
while True:
    screen.fill(WHITE)  # Fill screen with white

    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Check if mouse is hovering over the rectangle
    if rect.collidepoint(mouse_pos):
        color = LIGHT_GREEN  # Highlight when hovering
        if pygame.mouse.get_pressed()[0]:  # Check for left mouse click (button index 0)
            selected = True
    else:
        color = GREEN  # Default color when not hovering

    # If the rectangle is selected, change its color
    if selected:
        color = BLACK

    # Draw the rectangle
    pygame.draw.rect(screen, color, rect)

    # Event loop to check for quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update the display
    pygame.display.flip()
