import pygame
import sys
import random
import json
import os
from player import Player
from map import Map
from plx import ParallaxBackground
from monster import MonsterSpawner
from quiz import QuizManager

# --- CẤU HÌNH ĐƯỜNG DẪN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTION_FILE = os.path.join(BASE_DIR, "questions.json")

def load_all_questions(filepath):
    if not os.path.exists(filepath): return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception: return None

def get_question_by_difficulty(game_data, difficulty="easy"):
    if not game_data: return None
    if difficulty in game_data and game_data[difficulty]:
        return random.choice(game_data[difficulty])
    if "easy" in game_data and game_data["easy"]:
        return random.choice(game_data["easy"])
    return None

# --- KHỞI TẠO GAME ---
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Robotics Mini Game')
clock = pygame.time.Clock()
running = True

# --- LOAD DỮ LIỆU ---
GAME_DATA = load_all_questions(QUESTION_FILE)

# --- KHỞI TẠO ĐỐI TƯỢNG ---
background = ParallaxBackground(WIDTH, HEIGHT)
game_map = Map()
player = Player(200, 480) 
monster_spawner = MonsterSpawner(WIDTH, HEIGHT, 550)
quiz_ui = QuizManager(WIDTH, HEIGHT)

# --- THANH MÁU & TRẠNG THÁI ---
player_lives = 5 
max_lives = 5
try:
    heart_img = pygame.image.load(os.path.join(BASE_DIR, "Images", "Map", "hearth.png")).convert_alpha()
    heart_img = pygame.transform.scale(heart_img, (40, 40))
except:
    heart_img = pygame.Surface((40,40))
    heart_img.fill((255, 0, 0))

combat_state = "NONE" # NONE, VICTORY, DEFEAT, GAME_OVER

# --- VÒNG LẶP GAME ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        
        # Xử lý trả lời câu hỏi
        if quiz_ui.is_active:
            result = quiz_ui.handle_input(event)
            if result is not None:
                target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None
                
                if result == True: # ĐÚNG
                    print("ĐÚNG! Tấn công quái.")
                    combat_state = "VICTORY"
                    player.set_action("ATTACK")
                    if target_monster:
                        target_monster.set_action("DEATH")
                        
                else: # SAI
                    print("SAI! Bị thương.")
                    combat_state = "DEFEAT"
                    player.set_action("HIT")
                    if target_monster:
                        target_monster.set_action("ATTACK")
                    
                    player_lives -= 1
                    if player_lives <= 0:
                        player_lives = 0
                        combat_state = "GAME_OVER"
                        player.set_action("DEATH")

    # --- LOGIC UPDATE ---
    game_is_moving = True 
    
    # 1. Kiểm tra Combat
    if combat_state != "NONE":
        game_is_moving = False
        
        # Xử lý kết thúc animation
        if combat_state == "VICTORY":
            if player.animation_finished:
                if len(monster_spawner.monsters) > 0:
                    monster_spawner.monsters.pop(0)
                    monster_spawner.waiting_for_spawn = False
                combat_state = "NONE"
                player.set_action("WALK")

        elif combat_state == "DEFEAT":
            # Chờ player hết bị thương
            if player.animation_finished:
                if len(monster_spawner.monsters) > 0:
                    monster_spawner.monsters.pop(0)
                    monster_spawner.waiting_for_spawn = False
                combat_state = "NONE"
                player.set_action("WALK")
        
        elif combat_state == "GAME_OVER":
            if player.animation_finished:
                # Dừng game ở đây hoặc hiện menu thua
                pass

    # 2. Kiểm tra Va chạm (Nếu không combat)
    if combat_state == "NONE":
        if len(monster_spawner.monsters) > 0:
            target_monster = monster_spawner.monsters[0]
            distance = target_monster.rect.centerx - player.rect.centerx
            
            # Chạm trán quái
            if 0 < distance < 800: 
                game_is_moving = False
                player.set_action("IDLE")
                
                if not quiz_ui.is_active:
                    m_type = target_monster.type
                    diff = "easy" if m_type == "Frogger" else "medium"
                    q_data = get_question_by_difficulty(GAME_DATA, diff)
                    
                    if q_data:
                        quiz_ui.start_quiz({
                            "question": q_data["question"],
                            "options": q_data["options"],
                            "correct_index": q_data["answer"]
                        })
                    else:
                        quiz_ui.start_quiz({
                            "question": "Lỗi dữ liệu", "options": ["A", "B", "C", "D"], "correct_index": 0
                        })

    # 3. Gọi hàm Update
    player.update()
    
    # Quan trọng: Monster Update ở đây chỉ tính toán, KHÔNG vẽ
    if game_is_moving:
        monster_spawner.update(is_moving=True)
    else:
        monster_spawner.update(is_moving=False)

    # --- VẼ RA MÀN HÌNH (RENDER) ---
    # Thứ tự vẽ rất quan trọng: Sau -> đè lên Trước
    
    background.draw(screen)                  # 1. Vẽ nền (xóa màn hình cũ)
    game_map.draw(screen, is_moving=game_is_moving) # 2. Vẽ đất
    monster_spawner.draw(screen)             # 3. Vẽ quái (ĐÃ SỬA: Vẽ sau nền)
    screen.blit(player.image, player.rect)   # 4. Vẽ người chơi
    
    # 5. Vẽ thanh máu
    for i in range(max_lives):
        x = 20 + i * 45
        y = 20
        if i < player_lives:
            screen.blit(heart_img, (x, y))

    # 6. Vẽ UI câu hỏi (trên cùng)
    quiz_ui.draw(screen)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()