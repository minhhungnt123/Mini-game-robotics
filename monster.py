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
        self.distance_moved = 0
        self.max_distance = 400
        self.animation_speed = 0.15
        self.frame_index = 0
        self.monster_data = {}
        
        if monster_type == "Microwave":
            self.scale = 3
            self.speed = 3
            self.monster_data = {
                "RUN":  {"img": "Walk.png", "w": 80, "h": 80},
                "IDLE": {"img": "Idle.png", "w": 80, "h": 80},
            }
            
        elif monster_type == "Frogger":
            self.scale = 2
            self.speed = 4
            self.monster_data = {
                "RUN":    {"img": "frogger_move.png", "w": 384, "h": 128}, 
                "IDLE":   {"img": "frogger_idle.png", "w": 128, "h": 128},
                "ATTACK": {"img": "frogger_spit.png", "w": 80, "h": 48},
                "HURT":   {"img": "frogger_hurt.png", "w": 48, "h": 48}
            }
            
        elif monster_type == "Scout":
            self.scale = 2.5
            self.speed = 2
            self.monster_data = {
                "RUN":  {"img": "Scout_fly.png", "w": 672, "h": 574},
                "IDLE": {"img": "Scout_idle.png", "w": 672, "h": 574},
            }

        self.animations = {}
        
        for action, data in self.monster_data.items():
            frames = self.load_animation(data["img"], data["w"], data["h"])
            self.animations[action] = frames

        if "RUN" in self.animations and self.animations["RUN"]:
            self.image = self.animations["RUN"][0]
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0))
            self.animations["RUN"] = [self.image]
            self.animations["IDLE"] = [self.image]

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
                
                if frame_w > 0:
                    num_frames = sheet_w // frame_w
                else:
                    num_frames = 1 
                
                for i in range(num_frames):
                    frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                    frame.blit(sheet, (0, 0), (i * frame_w, 0, frame_w, frame_h))
                    
                    new_w = int(frame_w * self.scale)
                    new_h = int(frame_h * self.scale)
                    scaled_frame = pygame.transform.scale(frame, (new_w, new_h))
                    
                    animation_list.append(scaled_frame)
                
                return animation_list
            except Exception as e:
                print(f"Lỗi load {img_name}: {e}")
                return []
        else:
            return []

    def update(self, is_moving=True):
        if is_moving:
            self.rect.x -= self.speed 
            self.state = "RUN"
        else:
            self.state = "IDLE"
        if self.state in self.animations:
            self.animate(self.animations[self.state])

    def animate(self, frame_list):
        if not frame_list: return

        if len(frame_list) > 1:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(frame_list):
                self.frame_index = 0
            
            self.image = frame_list[int(self.frame_index)]
            
            old_bottom = self.rect.bottom
            old_center_x = self.rect.centerx
            
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom
            self.rect.centerx = old_center_x
            
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
        self.waiting_for_spawn = False
        self.last_death_time = 0
        self.spawn_cooldown = 5000

    def update(self, screen, is_moving=True):
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
            monster.draw(screen)
            
            if monster.rect.right < 0: 
                self.monsters.remove(monster)

    def spawn(self):
        m_type = random.choice(["Microwave", "Frogger"])
        new_monster = Monster(m_type, self.width, self.ground_y)
        self.monsters.append(new_monster)