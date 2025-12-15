import pygame

class Map:
    def __init__(self):
        self.image = pygame.image.load("Images/Map/ground.png").convert_alpha()
        self.ground_scroll = 0
        self.scroll_speed = 4 
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    # Thêm tham số is_moving
    def draw(self, screen, is_moving=True, offset_y=0):
        if is_moving:
            self.ground_scroll -= self.scroll_speed
            if abs(self.ground_scroll) > self.width: # Reset khi trôi hết 1 ảnh
                self.ground_scroll = 0
        
        # Logic vẽ nối tiếp
        # Cộng thêm offset_y vào vị trí Y
        y_pos = (screen.get_height() - self.height) + offset_y
        
        current_x = self.ground_scroll
        while current_x < screen.get_width():
            screen.blit(self.image, (current_x, y_pos))
            current_x += self.width