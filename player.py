import pygame
import os

# --- LOGIC ĐƯỜNG DẪN TỰ ĐỘNG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "Images", "Player")

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.scale_factor = 4.5
        self.state = "WALK" 
        
        self.player_data = {
            "IDLE":   {"img": "Idle.png",   "w": 112, "h": 90}, 
            "WALK":   {"img": "Walk.png",   "w": 112, "h": 90}, 
            "ATTACK": {"img": "Attack.png", "w": 112, "h": 90}, 
            "HIT":    {"img": "Hit.png",    "w": 112, "h": 90},
            "DEATH":  {"img": "Death.png",  "w": 112, "h": 90},
            "PARRY":  {"img": "Parry.png",  "w": 112, "h": 90},
        }
        
        self.animations = {}
        for action, data in self.player_data.items():
            self.animations[action] = self.load_animation(data["img"], data["w"], data["h"])

        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.animations["WALK"][0]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        
        if self.animations["IDLE"]:
            self.image = self.animations["IDLE"][0]

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.animation_finished = False # Cờ báo hiệu animation đã xong chưa

    def load_animation(self, img_name, frame_w, frame_h):
        animation_list = []
        full_path = os.path.join(IMG_DIR, img_name)
        if os.path.exists(full_path):
            try:
                sheet = pygame.image.load(full_path).convert_alpha()
                sheet_w = sheet.get_width()
                num_frames = sheet_w // frame_w if frame_w > 0 else 1
                for i in range(num_frames):
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    new_w = int(frame_w * self.scale_factor)
                    new_h = int(frame_h * self.scale_factor)
                    animation_list.append(pygame.transform.scale(frame, (new_w, new_h)))
                return animation_list
            except Exception:
                return []
        return []

    def update(self):
        # Xác định animation nào cần Loop (lặp lại), animation nào chỉ chạy 1 lần
        loop = True
        if self.state in ["ATTACK", "HIT", "DEATH"]:
            loop = False
        
        if self.state in self.animations:
            self.animate(self.animations[self.state], loop)
        else:
            self.animate(self.animations["IDLE"], True)

    def animate(self, frame_list, loop=True):
        if not frame_list: return
        
        self.frame_index += self.animation_speed
        
        if self.frame_index >= len(frame_list):
            if loop:
                self.frame_index = 0
                self.animation_finished = False
            else:
                self.frame_index = len(frame_list) - 1
                self.animation_finished = True # Đánh dấu đã chạy xong
        else:
            self.animation_finished = False

        old_bottom = self.rect.midbottom
        self.image = frame_list[int(self.frame_index)]
        self.rect = self.image.get_rect()
        self.rect.midbottom = old_bottom

    def set_action(self, new_action):
        if self.state != new_action:
            self.state = new_action
            self.frame_index = 0
            self.animation_finished = False