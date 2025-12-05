import pygame
import random
import os

# --- 1. TỰ ĐỘNG TÌM ĐƯỜNG DẪN ẢNH ---
# Lấy vị trí của file monster.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Ghép thành đường dẫn đến folder ảnh
IMG_DIR = os.path.join(BASE_DIR, "Images", "Monster")

class Monster:
    def __init__(self, monster_type, screen_width, ground_y):
        self.type = monster_type
        
        # --- CẤU HÌNH ---
        if monster_type == "Microwave":
            img_name = "Walk.png"
            self.frame_w, self.frame_h = 80, 80
            scale = 3
            self.speed = 3
        elif monster_type == "Frogger":
            img_name = "frogger_move.png"
            self.frame_w, self.frame_h = 384, 128
            scale = 1
            self.speed = 4
        
        # --- LOAD ẢNH ---
        self.image = None
        self.frames = []
        self.frame_index = 0
        self.animation_speed = 0.15

        # Tạo đường dẫn đầy đủ tới file ảnh
        full_path = os.path.join(IMG_DIR, monster_type, img_name)
        
        # In ra để kiểm tra (DEBUG)
        # print(f"Đang tìm ảnh tại: {full_path}")

        if os.path.exists(full_path):
            try:
                # Load tấm ảnh lớn (Sprite Sheet)
                sheet = pygame.image.load(full_path).convert_alpha()
                sheet_w = sheet.get_width()
                
                # Tính toán số lượng khung hình (frames)
                num_frames = sheet_w // self.frame_w
                
                # Cắt nhỏ từng frame
                for i in range(num_frames):
                    frame = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
                    # Cắt từ vị trí x = i * chiều rộng
                    frame.blit(sheet, (0, 0), (i * self.frame_w, 0, self.frame_w, self.frame_h))
                    
                    # Phóng to
                    new_w = int(self.frame_w * scale)
                    new_h = int(self.frame_h * scale)
                    scaled_frame = pygame.transform.scale(frame, (new_w, new_h))
                    
                    self.frames.append(scaled_frame)
                
                # Lấy frame đầu tiên làm ảnh mặc định
                if self.frames:
                    self.image = self.frames[0]
                    # print(f"--> OK: Đã load được {monster_type}")

            except Exception as e:
                print(f"LỖI KHI ĐỌC ẢNH {monster_type}: {e}")
        else:
            print(f"!!! KHÔNG TÌM THẤY FILE: {full_path}")

        # --- NẾU KHÔNG CÓ ẢNH -> DÙNG KHỐI ĐỎ ---
        if self.image is None:
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0)) # Màu đỏ cảnh báo
            self.frames = [self.image] # List frame ảo

        # --- VỊ TRÍ ---
        self.rect = self.image.get_rect()
        self.rect.x = screen_width  # Xuất hiện ở mép phải
        self.rect.bottom = ground_y # Chân chạm đất

    def move(self):
        # Di chuyển sang trái
        self.rect.x -= self.speed
        
        # Cập nhật hoạt hình (Animation)
        if len(self.frames) > 1:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.image = self.frames[int(self.frame_index)]

    def draw(self, screen):
        # Vẽ hình ảnh lên màn hình
        screen.blit(self.image, self.rect)

class MonsterSpawner:
    def __init__(self, screen_width, screen_height, ground_y):
        self.width = screen_width
        self.height = screen_height
        self.ground_y = ground_y
        
        self.monsters = [] 
        
        self.timer = 0
        self.spawn_delay = 120 # Khoảng 2 giây (60 fps * 2)

    def update(self, screen):
        # 1. LOGIC SINH QUÁI
        self.timer += 1
        if self.timer >= self.spawn_delay:
            self.spawn()
            self.timer = 0
        
        # 2. DI CHUYỂN VÀ VẼ
        # Duyệt ngược danh sách để xóa an toàn
        for monster in self.monsters[:]: 
            monster.move()
            monster.draw(screen)
            
            # Xóa nếu ra khỏi màn hình
            if monster.rect.right < 0:
                self.monsters.remove(monster)

    def spawn(self):
        # Chọn ngẫu nhiên loại quái: Microwave hoặc Frogger
        m_type = random.choice(["Microwave", "Frogger"])
        new_monster = Monster(m_type, self.width, self.ground_y)
        self.monsters.append(new_monster)