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
    heart_path = os.path.join(BASE_DIR, "Images", "Map", "hearth.png")
    if os.path.exists(heart_path):
        heart_img = pygame.image.load(heart_path).convert_alpha()
        heart_img = pygame.transform.scale(heart_img, (40, 40))
    else:
        raise Exception("Heart image missing")
except:
    heart_img = pygame.Surface((40,40))
    heart_img.fill((255, 0, 0))

combat_state = "NONE" # NONE, VICTORY, DEFEAT, GAME_OVER

# --- VÒNG LẶP GAME ---
while running:
    # 1. XỬ LÝ SỰ KIỆN (CHỈ DÙNG 1 VÒNG LẶP DUY NHẤT)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if quiz_ui.is_active:
            quiz_ui.handle_input(event)

    # 2. CẬP NHẬT LOGIC QUIZ
    # Kiểm tra xem người chơi đã trả lời xong chưa (hiệu ứng fade out xong chưa)
    quiz_result = quiz_ui.update()
    
    if quiz_result is not None:
        # Lấy quái vật hiện tại để set animation
        target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None

        if quiz_result == True: # Trả lời ĐÚNG
            print("ĐÚNG! Tấn công quái.")
            combat_state = "VICTORY"
            player.set_action("ATTACK")
            if target_monster:
                target_monster.set_action("DEATH")
        else: # Trả lời SAI
            print("SAI! Bị thương.")
            combat_state = "DEFEAT"
            player.set_action("HIT")
            if target_monster:
                target_monster.set_action("ATTACK") # Hoặc animation tấn công của quái

            player_lives -= 1
            if player_lives <= 0:
                player_lives = 0
                combat_state = "GAME_OVER"
                player.set_action("DEATH")

    # 3. QUẢN LÝ TRẠNG THÁI GAME (STATE MACHINE)
    game_is_moving = True # Mặc định là di chuyển

    if combat_state != "NONE":
        game_is_moving = False # Đang đánh nhau thì nền không trôi
        
        # --- XỬ LÝ KHI ANIMATION KẾT THÚC ---
        if combat_state == "VICTORY":
            target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None
            
            # Kiểm tra cả 2 đã diễn xong chưa
            player_done = player.animation_finished
            monster_done = target_monster.animation_finished if target_monster else True

            if player_done and monster_done:
                # Xóa quái vật đã chết
                if len(monster_spawner.monsters) > 0:
                    monster_spawner.monsters.pop(0)
                    monster_spawner.waiting_for_spawn = False
                
                # Reset trạng thái để đi tiếp
                combat_state = "NONE"
                player.set_action("WALK")

        elif combat_state == "DEFEAT":
            target_monster = monster_spawner.monsters[0] if monster_spawner.monsters else None
            player_done = player.animation_finished
            monster_done = target_monster.animation_finished if target_monster else True

            if player_done and monster_done:
                # Logic cũ của bạn: quái biến mất sau khi đánh mình (để game đi tiếp)
                if len(monster_spawner.monsters) > 0:
                    monster_spawner.monsters.pop(0)
                    monster_spawner.waiting_for_spawn = False
                
                combat_state = "NONE"
                player.set_action("WALK")
        
        elif combat_state == "GAME_OVER":
            game_is_moving = False
            # Ở đây bạn có thể vẽ thêm màn hình Game Over hoặc nút Restart

    # 4. KIỂM TRA VA CHẠM (NẾU KHÔNG TRONG COMBAT)
    else: # combat_state == "NONE"
        if len(monster_spawner.monsters) > 0:
            target_monster = monster_spawner.monsters[0]
            # Tính khoảng cách
            distance = target_monster.rect.centerx - player.rect.centerx
            
            if 0 < distance < 800: 
                game_is_moving = False
                player.set_action("IDLE")
                
                # Chỉ bật quiz nếu chưa bật
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
                        # Fallback nếu không load được câu hỏi
                        quiz_ui.start_quiz({
                            "question": "1 + 1 = ?", 
                            "options": ["1", "2", "3", "4"], 
                            "correct_index": 1
                        })

    # 5. UPDATE CÁC ĐỐI TƯỢNG (CHỈ GỌI 1 LẦN DUY NHẤT)
    player.update()
    
    # Monster update nhận vào biến is_moving
    if game_is_moving:
        monster_spawner.update(is_moving=True)
    else:
        monster_spawner.update(is_moving=False)

    # 6. VẼ RA MÀN HÌNH (RENDER - CHỈ GỌI 1 LẦN DUY NHẤT)
    background.draw(screen)
    game_map.draw(screen, is_moving=game_is_moving)
    monster_spawner.draw(screen)
    screen.blit(player.image, player.rect)

    # Vẽ thanh máu
    for i in range(max_lives):
        if i < player_lives:
            screen.blit(heart_img, (20 + i * 45, 20))

    # Vẽ UI câu hỏi sau cùng
    quiz_ui.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()