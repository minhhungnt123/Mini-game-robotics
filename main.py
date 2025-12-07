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

# --- TẠO ĐỐI TƯỢNG ---
background = ParallaxBackground(WIDTH, HEIGHT)
game_map = Map()

ground_height = game_map.image.get_height()
ground_y = HEIGHT - ground_height + 30 # +30 để chân nhân vật lún xuống đất một chút cho thật

player = Player(200, ground_y) # Đặt player ở vị trí x=200 cố định

monster_spawner = MonsterSpawner(WIDTH, HEIGHT, ground_y)

# --- VÒNG LẶP GAME ---
while running:
    # 1. Xử lý sự kiện thoát
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
            
    # 2. LOGIC KIỂM SOÁT TRẠNG THÁI (CHẠY HAY DỪNG)
    game_is_moving = True # Mặc định là chạy
    
    # Kiểm tra xem có quái nào đang ở trên màn hình không
    if len(monster_spawner.monsters) > 0:
        # Lấy con quái gần nhất (con đầu tiên trong list)
        target_monster = monster_spawner.monsters[0]
        
        # Tính khoảng cách giữa Player và Quái
        # Nếu quái đi đến vị trí cách Player khoảng 150px thì DỪNG LẠI
        distance = target_monster.rect.left - player.rect.right
        
        if distance < 100: # 100px là khoảng cách dừng (safe distance)
            game_is_moving = False
    
    # 3. CẬP NHẬT ĐỐI TƯỢNG THEO TRẠNG THÁI
    
    # Player: Nếu game chạy -> Run, Game dừng -> Idle
    if game_is_moving:
        player.set_action("RUN")
    else:
        player.set_action("IDLE")
    
    player.update() # Update animation
    
    background.draw(screen)      
    
    # Map: Truyền biến game_is_moving vào
    game_map.draw(screen, is_moving=game_is_moving)        
    
    # Monster: Truyền biến game_is_moving vào
    monster_spawner.update(screen, is_moving=game_is_moving)  
    
    screen.blit(player.image, player.rect)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()