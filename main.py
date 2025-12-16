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
from menu import Menu, GameOverMenu

# --- CẤU HÌNH ĐƯỜNG DẪN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTION_FILE = os.path.join(BASE_DIR, "questions.json")

# Danh sách ảnh background
NORMAL_BG_FILES = [
    "Images/parallax background/plx-1.png",
    "Images/parallax background/plx-2.png"
]

GAMEOVER_BG_FILES = [
    "Images/parallax background/plx-gameover-1.png",
    "Images/parallax background/plx-gameover-2.png"
]

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
bg_normal = ParallaxBackground(WIDTH, HEIGHT, NORMAL_BG_FILES)
bg_gameover = ParallaxBackground(WIDTH, HEIGHT, GAMEOVER_BG_FILES)

game_map = Map()
menu = Menu(WIDTH, HEIGHT)
game_over_menu = GameOverMenu(WIDTH, HEIGHT) 
quiz_ui = QuizManager(WIDTH, HEIGHT)

# --- CẤU HÌNH GAMEPLAY & CINEMATIC ---
START_PLAYER_X = -500
DEFAULT_PLAYER_X = 80
player = Player(START_PLAYER_X, 580) 

monster_spawner = MonsterSpawner(WIDTH, HEIGHT, 650)

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

ground_offset_target = 0
ground_offset_current = 400 

# --- QUẢN LÝ TRẠNG THÁI ---
cinematic_phase = 0
cinematic_timer = 0 
combat_state = "NONE" 
combat_timer = 0 

game_state = "MENU_INTRO"
menu.trigger_intro()

def draw_hearts(screen, lives, max_lives, y_pos):
    for i in range(max_lives):
        if i < lives:
            screen.blit(heart_img, (20 + i * 45, y_pos))

# --- HÀM RESET GAME ---
def reset_game():
    global player_lives, game_state, combat_state, ground_offset_current, cinematic_phase, heart_y_current
    
    # Reset chỉ số
    player_lives = 5
    combat_state = "NONE"
    game_over_menu.reset() 
    
    # Reset vị trí vật lý
    ground_offset_current = 400      
    player.rect.x = START_PLAYER_X   
    heart_y_current = -100           
    
    # Reset Entity
    player.set_action("IDLE") 
    monster_spawner.monsters = []
    monster_spawner.waiting_for_spawn = False
    
    # Bắt đầu lại Cinematic
    game_state = "GAME_CINEMATIC" 
    cinematic_phase = 0 

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
        
        if game_state == "GAME_OVER":
            action = game_over_menu.handle_input(event)
            if action == "RESTART":
                reset_game()

    # ================= LOGIC GAME =================
    
    # 1. MENU PHASES
    if game_state in ["MENU_INTRO", "MENU_ACTIVE", "MENU_OUTRO"]:
        status = menu.update()
        if status == "ACTIVE":
            game_state = "MENU_ACTIVE"
        elif status == "DONE":
            game_state = "GAME_CINEMATIC"
            cinematic_phase = 0 
            player.rect.x = START_PLAYER_X 

        bg_normal.draw(screen) 
        game_map.draw(screen, is_moving=False, offset_y=400) 
        menu.draw(screen)

    # 2. CINEMATIC PHASES
    elif game_state == "GAME_CINEMATIC":
        bg_normal.draw(screen)

        # --- Phase 0: Đất bay lên ---
        if cinematic_phase == 0:
            if ground_offset_current > ground_offset_target:
                ground_offset_current -= 8 
            else:
                ground_offset_current = ground_offset_target
                cinematic_phase = 1
                cinematic_timer = pygame.time.get_ticks() 

        # --- Phase 1: Chờ ngắn ---
        elif cinematic_phase == 1:
            if pygame.time.get_ticks() - cinematic_timer >= 500: 
                cinematic_phase = 2
        
        # --- Phase 2: Player & Heart bay vào ---
        elif cinematic_phase == 2:
            # Player chạy vào
            player_done = False
            if player.rect.x < DEFAULT_PLAYER_X:
                player.rect.x += 6
                player.set_action("WALK") 
                player.update()
            else:
                player.rect.x = DEFAULT_PLAYER_X
                # [QUAN TRỌNG] Không set IDLE ở đây nữa, để nó tự chuyển trong PLAYING
                player_done = True
            
            # Heart bay xuống
            heart_done = False
            if heart_y_current < heart_y_target:
                heart_y_current += 3
            else:
                heart_y_current = heart_y_target
                heart_done = True

            if player_done and heart_done:
                game_state = "PLAYING"
                # Spawn quái ngay lập tức
                monster_spawner.last_spawn_time = pygame.time.get_ticks() - 5000 

        game_map.draw(screen, is_moving=True, offset_y=ground_offset_current)
        screen.blit(player.image, player.rect)
        draw_hearts(screen, player_lives, max_lives, heart_y_current)

    # 3. PLAYING PHASE & GAME OVER
    elif game_state in ["PLAYING", "COOLDOWN", "GAME_OVER"]:
        
        # --- A. LOGIC CẬP NHẬT ---
        if game_state != "GAME_OVER":
            quiz_result = quiz_ui.update()
            
            if quiz_result is not None:
                target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None
                if quiz_result == True: 
                    combat_state = "VICTORY_PHASE_1"
                    player.set_action("ATTACK")
                    if target_monster: target_monster.set_action("IDLE")
                else: 
                    combat_state = "DEFEAT_PHASE_1"
                    if target_monster: target_monster.set_action("ATTACK")
                    player.set_action("IDLE")
            
            # Kiểm tra va chạm / Quiz
            if len(monster_spawner.monsters) > 0 and combat_state == "NONE":
                 target_monster = monster_spawner.monsters[0]
                 distance = target_monster.rect.centerx - player.rect.centerx
                 if 0 < distance < 700:
                     game_is_moving = False
                     # [QUAN TRỌNG] Gặp quái mới đứng lại (IDLE)
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
                             quiz_ui.start_quiz({"question":"1+1=?","options":["1","2"],"correct_index":1})
                 else:
                     # Chưa gặp quái -> Đi tiếp
                     game_is_moving = True
            else:
                 # Không có quái -> Đi tiếp
                 game_is_moving = True

            # [QUAN TRỌNG] Logic Animation: Nếu đất trôi -> Player chạy
            if combat_state == "NONE":
                if game_is_moving:
                    player.set_action("WALK")
                # Lưu ý: Không set IDLE ở đây vì logic dừng đã xử lý ở trên (khi distance < 700)

            # State Machine Combat
            if combat_state != "NONE":
                game_is_moving = False
                target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None
                
                if combat_state == "VICTORY_PHASE_1":
                    if player.animation_finished:
                        combat_state = "VICTORY_PHASE_2"
                        player.set_action("IDLE") 
                        if target_monster: target_monster.set_action("DEATH")
                elif combat_state == "VICTORY_PHASE_2":
                    monster_done = target_monster.animation_finished if target_monster else True
                    if monster_done:
                        if len(monster_spawner.monsters) > 0: monster_spawner.monsters.pop(0)
                        combat_state = "COOLDOWN"
                        combat_timer = pygame.time.get_ticks() 
                        player.set_action("IDLE") 

                elif combat_state == "DEFEAT_PHASE_1":
                    monster_done = target_monster.animation_finished if target_monster else True
                    if monster_done:
                        combat_state = "DEFEAT_PHASE_2"
                        if target_monster: target_monster.set_action("IDLE") 
                        player.set_action("HIT")
                        player_lives -= 1
                        if player_lives <= 0: player_lives = 0

                elif combat_state == "DEFEAT_PHASE_2":
                    if player.animation_finished:
                        if player_lives == 0:
                            combat_state = "PLAYER_DYING"
                            player.set_action("DEATH")
                        else:
                            combat_state = "COOLDOWN"
                            combat_timer = pygame.time.get_ticks()
                            player.set_action("IDLE")
                
                elif combat_state == "PLAYER_DYING":
                    if player.animation_finished:
                        game_state = "GAME_OVER"
                        ground_offset_current = 0 

                elif combat_state == "COOLDOWN":
                    if pygame.time.get_ticks() - combat_timer > 1500:
                        combat_state = "NONE"
                        player.set_action("WALK")
                        monster_spawner.waiting_for_spawn = False 

            player.update()
            
            # [FIX VẤN ĐỀ 1 - TĂNG TỐC QUÁI]
            if monster_spawner.monsters:
                for m in monster_spawner.monsters:
                    dist_to_player = m.rect.x - player.rect.x
                    # Nếu quái ở rất xa (>900px) -> Chạy cực nhanh (15px/frame)
                    if dist_to_player > 900:
                         m.rect.x -= 15 
                    # Nếu quái ở hơi xa (>750px) -> Chạy nhanh vừa (5px/frame)
                    elif dist_to_player > 750:
                         m.rect.x -= 5
                         
            monster_spawner.update(is_moving=game_is_moving)
        
        else:
            # === LOGIC GAME OVER ===
            game_is_moving = False
            current_alpha = game_over_menu.update()
            
            # Đất trôi xuống
            if ground_offset_current < 500: 
                ground_offset_current += 5 
            
            monster_spawner.update(is_moving=False)

        # --- B. LOGIC VẼ (RENDER) ---
        
        if game_state == "GAME_OVER":
            bg_normal.draw(screen)
            bg_gameover.draw(screen, alpha=game_over_menu.alpha)
            
            # Vẽ Map trôi xuống
            game_map.draw(screen, is_moving=False, offset_y=ground_offset_current)
            
            # [FIX VẤN ĐỀ 2] Vẽ Player trôi xuống theo đất
            if game_over_menu.alpha < 250:
                 screen.blit(player.image, (player.rect.x, player.rect.y + ground_offset_current))

            game_over_menu.draw(screen)

        else:
            bg_normal.draw(screen)
            game_map.draw(screen, is_moving=game_is_moving, offset_y=0) 
            monster_spawner.draw(screen)
            screen.blit(player.image, player.rect)
            draw_hearts(screen, player_lives, max_lives, heart_y_current)
            quiz_ui.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()