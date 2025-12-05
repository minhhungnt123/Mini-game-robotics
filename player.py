import pygame
import os
class Player(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.scale_factor = 4.5
        
        self.sprite_sheet = pygame.image.load(
            "Images\Player\Idle.png"
            ).convert_alpha()
        
        # kích thước khung hình ban đầu
        self.base_frame_width = 112
        self.base_frame_height = 80
        
        # kích thước khung hình mới sau khi phóng to
        self.frame_width = self.base_frame_width * self.scale_factor
        self.frame_height = self.base_frame_height * self.scale_factor
        
        self.num_frames = 8
        
        self.images = []
        self.index = 0
        self.counter = 0
        self.animation_speed = 5
        
        for i in range(self.num_frames):
            frame = pygame.Surface((self.base_frame_width, self.base_frame_height), pygame.SRCALPHA)
            source_x = i * self.base_frame_width
            source_y = 0
            
            frame.blit(self.sprite_sheet, (0,0),(source_x, source_y, self.base_frame_width, self.base_frame_height))
            
            scaled_frame = pygame.transform.scale(frame, (self.frame_width, self.frame_height))
            
            self.images.append(scaled_frame)
    
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False
        
    def update(self):
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            self.index = (self.index + 1) % self.num_frames
            self.image = self.images[self.index]