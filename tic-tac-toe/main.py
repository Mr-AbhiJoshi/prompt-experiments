import pygame
import sys
import random
import time
import os

# Initialize Pygame
pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bg_music = os.path.join(BASE_DIR, "assets", "background_music.mp3")

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 3
CELL_SIZE = WIDTH // GRID_SIZE
LINE_WIDTH = 15

# Themes: (bg_color, line_color, x_color, o_color, button_bg)
THEMES = [
    ((30, 30, 30), (200, 200, 200), (255, 0, 0), (0, 255, 0), (50, 50, 50)),  # Dark
    ((255, 255, 255), (0, 0, 0), (0, 0, 255), (255, 165, 0), (200, 200, 200)),   # Light
    ((240, 240, 200), (100, 100, 100), (128, 0, 128), (0, 128, 128), (180, 180, 150))  # Pastel
]

# Game State Variables
current_theme = 0
mode = None  # 'PvP' or 'PvC'
symbols = ['X', 'O']

# Fonts
font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 40)

# Music
pygame.mixer.music.load(bg_music)  # Ensure this file exists
pygame.mixer.music.play(-1)

# Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe")

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)
    return textrect

def main_menu():
    while True:
        screen.fill((0, 0, 0))
        draw_text('Tic-Tac-Toe', font, (255, 255, 255), screen, WIDTH//2, HEIGHT//4)
        draw_text('1. Play PvP', small_font, (255, 255, 255), screen, WIDTH//2, HEIGHT//2 - 40)
        draw_text('2. Play PvC', small_font, (255, 255, 255), screen, WIDTH//2, HEIGHT//2)
        draw_text('3. Exit', small_font, (255, 255, 255), screen, WIDTH//2, HEIGHT//2 + 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 'PvP'
                elif event.key == pygame.K_2:
                    return 'PvC'
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()

def choose_theme():
    while True:
        screen.fill((0, 0, 0))
        draw_text('Choose Theme', font, (255, 255, 255), screen, WIDTH//2, HEIGHT//4)
        draw_text('1. Dark', small_font, (255, 255, 255), screen, WIDTH//2, HEIGHT//2 - 40)
        draw_text('2. Light', small_font, (255, 255, 255), screen, WIDTH//2, HEIGHT//2)
        draw_text('3. Pastel', small_font, (255, 255, 255), screen, WIDTH//2, HEIGHT//2 + 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 0
                elif event.key == pygame.K_2:
                    return 1
                elif event.key == pygame.K_3:
                    return 2

def draw_board(board, colors):
    screen.fill(colors[0])

    for x in range(1, GRID_SIZE):
        pygame.draw.line(screen, colors[1], (0, x * CELL_SIZE), (WIDTH, x * CELL_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, colors[1], (x * CELL_SIZE, 0), (x * CELL_SIZE, HEIGHT), LINE_WIDTH)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            mark = board[row][col]
            center = (col * CELL_SIZE + CELL_SIZE//2, row * CELL_SIZE + CELL_SIZE//2)
            if mark == 'X':
                pygame.draw.line(screen, colors[2], (center[0]-50, center[1]-50), (center[0]+50, center[1]+50), LINE_WIDTH)
                pygame.draw.line(screen, colors[2], (center[0]+50, center[1]-50), (center[0]-50, center[1]+50), LINE_WIDTH)
            elif mark == 'O':
                pygame.draw.circle(screen, colors[3], center, 50, LINE_WIDTH)

    pygame.display.flip()

def check_winner(board):
    for i in range(GRID_SIZE):
        if board[i][0] != '' and all(board[i][j] == board[i][0] for j in range(GRID_SIZE)):
            return board[i][0]
        if board[0][i] != '' and all(board[j][i] == board[0][i] for j in range(GRID_SIZE)):
            return board[0][i]
    if board[0][0] != '' and all(board[i][i] == board[0][0] for i in range(GRID_SIZE)):
        return board[0][0]
    if board[0][GRID_SIZE-1] != '' and all(board[i][GRID_SIZE-1-i] == board[0][GRID_SIZE-1] for i in range(GRID_SIZE)):
        return board[0][GRID_SIZE-1]
    return None

def get_empty_cells(board):
    return [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == '']

def computer_move(board, computer_symbol, player_symbol):
    empty_cells = get_empty_cells(board)
    for row, col in empty_cells:
        board[row][col] = computer_symbol
        if check_winner(board) == computer_symbol:
            return row, col
        board[row][col] = ''
    for row, col in empty_cells:
        board[row][col] = player_symbol
        if check_winner(board) == player_symbol:
            board[row][col] = computer_symbol
            return row, col
        board[row][col] = ''
    return random.choice(empty_cells)

def game_loop(mode, theme_index):
    board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    colors = THEMES[theme_index]

    player1, player2 = ('Player', 'Computer') if mode == 'PvC' else ('Player 1', 'Player 2')
    random.shuffle(symbols)
    symbols_map = {player1: symbols[0], player2: symbols[1]}
    turn = player1

    running = True
    while running:
        draw_board(board, colors)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and (mode == 'PvP' or turn == 'Player'):
                x, y = event.pos
                row, col = y // CELL_SIZE, x // CELL_SIZE
                if board[row][col] == '':
                    board[row][col] = symbols_map[turn]
                    draw_board(board, colors)
                    winner_symbol = check_winner(board)
                    if winner_symbol or not get_empty_cells(board):
                        running = False
                        break
                    turn = player2 if turn == player1 else player1

        if mode == 'PvC' and turn == 'Computer' and running:
            time.sleep(1)
            row, col = computer_move(board, symbols_map['Computer'], symbols_map['Player'])
            board[row][col] = symbols_map['Computer']
            draw_board(board, colors)
            winner_symbol = check_winner(board)
            if winner_symbol or not get_empty_cells(board):
                running = False
            else:
                turn = player1

    draw_board(board, colors)
    winner_symbol = check_winner(board)
    if winner_symbol:
        winner = [name for name, symbol in symbols_map.items() if symbol == winner_symbol]
        winner_text = f"{winner[0]} won the game!!"
    else:
        winner_text = "Match Drawn!!"

    # Background rectangle for winner text
    text_surface = font.render(winner_text, True, (255, 255, 0))
    text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(20, 20))
    screen.blit(text_surface, text_rect)

    # Draw play again and menu buttons
    button_bg = colors[4]
    pygame.draw.rect(screen, button_bg, (WIDTH//2 - 150, HEIGHT//2 + 50, 300, 50))
    pygame.draw.rect(screen, button_bg, (WIDTH//2 - 150, HEIGHT//2 + 110, 300, 50))
    draw_text("Press R to Play Again", small_font, (0, 0, 0), screen, WIDTH//2, HEIGHT//2 + 75)
    draw_text("Press M for Main Menu", small_font, (0, 0, 0), screen, WIDTH//2, HEIGHT//2 + 135)

    pygame.display.flip()
    wait_for_choice(mode, theme_index)

def wait_for_choice(mode, theme_index):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_loop(mode, theme_index)
                    return
                elif event.key == pygame.K_m:
                    main()
                    return

def main():
    global mode, current_theme
    while True:
        mode = main_menu()
        current_theme = choose_theme()
        game_loop(mode, current_theme)

if __name__ == "__main__":
    main()
