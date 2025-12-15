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
# --- VÒNG LẶP GAME ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if quiz_ui.is_active:
            quiz_ui.handle_input(event)

    # ===== UPDATE QUIZ (BẮT BUỘC) =====
    quiz_result = quiz_ui.update()
    if quiz_result is not None:
        target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None

        if quiz_result:
            combat_state = "VICTORY"
            player.set_action("ATTACK")
            if target_monster:
                target_monster.set_action("DEATH")
        else:
            combat_state = "DEFEAT"
            player.set_action("HIT")
            if target_monster:
                target_monster.set_action("ATTACK")

            player_lives -= 1
            if player_lives <= 0:
                player_lives = 0
                combat_state = "GAME_OVER"
                player.set_action("DEATH")

    # ===== PHẦN CŨ GIỮ NGUYÊN =====
    game_is_moving = combat_state == "NONE"

    player.update()

    if game_is_moving:
        monster_spawner.update(is_moving=True)
    else:
        monster_spawner.update(is_moving=False)

    background.draw(screen)
    game_map.draw(screen, is_moving=game_is_moving)
    monster_spawner.draw(screen)
    screen.blit(player.image, player.rect)

    for i in range(max_lives):
        if i < player_lives:
            screen.blit(heart_img, (20 + i * 45, 20))

    quiz_ui.draw(screen)

    pygame.display.flip()
    clock.tick(60)

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
        
        # --- [SỬA ĐỔI QUAN TRỌNG] ---
        if combat_state == "VICTORY":
            # Lấy quái vật hiện tại
            target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None
            
            # Kiểm tra xem CẢ HAI đã diễn xong animation chưa
            player_done = player.animation_finished
            monster_done = target_monster.animation_finished if target_monster else True

            # Chỉ khi cả 2 xong (đặc biệt là quái đã diễn xong cảnh chết) mới xóa
            if player_done and monster_done:
                if len(monster_spawner.monsters) > 0:
                    monster_spawner.monsters.pop(0)
                    monster_spawner.waiting_for_spawn = False
                combat_state = "NONE"
                player.set_action("WALK")

        elif combat_state == "DEFEAT":
            target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None
            player_done = player.animation_finished
            monster_done = target_monster.animation_finished if target_monster else True

            # Khi trả lời sai, chờ cả 2 diễn xong (Monster đánh xong, Player hết bị thương)
            if player_done and monster_done:
                # Quái đánh xong thì biến mất để đi tiếp (theo logic cũ)
                if len(monster_spawner.monsters) > 0:
                    monster_spawner.monsters.pop(0)
                    monster_spawner.waiting_for_spawn = False
                combat_state = "NONE"
                player.set_action("WALK")
        
        elif combat_state == "GAME_OVER":
            if player.animation_finished:
                # Có thể hiện màn hình Game Over ở đây
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
    
    # Quan trọng: Monster Update ở đây chỉ tính toán animation
    if game_is_moving:
        monster_spawner.update(is_moving=True)
    else:
        # Khi dừng màn hình (trả lời hoặc combat), quái vẫn cần update để chạy animation (is_moving=False)
        monster_spawner.update(is_moving=False)

    # --- VẼ RA MÀN HÌNH (RENDER) ---
    background.draw(screen)                  
    game_map.draw(screen, is_moving=game_is_moving) 
    monster_spawner.draw(screen)             # Vẽ quái sau Background/Map để không bị che
    screen.blit(player.image, player.rect)   
    
    # Vẽ thanh máu
    for i in range(max_lives):
        x = 20 + i * 45
        y = 20
        if i < player_lives:
            screen.blit(heart_img, (x, y))

    # Vẽ UI câu hỏi
    quiz_ui.draw(screen)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()