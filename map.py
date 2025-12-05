import pygame

class Map:
    def __init__(self):
        self.image = pygame.image.load("Images/Map/ground.png").convert_alpha()
        
        self.ground_scroll = 0
        self.scroll_speed = 4 
        
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self, screen):
        self.ground_scroll -= self.scroll_speed
        if abs(self.ground_scroll) > 2560:
            self.ground_scroll = 0
        y_pos = screen.get_height() - self.height
        current_x = self.ground_scroll
        while current_x < screen.get_width():
            screen.blit(self.image, (current_x, y_pos))
            current_x += self.width