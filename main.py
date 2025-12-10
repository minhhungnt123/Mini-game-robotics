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

# --- HÀM LOAD CÂU HỎI TỪ JSON ---
def load_all_questions(filepath):
    """Đọc file JSON và trả về dữ liệu"""
    if not os.path.exists(filepath):
        print(f"CẢNH BÁO: Không tìm thấy file {filepath}")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Lỗi đọc JSON: {e}")
        return None

# --- HÀM LẤY CÂU HỎI THEO ĐỘ KHÓ ---
def get_question_by_difficulty(game_data, difficulty="easy"):
    """Lấy ngẫu nhiên 1 câu hỏi từ danh sách easy/medium/hard"""
    if not game_data: return None
    
    # Kiểm tra xem độ khó này có trong file JSON không
    if difficulty in game_data:
        question_list = game_data[difficulty]
        if question_list and len(question_list) > 0:
            return random.choice(question_list)
    
    # Nếu không tìm thấy hoặc danh sách rỗng, thử lấy Easy
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
                # result là True (đúng) hoặc False (sai)
                if result == True:
                    print("Trả lời ĐÚNG!")
                    # Xóa con quái đầu tiên
                    if len(monster_spawner.monsters) > 0:
                        monster_spawner.monsters.pop(0)
                        monster_spawner.waiting_for_spawn = False 
                else:
                    print("Trả lời SAI!")
                    # Tạm thời sai vẫn cho qua (hoặc bạn có thể trừ máu ở đây)
                    if len(monster_spawner.monsters) > 0:
                        monster_spawner.monsters.pop(0)
                        monster_spawner.waiting_for_spawn = False 
            
    game_is_moving = True 
    
    # Logic va chạm với quái
    if len(monster_spawner.monsters) > 0:
        target_monster = monster_spawner.monsters[0]
        # Tính khoảng cách giữa người chơi và quái
        distance = target_monster.rect.centerx - player.rect.centerx
        
        # Nếu khoảng cách < 800px thì dừng màn hình và hiện câu hỏi
        if 0 < distance < 800: 
            game_is_moving = False
            
            # Nếu bảng chưa hiện thì mới bắt đầu hỏi
            if not quiz_ui.is_active:
                monster_type = target_monster.type
                
                # --- CHỌN ĐỘ KHÓ DỰA VÀO QUÁI ---
                difficulty = "easy" 
                
                if monster_type == "Frogger":
                    difficulty = "easy"      # Ếch thì hỏi dễ
                elif monster_type == "Microwave":
                    difficulty = "medium"    # Lò vi sóng thì hỏi trung bình
                    # Hoặc random cả khó: 
                    # difficulty = random.choice(["medium", "hard"])
                
                # Lấy câu hỏi từ dữ liệu
                raw_q = get_question_by_difficulty(GAME_DATA, difficulty)
                
                if raw_q:
                    # Chuyển đổi format cho QuizManager
                    # JSON của bạn dùng "answer" (index), QuizManager dùng "correct_index"
                    question_data = {
                        "question": raw_q["question"],
                        "options": raw_q["options"],
                        "correct_index": raw_q["answer"]
                    }
                    quiz_ui.start_quiz(question_data)
                else:
                    print("Lỗi: Không lấy được câu hỏi nào!")
                    # Fallback để game không bị đứng
                    quiz_ui.start_quiz({
                        "question": "Lỗi dữ liệu!", 
                        "options": ["...", "...", "...", "..."], 
                        "correct_index": 0
                    })
    
    # Update Animation người chơi
    if game_is_moving:
        player.set_action("WALK")
    else:
        player.set_action("IDLE")
    
    player.update() 
    
    # Vẽ mọi thứ lên màn hình
    background.draw(screen)      
    game_map.draw(screen, is_moving=game_is_moving)        
    monster_spawner.update(screen, is_moving=game_is_moving)  
    screen.blit(player.image, player.rect)
    
    # Vẽ bảng câu hỏi (luôn vẽ cuối cùng để nằm trên cùng)
    quiz_ui.draw(screen)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()