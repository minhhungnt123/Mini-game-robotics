import pygame
import sys
from player import Player
from map import Map
from plx import ParallaxBackground
from monster import MonsterSpawner

# --- KHỞI TẠO ---
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Robotics Mini Game')
clock = pygame.time.Clock()
running = True

# --- KHỞI TẠO ĐỐI TƯỢNG ---
background = ParallaxBackground(WIDTH, HEIGHT)
game_map = Map()
player = Player(200, 500) 

monster_spawner = MonsterSpawner(WIDTH, HEIGHT, 550)

# --- VÒNG LẶP GAME ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
            
    game_is_moving = True 
    
    # Logic dừng game khi gặp quái
    if len(monster_spawner.monsters) > 0:
        target_monster = monster_spawner.monsters[0]
        # Tính khoảng cách
        distance = target_monster.rect.left - player.rect.right
        
        if 0 < distance < 400: 
            game_is_moving = False
    
    # Update trạng thái Player
    if game_is_moving:
        player.set_action("WALK")
    else:
        player.set_action("IDLE")
    
    player.update() 
    
    # Vẽ
    background.draw(screen)      
    game_map.draw(screen, is_moving=game_is_moving)        
    monster_spawner.update(screen, is_moving=game_is_moving)  
    screen.blit(player.image, player.rect)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()