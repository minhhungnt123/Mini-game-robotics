import pygame
import os
import random
# --- LOGIC ĐƯỜNG DẪN GIỮ NGUYÊN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "Images", "Monster")

class Monster(pygame.sprite.Sprite):
    def __init__(self, monster_type, screen_width, ground_y):
        super().__init__()
        self.type = monster_type
        self.state = "RUN"
        self.distance_moved = 0
        self.max_distance = 700 # Đi 200px thì dừng
        
        # --- 1. CẤU HÌNH TÊN FILE ẢNH CHO TỪNG LOẠI ---
        # Bạn cần chuẩn bị sẵn file ảnh Idle tương ứng trong folder
        if monster_type == "Microwave":
            walk_img_name = "Walk.png"
            idle_img_name = "Idle.png"  # <--- Tên file ảnh đứng yên
            self.frame_w, self.frame_h = 80, 80
            self.scale = 3              # Lưu scale vào biến để dùng lại
            self.speed = 3
            
        elif monster_type == "Frogger":
            walk_img_name = "frogger_move.png"
            idle_img_name = "frogger_idle.png" # <--- Tên file ảnh đứng yên
            self.frame_w, self.frame_h = 356, 128
            self.scale = 1
            self.speed = 4

        # --- 2. GỌI HÀM LOAD CHO 2 TRẠNG THÁI ---
        self.frames = self.load_animation(walk_img_name)      # List ảnh chạy
        self.idle_frames = self.load_animation(idle_img_name) # List ảnh đứng
        
        # Fallback: Nếu không tìm thấy ảnh Idle, dùng tạm ảnh chạy để không bị lỗi
        if not self.idle_frames:
            print(f"Cảnh báo: Không tìm thấy ảnh Idle cho {monster_type}, dùng tạm ảnh Walk.")
            self.idle_frames = self.frames 

        # --- KHỞI TẠO HÌNH ẢNH BAN ĐẦU ---
        self.frame_index = 0
        self.animation_speed = 0.15
        
        if self.frames:
            self.image = self.frames[0]
        else:
            # Tạo khối đỏ nếu lỗi toàn bộ
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0))
            self.frames = [self.image]
            self.idle_frames = [self.image]

        self.rect = self.image.get_rect()
        self.rect.x = screen_width
        self.rect.bottom = ground_y

    # --- HÀM HELPER: TÁCH LOGIC CẮT ẢNH RA RIÊNG ---
    def load_animation(self, img_name):
        animation_list = []
        full_path = os.path.join(IMG_DIR, self.type, img_name)
        
        if os.path.exists(full_path):
            try:
                sheet = pygame.image.load(full_path).convert_alpha()
                sheet_w = sheet.get_width()
                num_frames = sheet_w // self.frame_w
                
                for i in range(num_frames):
                    # Cắt frame
                    frame = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (i * self.frame_w, 0, self.frame_w, self.frame_h))
                    
                    # Scale (Phóng to/nhỏ)
                    new_w = int(self.frame_w * self.scale)
                    new_h = int(self.frame_h * self.scale)
                    scaled_frame = pygame.transform.scale(frame, (new_w, new_h))
                    
                    animation_list.append(scaled_frame)
                
                return animation_list # Trả về list ảnh đã xử lý
                
            except Exception as e:
                print(f"Lỗi load {img_name}: {e}")
                return []
        else:
            # print(f"Không thấy file: {full_path}") # Bỏ comment nếu muốn debug
            return []

    def update(self):
        # LOGIC DI CHUYỂN
        if self.state == "RUN":
            self.rect.x -= self.speed
            self.distance_moved += self.speed
            self.animate(self.frames) # Truyền list RUN vào
            
            if self.distance_moved >= self.max_distance:
                self.state = "IDLE"
                self.frame_index = 0 
        
        elif self.state == "IDLE":
            self.animate(self.idle_frames) # Truyền list IDLE vào

    # --- HÀM ANIMATE ĐƯỢC CẢI TIẾN ---
    def animate(self, frame_list):
        if len(frame_list) > 1:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frame_list):
                self.frame_index = 0
            self.image = frame_list[int(self.frame_index)]
        elif len(frame_list) == 1:
            self.image = frame_list[0]
            
    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
class MonsterSpawner:
    def __init__(self, screen_width, screen_height, ground_y):
        self.width = screen_width
        self.height = screen_height
        self.ground_y = ground_y
        
        self.monsters = [] 
        
        # --- BIẾN KIỂM SOÁT SPAWN ---
        self.waiting_for_spawn = False  # Đang đợi spawn hay không?
        self.last_death_time = 0        # Thời điểm quái chết/biến mất
        self.spawn_cooldown = 5000      # 5000 ms = 5 giây

    def update(self, screen):
        # 1. LOGIC SINH QUÁI THÔNG MINH
        current_time = pygame.time.get_ticks()

        # Nếu không còn quái trên sân
        if len(self.monsters) == 0:
            if not self.waiting_for_spawn:
                # Bắt đầu tính giờ (vừa mới hết quái)
                self.last_death_time = current_time
                self.waiting_for_spawn = True
                # print("Đã hết quái! Đợi 5s...")
            
            else:
                # Đang đợi, kiểm tra xem đủ 5s chưa
                if current_time - self.last_death_time >= self.spawn_cooldown:
                    self.spawn()
                    self.waiting_for_spawn = False
                    # print("Quái mới xuất hiện!")

        # 2. UPDATE VÀ VẼ QUÁI
        # Duyệt copy list [:] để có thể remove an toàn
        for monster in self.monsters[:]: 
            monster.update() 
            monster.draw(screen)
            
            # Xóa nếu ra khỏi màn hình (hoặc logic chết của bạn)
            if monster.rect.right < 0: 
                self.monsters.remove(monster)

    def spawn(self):
        # Chọn ngẫu nhiên loại quái
        m_type = random.choice(["Microwave", "Frogger"])
        
        # Tạo quái mới (Class Monster phải nằm cùng file này hoặc đã import)
        new_monster = Monster(m_type, self.width, self.ground_y)
        self.monsters.append(new_monster)