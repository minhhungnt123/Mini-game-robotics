import pygame
import random
import sys
import os # Thêm thư viện os để xử lý file

# --- CẤU HÌNH GAME ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Màu sắc (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)      # Màu Robot
RED = (200, 50, 50)        # Màu Quái vật
GREEN = (50, 200, 50)      # Màu Đúng/Máu
YELLOW = (255, 215, 0)     # Màu Sao/Điểm
GRAY = (200, 200, 200)
BG_COLOR = (135, 206, 235) # Màu trời

# --- CẤU HÌNH TÊN FILE ẢNH (BẠN HÃY ĐẶT ẢNH CÙNG THƯ MỤC VỚI FILE CODE) ---
ROBOT_IMAGE_PATH = "robot.png"      # Ảnh nhân vật
MONSTER_IMAGE_PATH = "monster.png"  # Ảnh quái vật
BG_IMAGE_PATH = "background.png"    # Ảnh nền (Nên có kích thước 800x600)

# --- DỮ LIỆU CÂU HỎI ROBOTICS (Mẫu) ---
# Cấu trúc: [Câu hỏi, Đáp án A, Đáp án B, Đáp án C, Đáp án D, Vị trí đáp án đúng (0-3)]
QUESTIONS = [
    ["Robot cần gì để hoạt động?", "Bánh kẹo", "Năng lượng (Pin)", "Nước ngọt", "Không khí", 1],
    ["Bộ phận nào giúp Robot 'nhìn'?", "Cảm biến/Camera", "Loa", "Bánh xe", "Cánh tay", 0],
    ["Bộ não của Robot là gì?", "Màn hình", "Dây điện", "Vi xử lý (Mạch)", "Vỏ nhựa", 2],
    ["Robot có biết buồn không?", "Rất buồn", "Có", "Không có cảm xúc", "Hay khóc", 2],
    ["Để Robot di chuyển, ta cần?", "Động cơ/Bánh xe", "Microphone", "Đèn LED", "Nút bấm", 0],
    ["Ai là người lập trình cho Robot?", "Bác sĩ", "Con mèo", "Lập trình viên", "Ca sĩ", 2],
    ["Robot hút bụi dùng để làm gì?", "Nấu cơm", "Dọn dẹp nhà", "Hát karaoke", "Trồng cây", 1],
]

# --- KHỞI TẠO PYGAME ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Robo-Hero: Giải Đố Robotics")
clock = pygame.time.Clock()

# Font chữ (Cố gắng dùng font hỗ trợ tiếng Việt cơ bản)
try:
    font_large = pygame.font.SysFont("Arial", 40, bold=True)
    font_med = pygame.font.SysFont("Arial", 28)
    font_small = pygame.font.SysFont("Arial", 20)
except:
    font_large = pygame.font.Font(None, 40)
    font_med = pygame.font.Font(None, 28)
    font_small = pygame.font.Font(None, 20)

# --- HÀM HỖ TRỢ LOAD ẢNH ---
def load_asset_image(path, width, height, fallback_color):
    try:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (width, height))
        return image, True # Trả về ảnh và trạng thái "Load thành công"
    except (pygame.error, FileNotFoundError):
        # Nếu lỗi (không thấy file), tạo hình khối mặc định
        image = pygame.Surface((width, height))
        image.fill(fallback_color)
        return image, False # Trả về hình khối và trạng thái "Dùng mặc định"

# --- CÁC CLASS (LỚP ĐỐI TƯỢNG) ---

class Robot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # --- CHỈNH SỬA Ở ĐÂY: LOAD ẢNH ROBOT ---
        # Thử load ảnh 'robot.png'. Nếu không có, dùng hình vẽ mặc định
        self.image, loaded = load_asset_image(ROBOT_IMAGE_PATH, 50, 50, BLUE)
        
        if not loaded:
            # Nếu không có ảnh, vẽ chi tiết mắt mũi cho hình khối mặc định
            pygame.draw.circle(self.image, WHITE, (35, 15), 8) 
            pygame.draw.circle(self.image, BLACK, (35, 15), 3)
        
        self.rect = self.image.get_rect()
        self.rect.center = (150, SCREEN_HEIGHT // 2)
        
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8
        self.hp = 3 # Máu của người chơi

    def update(self, is_paused):
        if not is_paused:
            # Áp dụng trọng lực
            self.velocity += self.gravity
            self.rect.y += int(self.velocity)

            # Giới hạn không cho rơi khỏi màn hình hoặc bay quá cao
            if self.rect.bottom > SCREEN_HEIGHT - 20:
                self.rect.bottom = SCREEN_HEIGHT - 20
                self.velocity = 0
            if self.rect.top < 0:
                self.rect.top = 0
                self.velocity = 0

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        # Vẽ thanh máu trên đầu
        width = 50 * (self.hp / 3)
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 15, 50, 8))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 15, width, 8))

class Monster(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # --- CHỈNH SỬA Ở ĐÂY: LOAD ẢNH QUÁI VẬT ---
        # Thử load ảnh 'monster.png'. Nếu không có, dùng hình vẽ mặc định
        self.image, loaded = load_asset_image(MONSTER_IMAGE_PATH, 60, 60, RED)
        
        if not loaded:
            # Nếu không có ảnh, vẽ mắt mũi cho hình khối mặc định
            pygame.draw.circle(self.image, YELLOW, (20, 20), 5)
            pygame.draw.circle(self.image, YELLOW, (40, 20), 5)
            pygame.draw.line(self.image, BLACK, (10, 45), (50, 45), 3)

        self.rect = self.image.get_rect()
        # Xuất hiện ngẫu nhiên bên phải màn hình
        self.rect.x = SCREEN_WIDTH + 100
        self.rect.y = random.randint(50, SCREEN_HEIGHT - 150)
        self.speed = 4

    def update(self, is_paused):
        if not is_paused:
            self.rect.x -= self.speed

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = (color[0] + 30 if color[0] < 225 else 255, 
                            color[1] + 30 if color[1] < 225 else 255, 
                            color[2] + 30 if color[2] < 225 else 255)
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        text_surf = font_med.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# --- HÀM HỖ TRỢ ---
def draw_text(surface, text, font, color, x, y, center=False):
    text_obj = font.render(text, True, color)
    rect = text_obj.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(text_obj, rect)

# --- HÀM CHÍNH CỦA GAME ---
def main():
    running = True
    game_state = "MENU" # MENU, PLAYING, BATTLE, GAMEOVER
    
    # Đối tượng game
    player = Robot()
    monsters = pygame.sprite.Group()
    
    # Biến quản lý trạng thái
    score = 0
    bg_scroll = 0
    bg_speed = 3
    ground_height = 20
    
    # Quản lý câu hỏi
    current_question = None
    answer_buttons = []
    feedback_timer = 0
    feedback_text = ""
    
    # Timer sinh quái vật
    SPAWN_MONSTER_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_MONSTER_EVENT, 4000) # 4 giây ra 1 con

    # --- CHỈNH SỬA Ở ĐÂY: LOAD ẢNH NỀN ---
    # Thử load hình nền
    bg_image = None
    try:
        bg_image = pygame.image.load(BG_IMAGE_PATH).convert()
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        bg_image = None # Nếu không có ảnh, sẽ dùng màu tô

    while running:
        # 1. XỬ LÝ SỰ KIỆN
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if game_state == "MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Reset game
                        player = Robot()
                        monsters.empty()
                        score = 0
                        game_state = "PLAYING"
            
            elif game_state == "PLAYING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                
                if event.type == SPAWN_MONSTER_EVENT:
                    monsters.add(Monster())

            elif game_state == "BATTLE":
                if event.type == pygame.MOUSEBUTTONDOWN and feedback_timer == 0:
                    for idx, btn in enumerate(answer_buttons):
                        if btn.is_clicked(mouse_pos):
                            correct_idx = current_question[5]
                            if idx == correct_idx:
                                # Trả lời đúng
                                feedback_text = "CHÍNH XÁC! TẤN CÔNG!"
                                score += 10
                                monsters.remove(current_monster) # Diệt quái
                            else:
                                # Trả lời sai
                                feedback_text = "SAI RỒI! BỊ TẤN CÔNG!"
                                player.hp -= 1
                                monsters.remove(current_monster) # Quái bỏ đi sau khi đánh
                            
                            feedback_timer = 60 # Hiện thông báo trong 1 giây (60 frames)

            elif game_state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                         game_state = "MENU"

        # 2. CẬP NHẬT LOGIC
        if game_state == "PLAYING":
            # Cuộn nền
            bg_scroll -= bg_speed
            if bg_scroll <= -SCREEN_WIDTH:
                bg_scroll = 0
            
            player.update(is_paused=False)
            monsters.update(is_paused=False)
            
            # Xóa quái ra khỏi màn hình
            for m in monsters:
                if m.rect.right < 0:
                    monsters.remove(m)
            
            # Kiểm tra va chạm (Gặp quái)
            collision_list = pygame.sprite.spritecollide(player, monsters, False)
            if collision_list:
                current_monster = collision_list[0]
                game_state = "BATTLE"
                
                # Lấy ngẫu nhiên câu hỏi
                q_data = random.choice(QUESTIONS)
                current_question = q_data
                
                # Tạo nút bấm
                answer_buttons = []
                # Vị trí nút
                start_y = 250
                for i in range(4):
                    btn = Button(150, start_y + i*70, 500, 60, f"{chr(65+i)}. {q_data[i+1]}", WHITE)
                    answer_buttons.append(btn)

        elif game_state == "BATTLE":
            # Trong lúc Battle, game tạm dừng (không update player/monster movement)
            # Chỉ xử lý feedback text
            if feedback_timer > 0:
                feedback_timer -= 1
                if feedback_timer == 0:
                    # Hết thời gian feedback, quay lại chơi
                    game_state = "PLAYING"
                    if player.hp <= 0:
                        game_state = "GAMEOVER"

        # 3. VẼ (RENDER)
        screen.fill(BG_COLOR)
        
        # Vẽ nền cuộn
        if bg_image:
            # Nếu có ảnh nền, vẽ ảnh nối tiếp nhau để tạo hiệu ứng cuộn
            screen.blit(bg_image, (bg_scroll, 0))
            screen.blit(bg_image, (bg_scroll + SCREEN_WIDTH, 0))
        else:
            # Nếu không có ảnh nền, vẽ đất như cũ
            pygame.draw.rect(screen, (34, 139, 34), (bg_scroll, SCREEN_HEIGHT - ground_height, SCREEN_WIDTH, ground_height))
            pygame.draw.rect(screen, (34, 139, 34), (bg_scroll + SCREEN_WIDTH, SCREEN_HEIGHT - ground_height, SCREEN_WIDTH, ground_height))
        
        # Vẽ đối tượng
        monsters.draw(screen)
        player.draw(screen)
        
        # UI HUD
        draw_text(screen, f"Điểm: {score}", font_med, BLACK, 20, 20)
        
        # Vẽ các trạng thái đặc biệt
        if game_state == "MENU":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(WHITE)
            screen.blit(overlay, (0,0))
            
            draw_text(screen, "ROBO-HERO", font_large, BLUE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50, center=True)
            draw_text(screen, "Nhấn SPACE để bắt đầu", font_med, BLACK, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20, center=True)
            draw_text(screen, "Space: Nhảy | Trả lời đúng để diệt quái", font_small, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, center=True)

        elif game_state == "BATTLE":
            # Làm tối màn hình
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0,0))
            
            if feedback_timer > 0:
                # Hiện kết quả
                color = GREEN if "CHÍNH XÁC" in feedback_text else RED
                draw_text(screen, feedback_text, font_large, color, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center=True)
            else:
                # Hiện câu hỏi
                # Vẽ khung câu hỏi
                pygame.draw.rect(screen, BLUE, (50, 50, SCREEN_WIDTH-100, 150), border_radius=15)
                pygame.draw.rect(screen, WHITE, (50, 50, SCREEN_WIDTH-100, 150), 3, border_radius=15)
                
                # In câu hỏi (xử lý xuống dòng đơn giản nếu cần, ở đây viết ngắn gọn)
                draw_text(screen, "CÂU HỎI:", font_small, YELLOW, 70, 70)
                draw_text(screen, current_question[0], font_med, WHITE, SCREEN_WIDTH//2, 125, center=True)
                
                # Vẽ nút
                for btn in answer_buttons:
                    btn.check_hover(mouse_pos)
                    btn.draw(screen)

        elif game_state == "GAMEOVER":
            draw_text(screen, "GAME OVER", font_large, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20, center=True)
            draw_text(screen, f"Tổng điểm: {score}", font_med, BLACK, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30, center=True)
            draw_text(screen, "Nhấn SPACE để chơi lại", font_small, BLACK, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70, center=True)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()