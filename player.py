import pygame
import os

# --- LOGIC ĐƯỜNG DẪN TỰ ĐỘNG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "Images", "Player")

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.scale_factor = 4.5
        self.state = "WALK" # Trạng thái hiện tại: IDLE, WALK, ATTACK, HIT, DEATH...
        
        # 1. CẤU HÌNH KÍCH THƯỚC CHO TỪNG HÀNH ĐỘNG
        self.player_data = {
            "IDLE":   {"img": "Idle.png",   "w": 112, "h": 90}, 
            "WALK":   {"img": "Walk.png",   "w": 112, "h": 90}, 
            "ATTACK": {"img": "Attack.png", "w": 112, "h": 90}, 
            "HIT":    {"img": "Hit.png",    "w": 112, "h": 90},
            "DEATH":  {"img": "Death.png",  "w": 112, "h": 90},
            "PARRY":  {"img": "Parry.png",  "w": 112, "h": 90},
        }
        
        # 2. LOAD TOÀN BỘ ẢNH VÀO TỪ ĐIỂN
        self.animations = {}
        for action, data in self.player_data.items():
            self.animations[action] = self.load_animation(data["img"], data["w"], data["h"])

        # 3. THIẾT LẬP BAN ĐẦU
        self.frame_index = 0
        self.animation_speed = 0.2 # Tốc độ chuyển frame (nhỏ = chậm, lớn = nhanh)
        self.image = self.animations["WALK"][0] # Mặc định lấy ảnh chạy
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
        # Gán ảnh mặc định để tránh lỗi
        if self.animations["IDLE"]:
            self.image = self.animations["IDLE"][0]
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill((0, 255, 0)) # Xanh lá báo lỗi

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
        # Các biến vật lý (giữ nguyên logic cũ)
        self.vel = 0
        self.clicked = False

    def load_animation(self, img_name, frame_w, frame_h):
        animation_list = []
        full_path = os.path.join(IMG_DIR, img_name)
        
        if os.path.exists(full_path):
            try:
                sheet = pygame.image.load(full_path).convert_alpha()
                sheet_w = sheet.get_width()
                
                # Tính số lượng frame
                if frame_w > 0:
                    num_frames = sheet_w // frame_w
                else:
                    num_frames = 1
                
                for i in range(num_frames):
                    # Cắt từng frame
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    
                    # Phóng to (Scale)
                    new_w = int(frame_w * self.scale_factor)
                    new_h = int(frame_h * self.scale_factor)
                    scaled_frame = pygame.transform.scale(frame, (new_w, new_h))
                    
                    animation_list.append(scaled_frame)
                
                return animation_list
            except Exception as e:
                print(f"Lỗi load {img_name}: {e}")
                return []
        else:
            print(f"Không tìm thấy file: {full_path}")
            return []

    def update(self):
        # Cập nhật animation dựa trên self.state
        if self.state in self.animations:
                self.animate(self.animations[self.state])
        else:
            self.animate(self.animations["IDLE"])

    def animate(self, frame_list):
        if not frame_list: return
        self.frame_index += self.animation_speed
        if self.frame_index >= len(frame_list):
            self.frame_index = 0
        old_bottom = self.rect.midbottom
        
        self.image = frame_list[int(self.frame_index)]
        self.rect = self.image.get_rect()
        self.rect.midbottom = old_bottom

    # --- HÀM HỖ TRỢ ĐỂ MAIN GỌI ---
    def set_action(self, new_action):
        if self.state != new_action:
            self.state = new_action
            self.frame_index = 0