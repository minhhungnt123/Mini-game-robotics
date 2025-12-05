import pygame
import sys
from player import Player
from map import Map
from plx import ParallaxBackground
from monster import MonsterSpawner

# --- KHỞI TẠO CƠ BẢN ---
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Robotics Mini Game')
clock = pygame.time.Clock()
running = True

# --- TẠO ĐỐI TƯỢNG ---
background = ParallaxBackground(WIDTH, HEIGHT)
game_map = Map()

ground_height = game_map.image.get_height()
if ground_height > 200: 
    ground_y = HEIGHT - 90
else:
    ground_y = HEIGHT - ground_height

player = Player(100, ground_y)
player.rect.bottom = ground_y

ground_y = 500
monster = MonsterSpawner(WIDTH, HEIGHT, ground_y)

# --- VÒNG LẶP GAME ---
while running:
    current_time = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
            
    # 2. Cập nhật logic
    player.update()
    
    # 3. Vẽ hình
    background.draw(screen)    # Layer 0
    game_map.draw(screen)       # Layer 1
    
    monster.update(screen)
    
    screen.blit(player.image, player.rect) 
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()