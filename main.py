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
from menu import Menu 

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
menu = Menu(WIDTH, HEIGHT)
quiz_ui = QuizManager(WIDTH, HEIGHT)

# --- CẤU HÌNH CINEMATIC ---
# 1. Player: Bắt đầu bên trái ngoài màn hình
START_PLAYER_X = -100
DEFAULT_PLAYER_X = 80
player = Player(START_PLAYER_X, 580) 

monster_spawner = MonsterSpawner(WIDTH, HEIGHT, 650)

# 2. Heart: Bắt đầu bên trên ngoài màn hình
player_lives = 5 
max_lives = 5
heart_y_target = 20
heart_y_current = -100 

try:
    heart_path = os.path.join(BASE_DIR, "Images", "Map", "hearth.png")
    heart_img = pygame.image.load(heart_path).convert_alpha()
    heart_img = pygame.transform.scale(heart_img, (40, 40))
except:
    heart_img = pygame.Surface((40,40))
    heart_img.fill((255, 0, 0))

# 3. Ground: Bắt đầu bên dưới ngoài màn hình (Offset dương lớn)
ground_offset_target = 0
ground_offset_current = 400 # Đẩy xuống 400px

# --- QUẢN LÝ TRẠNG THÁI ---
# Biến phụ cho Cinematic
cinematic_phase = 0 # 0: Ground Fly-in, 1: Wait 2s, 2: Player & Heart Fly-in
cinematic_timer = 0 # Dùng để đếm thời gian chờ

game_state = "MENU_INTRO"
menu.trigger_intro()

combat_state = "NONE" 

def draw_hearts(screen, lives, max_lives, y_pos):
    for i in range(max_lives):
        if i < lives:
            screen.blit(heart_img, (20 + i * 45, y_pos))

# --- VÒNG LẶP CHÍNH ---
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if game_state == "MENU_ACTIVE":
            action = menu.handle_input(event)
            if action == "START":
                menu.trigger_outro()
                game_state = "MENU_OUTRO"
            elif action == "SETTING":
                print("Setting clicked")

        if game_state == "PLAYING" and quiz_ui.is_active:
            quiz_ui.handle_input(event)

    # ================= LOGIC GAME =================
    
    # 1. MENU PHASES
    if game_state in ["MENU_INTRO", "MENU_ACTIVE", "MENU_OUTRO"]:
        status = menu.update()
        if status == "ACTIVE":
            game_state = "MENU_ACTIVE"
        elif status == "DONE":
            # Chuyển sang Cinematic
            game_state = "GAME_CINEMATIC"
            cinematic_phase = 0 # Bắt đầu phase 0: Ground bay vào
            player.set_action("WALK") 

        # Khi ở Menu: Ground bị đẩy xuống dưới (ẩn đi)
        background.draw(screen) 
        # Gọi draw với offset lớn để giấu đất đi
        game_map.draw(screen, is_moving=False, offset_y=400) 
        menu.draw(screen)

    # 2. CINEMATIC PHASES
    elif game_state == "GAME_CINEMATIC":
        # Luôn vẽ background
        background.draw(screen)

        # --- PHASE 0: Ground bay từ dưới lên ---
        if cinematic_phase == 0:
            # Ground di chuyển lên (giảm offset)
            if ground_offset_current > ground_offset_target:
                ground_offset_current -= 5 # Tốc độ bay lên của đất
            else:
                ground_offset_current = ground_offset_target
                # Xong việc bay lên -> Chuyển sang chờ
                cinematic_phase = 1
                cinematic_timer = pygame.time.get_ticks() # Bắt đầu đếm giờ

        # --- PHASE 1: Chờ 2 giây ---
        elif cinematic_phase == 1:
            # Kiểm tra thời gian
            if pygame.time.get_ticks() - cinematic_timer >= 2000: # 2000ms = 2s
                cinematic_phase = 2
        
        # --- PHASE 2: Player & Heart bay vào cùng lúc ---
        elif cinematic_phase == 2:
            # Player chạy vào
            player_done = False
            if player.rect.x < DEFAULT_PLAYER_X:
                player.rect.x += 5
                player.update()
            else:
                player.rect.x = DEFAULT_PLAYER_X
                player.set_action("IDLE")
                player_done = True
            
            # Heart bay xuống
            heart_done = False
            if heart_y_current < heart_y_target:
                heart_y_current += 2
            else:
                heart_y_current = heart_y_target
                heart_done = True

            # Nếu cả 2 đã vào vị trí -> Vào Game
            if player_done and heart_done:
                game_state = "PLAYING"
                monster_spawner.last_spawn_time = pygame.time.get_ticks()

        # --- RENDER TRONG LÚC CINEMATIC ---
        # Ground luôn scroll (is_moving=True) và áp dụng offset hiện tại
        game_map.draw(screen, is_moving=True, offset_y=ground_offset_current)
        
        # Chỉ vẽ Player và Heart khi ở Phase 2 (hoặc nếu bạn muốn vẽ nó chờ ở ngoài cũng được)
        screen.blit(player.image, player.rect)
        draw_hearts(screen, player_lives, max_lives, heart_y_current)


    # 3. PLAYING PHASE (Game chính)
    elif game_state == "PLAYING":
        # ... (Logic game cũ giữ nguyên) ...
        quiz_result = quiz_ui.update()
        target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None

        if quiz_result is not None:
            if quiz_result == True: 
                combat_state = "VICTORY"
                player.set_action("ATTACK")
                if target_monster: target_monster.set_action("DEATH")
            else: 
                combat_state = "DEFEAT"
                player.set_action("HIT")
                if target_monster: target_monster.set_action("ATTACK")
                player_lives -= 1
                if player_lives <= 0:
                    player_lives = 0
                    combat_state = "GAME_OVER"
                    player.set_action("DEATH")
        
        # Sửa logic get question (fix lỗi KeyError)
        if len(monster_spawner.monsters) > 0 and combat_state == "NONE":
             target_monster = monster_spawner.monsters[0]
             distance = target_monster.rect.centerx - player.rect.centerx
             if 0 < distance < 700:
                 game_is_moving = False
                 player.set_action("IDLE")
                 if not quiz_ui.is_active:
                     m_type = target_monster.type
                     diff = "easy" if m_type == "Frogger" else "medium"
                     q_data = get_question_by_difficulty(GAME_DATA, diff)
                     if q_data:
                         # FIX LỖI KEY ERROR TẠI ĐÂY
                         quiz_ui.start_quiz({
                             "question": q_data["question"],
                             "options": q_data["options"],
                             "correct_index": q_data["answer"] # Đổi key 'answer' -> 'correct_index'
                         })
                     else:
                         quiz_ui.start_quiz({"question":"1+1=?","options":["1","2"],"correct_index":1})
        else:
             game_is_moving = True

        if combat_state != "NONE":
            game_is_moving = False
            # Logic animation combat (giữ nguyên)
            player_done = player.animation_finished
            monster_done = target_monster.animation_finished if target_monster else True
            if player_done and monster_done:
                if combat_state in ["VICTORY", "DEFEAT"]:
                    if len(monster_spawner.monsters) > 0:
                        monster_spawner.monsters.pop(0)
                        monster_spawner.waiting_for_spawn = False
                    combat_state = "NONE"
                    player.set_action("WALK")

        # Update & Draw
        player.update()
        monster_spawner.update(is_moving=game_is_moving)

        background.draw(screen)
        # Khi chơi game, offset_y = 0
        game_map.draw(screen, is_moving=game_is_moving, offset_y=0) 
        monster_spawner.draw(screen)
        screen.blit(player.image, player.rect)
        draw_hearts(screen, player_lives, max_lives, heart_y_current)
        quiz_ui.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()