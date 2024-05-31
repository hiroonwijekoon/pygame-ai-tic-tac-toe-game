import math
import random
import sys
import time

import pygame
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Screen size
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

CELL_WIDTH = SCREEN_WIDTH / 3
CELL_HEIGHT = (SCREEN_HEIGHT-200) / 3 # Adjusted height to keep the top area free

# Colors
BACKGROUND_COLOR = (200, 200, 200)  # White-ish
X_WIN_COLOR = (200, 150, 150)  # Red
O_WIN_COLOR = (150, 150, 200)  # Blue
DRAW_COLOR = (150, 150, 150)  # Gray

LINE_COLOR = (30, 30, 30)  # Black
X_COLOR = (200, 0, 0)  # Red
O_COLOR = (0, 0, 200)  # Blue

TEXT_COLOR = (30, 30, 30)  # Black

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tic Tac Toe with Heuristics + AI : M23W0307")
screen.fill(BACKGROUND_COLOR)

# Tic Tac Toe board (3×3 matrix)
board = [["" for _ in range(3)] for _ in range(3)]

# Define player and AI marks
HUMAN = "O"
AI = "X"

# Game states
running=True
game_over = False
winner = None
last_player = None  # Track the last player
current_player = HUMAN

iterations = 0

#Initialize scores
human_score = 0
ai_score = 0

#initialize difficulty level
difficulty_level = 1

# Font for displaying scores
font = pygame.font.Font(pygame.font.match_font('freesansbold'), 36)
font_title = pygame.font.Font(pygame.font.match_font('courier'), 42)
font_level = pygame.font.Font(pygame.font.match_font('freesansbold'), 28)


def draw_board():
    """
    Draw the Tic Tac Toe board respectively to the screen size
    """
    # Draw horizontal lines
    pygame.draw.line(screen, LINE_COLOR, (0, 200), (SCREEN_WIDTH, 200), 3) # Draw top line
    pygame.draw.line(screen, LINE_COLOR, (0, CELL_HEIGHT + 200), (SCREEN_WIDTH, CELL_HEIGHT + 200), 3)
    pygame.draw.line(screen, LINE_COLOR, (0, CELL_HEIGHT * 2 + 200), (SCREEN_WIDTH, CELL_HEIGHT * 2 + 200), 3)

    # Draw vertical lines
    pygame.draw.line(screen, LINE_COLOR, (CELL_WIDTH, 200), (CELL_WIDTH, SCREEN_HEIGHT), 3)
    pygame.draw.line(screen, LINE_COLOR, (CELL_WIDTH * 2, 200), (CELL_WIDTH * 2, SCREEN_HEIGHT), 3)

def draw_in_game_title():
    # Define positions and sizes
    maring_y_level = 20
    margin_y_title = 80

    if difficulty_level==1:
        level_text_string = "Training Wheels"
    elif difficulty_level==2:
        level_text_string = "Rising Star"
    elif difficulty_level==3:
        level_text_string = "Tic-Tac-Titan"

    # Draw difficulty level
    level_text = font_level.render(f"Difficulty: {level_text_string}", True, (0, 0, 0))
    level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, maring_y_level))
    pygame.draw.rect(screen, BACKGROUND_COLOR, level_rect) 
    screen.blit(level_text, level_rect)

    # Draw game title
    title_text = font_title.render("AI Tic-Tac-Toe", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, margin_y_title))
    pygame.draw.rect(screen, BACKGROUND_COLOR, title_rect) 
    screen.blit(title_text, title_rect)

def draw_scores():
    # Define positions and sizes
    human_x = 20
    human_y= 150
    ai_x = SCREEN_WIDTH - 80
    ai_y = 150

    # Draw human player score
    human_text = font.render(f"Human: {human_score}", True, (0, 0, 0))
    human_rect = human_text.get_rect(topleft=(human_x, human_y))
    pygame.draw.rect(screen, O_WIN_COLOR, human_rect) 
    screen.blit(human_text, human_rect)

    # Draw AI player score
    ai_text = font.render(f"AI: {ai_score}", True, (0, 0, 0))
    ai_rect = ai_text.get_rect(topleft=(ai_x, ai_y))
    pygame.draw.rect(screen, X_WIN_COLOR, ai_rect)
    screen.blit(ai_text, ai_rect)



def draw_marks():
    """
    Draw the marks (X or O) on the Tic Tac Toe board respectively to the current game state
    """
    for row in range(3):
        for col in range(3):
            # Calculate the center coordinates of the cell
            center_x = int(col * CELL_WIDTH + CELL_WIDTH / 2)
            center_y = int(row * CELL_HEIGHT + CELL_HEIGHT / 2) + 200  # Adjusted for top area

            # Fill in already made moves
            if board[row][col] == HUMAN:
                # Draw O mark for human player
                pygame.draw.circle(screen, O_COLOR, (center_x, center_y), int(min(CELL_WIDTH, CELL_HEIGHT) / 4), 5)
            elif board[row][col] == AI:
                # Draw X mark for AI player
                margin = int(min(CELL_WIDTH, CELL_HEIGHT) / 4)  # Margin from the cell borders
                pygame.draw.line(screen, X_COLOR, (center_x - margin, center_y - margin),
                                 (center_x + margin, center_y + margin), 5)
                pygame.draw.line(screen, X_COLOR, (center_x + margin, center_y - margin),
                                 (center_x - margin, center_y + margin), 5)


def check_win(player):
    """
    Check rows, columns and diagonals for a win
    :param player: The player to check for a win
    :return: True if the player has won, False otherwise
    """
    # Check rows
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] == player:
            return True
    # Check columns
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] == player:
            return True
    # Check diagonals
    if board[0][0] == board[1][1] == board[2][2] == player or board[0][2] == board[1][1] == board[2][0] == player:
        return True
    return False


def check_draw():
    """
    Check if any board place is still empty, otherwise the game is a draw
    :return: True if the game is a draw, False otherwise
    """
    for row in range(3):
        for col in range(3):
            if board[row][col] == "":
                return False
    return True


def minimax(board_variant, depth, is_maximizing):
    """
    Minimax algorithm to determine the best move for the AI
    :param board_variant: The current game state at the given depth
    :param depth: The depth of the game tree
    :param is_maximizing: True if the AI is maximizing, False if the AI is minimizing (playing as the human)
    :return: The best score in context of the AI player
    """
    global iterations
    iterations = iterations + 1
    # print(f"depth: {depth}, is_maximizing: {is_maximizing}, board: {board_variant}, iterations: {iterations}")

    if check_win(AI):
        return 1
    if check_win(HUMAN):
        return -1
    if check_draw():
        return 0

    if is_maximizing:
        best_score = -math.inf
        for row in range(3):
            for col in range(3):
                # Check if cell is available
                if board_variant[row][col] == "":
                    board_variant[row][col] = AI
                    score = minimax(board_variant, depth + 1, False)
                    board_variant[row][col] = ""
                    best_score = max(score, best_score)
                    # print(f"best_score max: {best_score}, depth: {depth}")
        # print(f"return best_score max: {best_score}, depth: {depth}")
        return best_score
    else:
        best_score = math.inf
        for row in range(3):
            for col in range(3):
                # Check if cell is available
                if board_variant[row][col] == "":
                    board_variant[row][col] = HUMAN
                    score = minimax(board_variant, depth + 1, True)
                    board_variant[row][col] = ""
                    best_score = min(score, best_score)
                    # print(f"best_score min: {best_score}, depth: {depth}")
        # print(f"return best_score min: {best_score}, depth: {depth}")
        return best_score

def ai_turn():
    """
    Perform the AI's move using the heuristic evaluation
    """

    # Use techniques according to the difficulty levels

    #  If the board is empty, take the center
    if board[1][1] == "":
        board[1][1] = AI  # AI takes the center
        return
    
    if difficulty_level==1:
        # Take any open cell
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":  # If the cell is empty
                    board[row][col] = AI
                    print("Open cell")
                    return

    if difficulty_level==2:
        # Prioritize winning moves
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":  # If the cell is empty
                    board[row][col] = AI  # Simulate the AI's move
                    if check_win(AI):  # Check if this is a winning move for the AI
                        print("Winning move found")
                        return
                    board[row][col] = ""  # Reset the board back

        # Block opponent's winning moves
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":  # If the cell is empty
                    board[row][col] = HUMAN  # Simulate the human's move
                    if check_win(HUMAN):  # Check if this is a winning move for the human player - if so then block it
                        board[row][col] = AI  # Block the cell to prevent losing
                        print("Blocked opponent's move")
                        return
                    board[row][col] = ""  # Reset the board back
        
        # Take any open cell
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":  # If the cell is empty
                    board[row][col] = AI
                    print("Open cell")
                    return
        
    if difficulty_level==3:
        # Prioritize winning moves
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":  # If the cell is empty
                    board[row][col] = AI  # Simulate the AI's move
                    if check_win(AI):  # Check if this is a winning move for the AI
                        return
                    board[row][col] = ""  # Reset the board back

        # Block opponent's winning moves
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":  # If the cell is empty
                    board[row][col] = HUMAN  # Simulate the human's move
                    if check_win(HUMAN):  # Check if this is a winning move for the human player - if so then block it
                        board[row][col] = AI  # Block the cell to prevent losing
                        return
                    board[row][col] = ""  # Reset the board back
        # Run Minimax
        global iterations
        iterations = 0
        best_score = -math.inf
        move = [-1, -1]
        # Iterate over the board and determine the best move
        for row in range(3):
            for col in range(3):
                # Check if cell is available
                if board[row][col] == "":
                    board[row][col] = AI  # Simulate the move
                    score = minimax(board, 0, False)
                    board[row][col] = ""  # Undo the move
                    if score > best_score:
                        best_score = score
                        move = [row, col]

        print(f"number of iterations: {iterations}")
        board[move[0]][move[1]] = AI  # Make the best move

def reset_game():
    global game_over, winner, board, current_player, last_player
    game_over = False
    winner = None
    board = [["" for _ in range(3)] for _ in range(3)]
    if winner == "Draw":
        current_player = random.choice([HUMAN, AI])
    else:
        current_player = AI if last_player == HUMAN else HUMAN
    winner = None
    last_player = current_player # Update last player to the current player

def main_loop():
    global running, game_over, current_player, winner, human_score, ai_score, last_player

    
    clock = pygame.time.Clock()  # Create a clock object
    
    while running:
        screen.fill(BACKGROUND_COLOR)

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: #Quit on escape key press
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_RETURN and game_over: # Handle enter key press -> start next round
                    reset_game()

            if event.type == MOUSEBUTTONDOWN and current_player == HUMAN and not game_over:
                mouse_x = event.pos[0]  # Column
                mouse_y = event.pos[1] - 200  # Row - Adjusted for top area

                clicked_row = int(mouse_y // CELL_HEIGHT)
                clicked_col = int(mouse_x // CELL_WIDTH)

                # Check if this is a valid move - it must be an empty cell
                if 0 <= clicked_row < 3 and 0 <= clicked_col < 3 and board[clicked_row][clicked_col] == "": #making sure it takes inputs only from the board area
                    board[clicked_row][clicked_col] = HUMAN
                    if check_win(HUMAN):
                        game_over = True
                        winner = HUMAN
                        human_score+=1 # increment human_score
                        last_player = HUMAN # Record last player
                    else:
                        current_player = AI

        if not game_over:

            if check_draw():
                game_over = True
                winner = "Draw"
                current_player = random.choice([HUMAN,AI]) # Select next player randomly

            if current_player == AI:
                ai_turn()
                if check_win(AI):
                    game_over = True
                    winner = AI
                    ai_score+=1 # increment ai_score
                    last_player = AI # Record last player
                else:
                    current_player = HUMAN

            draw_scores()
            draw_board()
            draw_marks()
            draw_in_game_title()


        
        else:
            # Render Winner
            if winner == AI:
                winner_text = font.render("AI Player Won!!", True, TEXT_COLOR)
            elif winner == HUMAN:
                winner_text = font.render("You Won!", True, TEXT_COLOR)
            elif winner=="Draw":
                winner_text = font.render("Draw!", True, TEXT_COLOR)

            instruction_text = font.render("Press enter to continue", True, TEXT_COLOR)

            screen.blit(winner_text, ((SCREEN_WIDTH - winner_text.get_width()) // 2, ((SCREEN_HEIGHT - winner_text.get_height()) // 2)-25))
            screen.blit(instruction_text, ((SCREEN_WIDTH - instruction_text.get_width()) // 2, ((SCREEN_HEIGHT - instruction_text.get_height()) // 2)+25))

        
        pygame.display.update()
        clock.tick(60)  # Limit the loop to run at 60 FPS

        


if __name__ == "__main__":
    # Start the main game loop
    main_loop()