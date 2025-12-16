import pygame
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "Images", "Monster")

class Monster(pygame.sprite.Sprite):
    def __init__(self, monster_type, screen_width, ground_y):
        super().__init__()
        self.type = monster_type
        self.state = "RUN"
        self.animation_speed = 0.15
        self.frame_index = 0
        self.monster_data = {}
        self.animation_finished = False
        
        # Cấu hình dữ liệu quái vật
        if monster_type == "Microwave":
            self.scale = 3
            self.speed = 3
            self.monster_data = {
                "RUN":    {"img": "Walk.png",   "w": 80, "h": 80},
                "IDLE":   {"img": "Idle.png",   "w": 80, "h": 80},
                "ATTACK": {"img": "Attack.png", "w": 80, "h": 80},
                "DEATH":  {"img": "Death.png",  "w": 80, "h": 80},
                "HIT":    {"img": "Hit.png",    "w": 80, "h": 80}
            }
            
        elif monster_type == "Frogger":
            self.scale = 2
            self.speed = 4
            self.monster_data = {
                "RUN":    {"img": "frogger_move.png", "w": 384, "h": 128}, 
                "IDLE":   {"img": "frogger_idle.png", "w": 128, "h": 128},
                "ATTACK": {"img": "frogger_spit.png", "w": 384, "h": 128},
                "DEATH":  {"img": "frogger_hurt.png", "w": 384, "h": 128}
            }
            
        elif monster_type == "Scout":
            self.scale = 1
            self.speed = 2
            self.monster_data = {
                "RUN":    {"img": "Scout_fly.png",   "w": 336, "h": 288},
                "IDLE":   {"img": "Scout_idle.png",   "w": 336, "h": 288},
                "ATTACK": {"img": "Scout_attack.png", "w": 336, "h": 288},
                "DEATH":  {"img": "Scout_death.png",  "w": 336, "h": 288},
            }

        self.animations = {}
        for action, data in self.monster_data.items():
            frames = self.load_animation(data["img"], data["w"], data["h"])
            self.animations[action] = frames

        # Load hình mặc định
        if "RUN" in self.animations and self.animations["RUN"]:
            self.image = self.animations["RUN"][0]
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0))
            self.animations["RUN"] = [self.image]

        self.rect = self.image.get_rect()
        self.rect.x = screen_width
        self.rect.bottom = ground_y

    def load_animation(self, img_name, frame_w, frame_h):
        animation_list = []
        full_path = os.path.join(IMG_DIR, self.type, img_name)
        if os.path.exists(full_path):
            try:
                sheet = pygame.image.load(full_path).convert_alpha()
                sheet_w = sheet.get_width()
                num_frames = sheet_w // frame_w if frame_w > 0 else 1
                for i in range(num_frames):
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    new_w = int(frame_w * self.scale)
                    new_h = int(frame_h * self.scale)
                    animation_list.append(pygame.transform.scale(frame, (new_w, new_h)))
                return animation_list
            except Exception as e:
                print(f"Error loading {img_name}: {e}")
                return []
        return []

    def update(self, is_moving=True):
        # 1. Logic di chuyển (chỉ khi không đang đánh nhau/chết)
        if is_moving:
            self.rect.x -= self.speed 
            if self.state not in ["ATTACK", "DEATH", "HURT", "HIT"]:
                self.state = "RUN"
        else:
            # Nếu màn hình dừng, chuyển về IDLE trừ khi đang đánh nhau
            if self.state == "RUN":
                self.state = "IDLE"

        # 2. Logic Animation Loop
        # Các hành động này chỉ chạy 1 lần rồi dừng (loop = False)
        loop = True
        if self.state in ["ATTACK", "DEATH", "HURT", "HIT"]:
            loop = False

        # 3. Chạy animation
        if self.state in self.animations:
            self.animate(self.animations[self.state], loop)
        else:
            # Fallback: Nếu Frogger không có DEATH thì dùng HURT
            if self.state == "DEATH" and "HURT" in self.animations:
                 self.animate(self.animations["HURT"], False)

    def animate(self, frame_list, loop=True):
        if not frame_list: return

        if len(frame_list) > 1:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frame_list):
                if loop:
                    self.frame_index = 0
                    self.animation_finished = False
                else:
                    self.frame_index = len(frame_list) - 1
                    self.animation_finished = True
            else:
                self.animation_finished = False
            
            self.image = frame_list[int(self.frame_index)]
            old_bottom = self.rect.bottom
            old_center_x = self.rect.centerx
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.centerx = old_center_x
            
        elif len(frame_list) == 1:
            self.image = frame_list[0]
            self.animation_finished = True

    def set_action(self, new_action):
        if self.state != new_action:
            self.state = new_action
            self.frame_index = 0
            self.animation_finished = False
            
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class MonsterSpawner:
    def __init__(self, screen_width, screen_height, ground_y):
        self.width = screen_width
        self.height = screen_height
        self.ground_y = ground_y
        self.monsters = [] 
        self.waiting_for_spawn = False
        self.last_death_time = 0
        self.spawn_cooldown = 2000 

    def update(self, is_moving=True):
        current_time = pygame.time.get_ticks()
        
        if is_moving:
            if len(self.monsters) == 0:
                if not self.waiting_for_spawn:
                    self.last_death_time = current_time
                    self.waiting_for_spawn = True
                else:
                    if current_time - self.last_death_time >= self.spawn_cooldown:
                        self.spawn()
                        self.waiting_for_spawn = False

        for monster in self.monsters[:]: 
            monster.update(is_moving)
            if monster.rect.right < 0: 
                self.monsters.remove(monster)

    def draw(self, screen):
        for monster in self.monsters:
            monster.draw(screen)

    def spawn(self):
        m_type = random.choice(["Microwave", "Frogger", "Scout"])
        new_monster = Monster(m_type, self.width, self.ground_y)
        self.monsters.append(new_monster)