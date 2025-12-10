import pygame
import sys
import random # <--- Thêm import random
from player import Player
from map import Map
from plx import ParallaxBackground
from monster import MonsterSpawner
from quiz import QuizManager # <--- Import file quiz vừa tạo

# --- DANH SÁCH CÂU HỎI MẪU ---
QUESTIONS = [
    {"question": "1 + 1 = ?", "options": ["1", "2", "3", "4"], "correct_index": 1},
    {"question": "Trai dat hinh gi?", "options": ["Hinh vuong", "Hinh cau", "Hinh tam giac", "Hinh thang"], "correct_index": 1},
    {"question": "Con gi keu Meo Meo?", "options": ["Con Cho", "Con Lon", "Con Meo", "Con Ga"], "correct_index": 2},
]

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
player = Player(200, 480) 
monster_spawner = MonsterSpawner(WIDTH, HEIGHT, 550)

# Khởi tạo bộ quản lý câu đố
quiz_ui = QuizManager(WIDTH, HEIGHT) # <--- Thêm dòng này

# --- VÒNG LẶP GAME ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        
        # --- XỬ LÝ TRẢ LỜI CÂU HỎI ---
        if quiz_ui.is_active:
            result = quiz_ui.handle_input(event)
            if result is not None:
                if result == True:
                    print("Đúng rồi! Quái biến mất.")
                    # Xóa con quái đang chặn đường
                    if len(monster_spawner.monsters) > 0:
                        monster_spawner.monsters.pop(0)
                        monster_spawner.waiting_for_spawn = False 
                else:
                    print("Sai rồi! (Có thể trừ máu ở đây)")
                    # Tạm thời vẫn cho qua để test game
                    if len(monster_spawner.monsters) > 0:
                        monster_spawner.monsters.pop(0)
                        monster_spawner.waiting_for_spawn = False 
            
    game_is_moving = True 
    
    # Logic dừng game khi gặp quái (GIỮ NGUYÊN NHƯ Ý BẠN)
    if len(monster_spawner.monsters) > 0:
        target_monster = monster_spawner.monsters[0]
        # Tính khoảng cách
        distance = target_monster.rect.centerx - player.rect.centerx
        
        if 0 < distance < 800: 
            game_is_moving = False
            
            # --- THÊM: KÍCH HOẠT CÂU HỎI KHI GAME DỪNG ---
            # Nếu bảng chưa hiện thì hiện lên
            if not quiz_ui.is_active:
                q = random.choice(QUESTIONS)
                quiz_ui.start_quiz(q)
    
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
    
    # --- VẼ BẢNG CÂU HỎI LÊN TRÊN CÙNG ---
    quiz_ui.draw(screen)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()