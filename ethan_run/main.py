import pygame
import sys
import os
import random

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Set screen dimensions (doubled)
WIDTH, HEIGHT = 1600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ethan Run!")

# Clock and font
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 64)

# Colors
SKY_BLUE = (60, 60, 60)        # almost black background
GROUND_COLOR = (92, 64, 51)    # dark grey-brown ground strip

# Ground position
GROUND_Y = HEIGHT - 100

# Load assets
ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

ethan_run = pygame.image.load(os.path.join(ASSET_DIR, "ethan_run.png")).convert_alpha()
ethan_jump = pygame.image.load(os.path.join(ASSET_DIR, "ethan_jump.png")).convert_alpha()
ethan_cry = pygame.image.load(os.path.join(ASSET_DIR, "ethan_cry.png")).convert_alpha()
wolf_img = pygame.image.load(os.path.join(ASSET_DIR, "big_bad_wolf.png")).convert_alpha()

ethan_run = pygame.transform.smoothscale(ethan_run, (140, 140))
ethan_jump = pygame.transform.smoothscale(ethan_jump, (140, 140))
ethan_cry = pygame.transform.smoothscale(ethan_cry, (140, 140))
wolf_img = pygame.transform.smoothscale(wolf_img, (160, 130))

jump_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "jump_sound.mp3"))
hit_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "gg_sound.mp3"))

# Player setup
player = pygame.Rect(200, GROUND_Y - 140, 140, 140)
player_vel_y = 0
gravity = 1
jump_strength = 35
on_ground = True
game_active = True
score = 0

# Obstacles
obstacles = []
for i in range(1):
    rect = pygame.Rect(WIDTH + i * 600, GROUND_Y - 130, 160, 130)
    obstacles.append(rect)

# Main loop
running = True
while running:
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GROUND_COLOR, (0, GROUND_Y, WIDTH, 100))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if game_active:
        if keys[pygame.K_SPACE] and on_ground:
            player_vel_y = -jump_strength
            on_ground = False
            jump_sound.play()

        player_vel_y += gravity
        player.y += player_vel_y

        if player.bottom >= GROUND_Y:
            player.bottom = GROUND_Y
            player_vel_y = 0
            on_ground = True

        for obstacle in obstacles:
            obstacle.x -= 9
            if obstacle.right < 0:
                obstacle.left = WIDTH + random.randint(300, 600)
                score += 1
            screen.blit(wolf_img, obstacle)

        if any(player.colliderect(obstacle) for obstacle in obstacles):
            hit_sound.play()
            game_active = False

        if not on_ground:
            screen.blit(ethan_jump, player)
        else:
            screen.blit(ethan_run, player)

    else:
        screen.blit(ethan_cry, player)
        text = font.render("Game Over! Press R to Restart", True, (255, 0, 0))
        screen.blit(text, (WIDTH // 2 - 300, HEIGHT // 2))

        if keys[pygame.K_r]:
            game_active = True
            player.y = GROUND_Y - 100
            player_vel_y = 0
            obstacles = [pygame.Rect(WIDTH + i * 600, GROUND_Y - 130, 160, 130) for i in range(1)]
            score = 0

    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

# Run the game if executed as a script
if __name__ == "__main__":
    main()