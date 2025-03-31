import pygame
import sys
import os
import random

# Initialize
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1600, 800
GROUND_Y = HEIGHT - 100
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
FONT = pygame.font.SysFont(None, 64)
TITLE_FONT = pygame.font.SysFont(None, 96)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors
SKY_COLOR = (60, 60, 60)
GROUND_COLOR = (92, 64, 51)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Config
NUM_OBSTACLES = 2
OBSTACLE_SPEED = 8
JUMP_HEIGHT = 35

# Players
PLAYERS = {
    "ethan": {
        "run": "ethan_run.png",
        "jump": "ethan_jump.png",
        "cry": "ethan_cry.png",
        "jump_sound": "ethan_jump_sound.mp3",
        "gameover_sound": "ethan_cry_sound.mp3"
    },
    "max": {
        "run": "max_run.png",
        "jump": "max_jump.png",
        "cry": "max_cry.png",
        "jump_sound": "max_jump_sound.mp3",
        "gameover_sound": "max_cry_sound.mp3"
    }
}

# Obstacle pool
OBSTACLE_TYPES = [
    {
        "img": "obstacle_wolf.png",
        "entry_sound": "obstacle_wolf_sound.mp3"
    },
    {
        "img": "obstacle_dad_wolf.png",
        "entry_sound": "obstacle_dad_wolf_sound.mp3"
    }
]

# Load assets
def load_img(name, size):
    return pygame.transform.smoothscale(
        pygame.image.load(os.path.join(ASSET_DIR, name)).convert_alpha(), size
    )

def load_sound(name):
    return pygame.mixer.Sound(os.path.join(ASSET_DIR, name))

# Game state class
class GameState:
    def __init__(self):
        self.reset()
    
    # Game reset
    def reset(self):
        self.player_rect = pygame.Rect(200, GROUND_Y - 140, 140, 140)
        self.player_vel_y = 0
        self.on_ground = True
        self.game_active = True
        self.you_won = False
        self.restart_ready = False
        self.victory_sound_played = False
        self.victory_rect = pygame.Rect(WIDTH + 200, GROUND_Y - 180, 180, 180)
        self.score = 0

# Start menu
def start_menu():
    selected_player = "ethan"
    selecting = True
    while selecting:
        screen.fill(SKY_COLOR)
        title = TITLE_FONT.render("Choose Your Runner", True, WHITE)
        screen.blit(title, (WIDTH // 2 - 300, 100))

        player_text = FONT.render(f"Player: {selected_player.title()}", True, WHITE)
        screen.blit(player_text, (WIDTH // 2 - 150, 250))

        tip = FONT.render("Press 1 to toggle, Enter to start", True, YELLOW)
        screen.blit(tip, (WIDTH // 2 - 400, 600))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_player = "ethan" if selected_player == "max" else "max"
                elif event.key == pygame.K_RETURN:
                    selecting = False

        pygame.display.flip()
        clock.tick(30)

    return selected_player

# Load selected player and all obstacles
def load_assets(player):
    assets = {
        "run": load_img(PLAYERS[player]["run"], (140, 140)),
        "jump": load_img(PLAYERS[player]["jump"], (140, 140)),
        "cry": load_img(PLAYERS[player]["cry"], (140, 140)),
        "jump_sound": load_sound(PLAYERS[player]["jump_sound"]),
        "gameover_sound": load_sound(PLAYERS[player]["gameover_sound"]),
        "victory_lady": load_img("fion_victory.png", (180, 180)),
        "victory_sound": load_sound("fion_victory_sound.mp3"),
        "obstacles": []
    }

    for ob in OBSTACLE_TYPES:
        assets["obstacles"].append({
            "img": load_img(ob["img"], (160, 130)),
            "sound": load_sound(ob["entry_sound"])
        })

    return assets

# Main game loop
def run_game(assets, state):
    state.reset()  # initialize state

    # Create obstacles with random types
    obstacles = []
    for i in range(NUM_OBSTACLES):
        rect = pygame.Rect(WIDTH + i * 800, GROUND_Y - 130, 160, 130)
        ob_asset = random.choice(assets["obstacles"])
        obstacles.append({
            "rect": rect,
            "asset": ob_asset,
            "sound_played": False
        })

    running = True

    while running:
        dt = clock.tick(60) / 1000
        screen.fill(SKY_COLOR)
        pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if state.game_active and not state.you_won:
            if keys[pygame.K_SPACE] and state.on_ground:
                state.player_vel_y = -JUMP_HEIGHT
                state.on_ground = False
                assets["jump_sound"].play()

            state.player_vel_y += 1
            state.player_rect.y += state.player_vel_y
            if state.player_rect.bottom >= GROUND_Y:
                state.player_rect.bottom = GROUND_Y
                state.player_vel_y = 0
                state.on_ground = True

            # Update and draw obstacles
            for obstacle in obstacles:
                obstacle["rect"].x -= OBSTACLE_SPEED

                # Reset obstacle when it goes off screen, and update score
                if obstacle["rect"].right < 0:
                    obstacle["rect"].left = WIDTH + random.randint(600, 1000)
                    obstacle["asset"] = random.choice(assets["obstacles"])
                    obstacle["sound_played"] = False
                    state.score += 1

                # Play the obstacle’s sound only when it first becomes visible from the right
                if not obstacle["sound_played"] and obstacle["rect"].left < WIDTH:
                    obstacle["asset"]["sound"].play()
                    obstacle["sound_played"] = True

                screen.blit(obstacle["asset"]["img"], obstacle["rect"])

            # Collision detection
            if any(state.player_rect.colliderect(obstacle["rect"]) for obstacle in obstacles):
                assets["gameover_sound"].play()
                return

            screen.blit(assets["jump"] if not state.on_ground else assets["run"], state.player_rect)

            if state.score >= 6:
                state.you_won = True
                state.game_active = False

        elif state.you_won:
            screen.blit(assets["run"], state.player_rect)

            for obstacle in obstacles:
                obstacle["rect"].x += OBSTACLE_SPEED * 2
                screen.blit(obstacle["asset"]["img"], obstacle["rect"])

            if not state.victory_sound_played:
                assets["victory_sound"].play()
                state.victory_sound_played = True

            if state.victory_rect.centerx > WIDTH // 2:
                state.victory_rect.x -= 7
            else:
                state.restart_ready = True

            screen.blit(assets["victory_lady"], state.victory_rect)

            if state.restart_ready:
                msg = FONT.render("You won! Press R to restart", True, YELLOW)
                screen.blit(msg, (WIDTH // 2 - 300, HEIGHT // 2))

            if keys[pygame.K_r]:
                return

        else:
            screen.blit(assets["cry"], state.player_rect)
            msg = FONT.render("Game Over! Press R to restart", True, (255, 0, 0))
            screen.blit(msg, (WIDTH // 2 - 300, HEIGHT // 2))
            if keys[pygame.K_r]:
                return

        score_msg = FONT.render(f"Score: {state.score}", True, WHITE)
        screen.blit(score_msg, (20, 20))
        pygame.display.flip()

# MAIN LOOP
if __name__ == "__main__":
    state = GameState()
    selected_player = start_menu()
    assets = load_assets(selected_player)
    while True:
        run_game(assets, state)