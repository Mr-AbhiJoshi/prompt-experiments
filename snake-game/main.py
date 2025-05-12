import pygame
import time
import random
import sys
import json
import os

pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bg_music = os.path.join(BASE_DIR, "assets", "background.mp3")
eat_music = os.path.join(BASE_DIR, "assets", "eat.wav")
game_over_music = os.path.join(BASE_DIR, "assets", "game_over.wav")
high_score_file = os.path.join(BASE_DIR, "assets", "highscores.json")


pygame.mixer.init()
pygame.mixer.music.load(bg_music)
pygame.mixer.music.play(-1)  # Loop indefinitely

# --- Sounds ---
eat_sound = pygame.mixer.Sound(eat_music)
game_over_sound = pygame.mixer.Sound(game_over_music)

# --- Fonts ---
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)
menu_font = pygame.font.SysFont("comicsansms", 40)
title_font = pygame.font.SysFont("comicsansms", 60)

# --- Global Settings ---
block_size = 20
current_theme = {
    "background": (50, 153, 213),
    "snake": (0, 255, 0)
}

# --- Themes ---
themes = {
    "Classic": {"background": (50, 153, 213), "snake": (0, 255, 0)},
    "Dark": {"background": (0, 0, 0), "snake": (255, 255, 255)},
    "Desert": {"background": (210, 180, 140), "snake": (0, 0, 128)}
}

def draw_text_center(text, font, color, surface, y_offset=0):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + y_offset))
    surface.blit(text_obj, text_rect)

def score_display(score, surface):
    value = score_font.render("Score: " + str(score), True, (213, 50, 80))
    surface.blit(value, [10, 10])

def draw_snake(block_size, snake_list, surface, snake_color):
    for block in snake_list:
        pygame.draw.rect(surface, snake_color, [block[0], block[1], block_size, block_size])

def message(msg, color, surface, width, height):
    mesg = font_style.render(msg, True, color)
    surface.blit(mesg, [width / 6, height / 3])

def difficulty_menu(window):
    selecting = True
    while selecting:
        window.fill((100, 100, 100))
        draw_text_center("Select Difficulty", menu_font, (255, 255, 255), window, -100)
        draw_text_center("1. Easy (10 FPS)", font_style, (0, 255, 0), window, -30)
        draw_text_center("2. Medium (15 FPS)", font_style, (255, 255, 0), window, 10)
        draw_text_center("3. Hard (25 FPS)", font_style, (255, 0, 0), window, 50)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_KP1]:
                    return 10
                elif event.key in [pygame.K_2, pygame.K_KP2]:
                    return 15
                elif event.key in [pygame.K_3, pygame.K_KP3]:
                    return 25

def select_theme_menu(window):
    selecting = True
    while selecting:
        window.fill((50, 50, 50))
        draw_text_center("Select Theme", menu_font, (255, 255, 255), window, -150)

        options = list(themes.items())
        for idx, (theme_name, colors) in enumerate(options):
            y_offset = -50 + idx * 100
            draw_text_center(f"{idx + 1}. {theme_name}", font_style, (255, 255, 255), window, y_offset - 30)

            # Draw preview box
            preview_x = window.get_width() // 2 - 60
            preview_y = window.get_height() // 2 + y_offset
            pygame.draw.rect(window, colors["background"], (preview_x, preview_y, 120, 40))
            pygame.draw.rect(window, colors["snake"], (preview_x + 40, preview_y + 5, 40, 30))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_KP1]:
                    return options[0][1]
                elif event.key in [pygame.K_2, pygame.K_KP2]:
                    return options[1][1]
                elif event.key in [pygame.K_3, pygame.K_KP3]:
                    return options[2][1]

def main_menu(window):
    while True:
        window.fill((30, 30, 30))
        draw_text_center("Snake Game", title_font, (0, 255, 0), window, -180)

        draw_text_center("1. Play", menu_font, (255, 255, 255), window, -60)
        draw_text_center("2. High Scores", menu_font, (255, 255, 255), window, 20)
        draw_text_center("3. Quit", menu_font, (255, 255, 255), window, 100)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_theme = select_theme_menu(window)  # ✅ Use your existing theme selector
                    game_loop(window, selected_theme)
                elif event.key == pygame.K_2:
                    view_highscores(window)
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()

def view_highscores(window):
    highscores = load_highscores()

    font = pygame.font.SysFont("Arial", 30)
    message_font = pygame.font.SysFont("Arial", 25)

    while True:
        window.fill(current_theme["background"])

        # Display Title
        title_text = font.render("High Scores", True, (255, 255, 255))
        window.blit(title_text, (window.get_width() // 2 - title_text.get_width() // 2, 50))

        # Display High Scores for each difficulty
        y_offset = 100
        for difficulty in ["easy", "medium", "hard"]:
            difficulty_text = message_font.render(f"{difficulty.capitalize()}:", True, (255, 255, 255))
            window.blit(difficulty_text, (50, y_offset))

            scores = highscores[difficulty]
            for idx, score in enumerate(scores):
                score_text = message_font.render(f"{idx + 1}. {score['name']} - {score['score']}", True, (255, 255, 255))
                window.blit(score_text, (50, y_offset + (idx + 1) * 30))

            y_offset += (len(scores) + 1) * 30  # Move to the next difficulty's high score

        # Message to return to the main menu
        return_text = message_font.render("Press M to Return to Menu", True, (255, 0, 0))
        window.blit(return_text, (window.get_width() // 2 - return_text.get_width() // 2, window.get_height() - 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    return  # Go back to the main menu

def pause_game(window, width, height):
    paused = True
    while paused:
        window.fill(current_theme["background"])
        message("Game Paused - Press R to Resume or Q to Quit", (255, 255, 255), window, width, height)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    paused = False

def load_highscores():
    try:
        with open(high_score_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"easy": [], "medium": [], "hard": []}  # Default empty high scores

def save_highscores(highscores):
    with open(high_score_file, "w") as file:
        json.dump(highscores, file)
        
def get_player_name(window, width, height):
    font = pygame.font.SysFont("Arial", 30)
    name = ""
    input_active = True

    while input_active:
        window.fill(current_theme["background"])
        text_surface = font.render(f"Enter your name to enter HighScore Table: {name}", True, (255, 255, 255))
        window.blit(text_surface, (width // 2 - text_surface.get_width() // 2, height // 2))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                input_active = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(name) > 0:  # If Enter is pressed and name is not empty
                    return name
                elif event.key == pygame.K_BACKSPACE:  # If Backspace is pressed, remove last character
                    name = name[:-1]
                elif len(name) < 20:  # Max length of name
                    name += event.unicode  # Add the pressed character to name

    return name

def game_loop(window, current_theme):
    highscore_entered = False  # Reset highscore entry flag
    
    snake_speed = difficulty_menu(window)
    difficulty_key = {10: "easy", 15: "medium", 25: "hard"}[snake_speed]

    width, height = 600, 400
    window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    pygame.display.set_caption('Snake Game')

    game_over = False
    game_close = False

    x = width // 2
    y = height // 2
    x_change = block_size
    y_change = 0

    # Proper snake facing left (head is leftmost)
    snake_list = [
        [x - block_size * i, y]
        for i in range(2, -1, -1)
    ]
    snake_length = len(snake_list)

    food_x = round(random.randrange(0, width - block_size) / 20.0) * 20.0
    food_y = round(random.randrange(0, height - block_size) / 20.0) * 20.0

    clock = pygame.time.Clock()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                window = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -block_size
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = block_size
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -block_size
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = block_size
                    x_change = 0
                elif event.key == pygame.K_p:
                    pause_game(window, width, height)

        x += x_change
        y += y_change

        if x >= width or x < 0 or y >= height or y < 0:
            pygame.mixer.Sound.play(game_over_sound)
            game_close = True

        window.fill(current_theme["background"])
        pygame.draw.rect(window, (213, 50, 80), [food_x, food_y, block_size, block_size])

        snake_head = [x, y]
        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                pygame.mixer.Sound.play(game_over_sound)
                game_close = True

        draw_snake(block_size, snake_list, window, current_theme["snake"])
        score_display(snake_length - 3, window)
        pygame.display.update()

        if x == food_x and y == food_y:
            pygame.mixer.Sound.play(eat_sound)
            food_x = round(random.randrange(0, width - block_size) / 20.0) * 20.0
            food_y = round(random.randrange(0, height - block_size) / 20.0) * 20.0
            snake_length += 1

        while game_close:
            score = snake_length - 3
            highscores = load_highscores()
            current_scores = highscores[difficulty_key]

            # Check if the player’s score qualifies for the high score list
            if len(current_scores) < 5 or score > current_scores[-1]["score"]:
                if not highscore_entered:  # We will use a flag to ensure the name is only entered once
                    name = get_player_name(window, width, height)
                    current_scores.append({"name": name, "score": score})
                    current_scores = sorted(current_scores, key=lambda x: x["score"], reverse=True)[:5]
                    highscores[difficulty_key] = current_scores
                    save_highscores(highscores)
                    highscore_entered = True  # Ensure that name is only entered once
            else:
                highscore_entered = True  # If the score isn't high enough, still set the flag

            window.fill(current_theme["background"])
            message("Game Over! Press C to Replay or Q to Quit", (255, 0, 0), window, width, height)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    elif event.key == pygame.K_c:
                        game_loop(window,current_theme)  # Replay the game


        clock.tick(snake_speed)

# Start from main menu
window = pygame.display.set_mode((600, 400), pygame.RESIZABLE)
main_menu(window)