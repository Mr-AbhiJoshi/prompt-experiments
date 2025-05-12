import pygame
import random
import json
import os
import sys

# Initialize Pygame
pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
bg_music = os.path.join(BASE_DIR, "assets", "background.mp3")
flap_music = os.path.join(BASE_DIR, "assets", "flap.wav")
hit_music = os.path.join(BASE_DIR, "assets", "hit.wav")
score_music = os.path.join(BASE_DIR, "assets", "score.wav")
high_score_file = os.path.join(BASE_DIR, "assets", "highscores.json")

# Constants
WIDTH, HEIGHT = 400, 600
FPS = 60
PIPE_WIDTH = 70
PIPE_GAP_HARD = 150
PIPE_GAP_MEDIUM = 180
PIPE_GAP_EASY = 220
GRAVITY_HARD = 0.5
GRAVITY_EASY = 0.35
FLAP_STRENGTH = -10
PIPE_SPEED = 3
BIRD_RADIUS = 20
FONT_NAME = pygame.font.get_default_font()
HIGHSCORE_FILE = high_score_file

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 177, 76)
BLUE = (0, 162, 232)
RED = (200, 0, 0)
GREY = (200, 200, 200)
YELLOW = (255, 255, 0)

# Fonts
title_font = pygame.font.Font(FONT_NAME, 48)
menu_font = pygame.font.Font(FONT_NAME, 32)
small_font = pygame.font.Font(FONT_NAME, 24)

# Sounds
def load_sound(file):
    try:
        return pygame.mixer.Sound(file)
    except:
        return None

flap_sound = load_sound(flap_music)
score_sound = load_sound(score_music)
hit_sound = load_sound(hit_music)
try:
    pygame.mixer.music.load(bg_music)
    pygame.mixer.music.set_volume(0.3)
except:
    pass

# Highscore Handling
def load_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump([], f)
    with open(HIGHSCORE_FILE, 'r') as f:
        return json.load(f)

def save_highscores(scores):
    with open(HIGHSCORE_FILE, 'w') as f:
        json.dump(scores[:5], f)

def draw_bird(window, bird_y):
    pygame.draw.circle(window, BLUE, (80, int(bird_y)), BIRD_RADIUS)

def draw_pipes(window, pipes):
    for pipe in pipes:
        pygame.draw.rect(window, GREEN, pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['top']))
        pygame.draw.rect(window, GREEN, pygame.Rect(pipe['x'], pipe['bottom'], PIPE_WIDTH, HEIGHT - pipe['bottom']))

def check_collision(bird_y, pipes):
    if bird_y + BIRD_RADIUS >= HEIGHT or bird_y - BIRD_RADIUS <= 0:
        return True
    for pipe in pipes:
        if 80 + BIRD_RADIUS > pipe['x'] and 80 - BIRD_RADIUS < pipe['x'] + PIPE_WIDTH:
            if bird_y - BIRD_RADIUS < pipe['top'] or bird_y + BIRD_RADIUS > pipe['bottom']:
                return True
    return False

def pause_game(window, clock):
    paused = True
    pause_text = title_font.render("Paused", True, BLACK)
    window.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.update()
    while paused:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = False

def get_player_name(window, clock):
    name = ""
    entering = True
    while entering:
        clock.tick(FPS)
        window.fill(WHITE)
        prompt = small_font.render("New High Score! Enter your name:", True, BLACK)
        name_text = title_font.render(name, True, BLUE)
        window.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 3))
        window.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Anonymous"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name if name else "Anonymous"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 10 and event.unicode.isprintable():
                    name += event.unicode
    return name

def display_highscores(window):
    scores = load_highscores()
    showing = True
    while showing:
        window.fill(WHITE)
        title = title_font.render("High Scores", True, BLACK)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        for i, score in enumerate(scores):
            score_text = menu_font.render(f"{i+1}. {score['name']} - {score['score']}", True, BLUE)
            window.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 120 + i * 40))
        back_text = small_font.render("Press ESC to return", True, GREY)
        window.blit(back_text, (10, HEIGHT - 30))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                showing = False

def select_difficulty(window):
    options = ["Easy", "Medium", "Hard"]
    selected = 0
    choosing = True
    while choosing:
        window.fill(WHITE)
        title = title_font.render("Select Difficulty", True, BLACK)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        for i, option in enumerate(options):
            color = RED if i == selected else BLACK
            text = menu_font.render(option, True, color)
            window.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected]

def game_over_screen(window, clock, score):
    rect_width, rect_height = 300, 180
    rect_x = WIDTH // 2 - rect_width // 2
    rect_y = HEIGHT // 2 - rect_height // 2
    while True:
        clock.tick(FPS)
        pygame.draw.rect(window, BLACK, (rect_x, rect_y, rect_width, rect_height))
        over = menu_font.render("Game Over!!", True, YELLOW)
        again = small_font.render("Press R to Play Again", True, YELLOW)
        quit_ = small_font.render("Press ESC to Exit", True, YELLOW)
        window.blit(over, (WIDTH // 2 - over.get_width() // 2, rect_y + 20))
        window.blit(again, (WIDTH // 2 - again.get_width() // 2, rect_y + 70))
        window.blit(quit_, (WIDTH // 2 - quit_.get_width() // 2, rect_y + 110))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_ESCAPE:
                    return "menu"

def main_menu(window):
    selected = 0
    options = ["Play", "View High Scores", "Quit"]
    while True:
        window.fill(WHITE)
        title = title_font.render("Flappy Bird", True, BLUE)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        for i, option in enumerate(options):
            color = RED if i == selected else BLACK
            text = menu_font.render(option, True, color)
            window.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "Play":
                        return select_difficulty(window)
                    elif options[selected] == "View High Scores":
                        display_highscores(window)
                    elif options[selected] == "Quit":
                        pygame.quit(); sys.exit()

def game_loop(window, difficulty):
    clock = pygame.time.Clock()
    bird_y = HEIGHT // 2
    bird_velocity = 0
    pipes = []
    spawn_timer = 0
    score = 0

    if difficulty == "Easy":
        pipe_gap = PIPE_GAP_EASY
        gravity = GRAVITY_EASY
    elif difficulty == "Medium":
        pipe_gap = PIPE_GAP_MEDIUM
        gravity = GRAVITY_HARD
    else:
        pipe_gap = PIPE_GAP_HARD
        gravity = GRAVITY_HARD

    pygame.mixer.music.play(-1)

    while True:
        clock.tick(FPS)
        window.fill(WHITE)

        # Bird physics
        bird_velocity += gravity
        bird_y += bird_velocity

        # Pipe logic
        spawn_timer += 1
        if spawn_timer > 90:
            top = random.randint(50, HEIGHT - pipe_gap - 50)
            bottom = top + pipe_gap
            pipes.append({'x': WIDTH, 'top': top, 'bottom': bottom})
            spawn_timer = 0

        for pipe in pipes:
            pipe['x'] -= PIPE_SPEED
        pipes = [p for p in pipes if p['x'] + PIPE_WIDTH > 0]

        draw_pipes(window, pipes)
        draw_bird(window, bird_y)

        for pipe in pipes:
            if pipe['x'] + PIPE_WIDTH < 80 and not pipe.get('scored'):
                pipe['scored'] = True
                score += 1
                if score_sound: score_sound.play()

        if check_collision(bird_y, pipes):
            if hit_sound: hit_sound.play()
            pygame.mixer.music.stop()
            highscores = load_highscores()
            if len(highscores) < 5 or score > highscores[-1]['score']:
                name = get_player_name(window, clock)
                highscores.append({'name': name, 'score': score})
                highscores = sorted(highscores, key=lambda x: x['score'], reverse=True)
                save_highscores(highscores)
            choice = game_over_screen(window, clock, score)
            if choice == "restart":
                return difficulty
            elif choice == "menu":
                return None

        score_text = title_font.render(str(score), True, BLACK)
        window.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird_velocity = FLAP_STRENGTH
                    if flap_sound: flap_sound.play()
                elif event.key == pygame.K_p:
                    pause_game(window, clock)

def main():
    window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Flappy Bird Clone")
    while True:
        difficulty = main_menu(window)
        while difficulty:
            difficulty = game_loop(window, difficulty)

if __name__ == "__main__":
    main()
