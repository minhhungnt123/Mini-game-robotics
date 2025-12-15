import pygame

WHITE = (255, 255, 255)

class QuizManager:
    def __init__(self, screen_width, screen_height):
        self.sw = screen_width
        self.sh = screen_height

        # ===== FONT =====
        try:
            self.font_q = pygame.font.Font("Font/Mitr/Mitr-Medium.ttf", 26)
            self.font_a = pygame.font.Font("Font/Mitr/Mitr-Medium.ttf", 18)
        except:
            self.font_q = pygame.font.SysFont("Arial", 26, bold=True)
            self.font_a = pygame.font.SysFont("Arial", 18, bold=True)

        # ===== BOARD =====
        raw = pygame.image.load("Images/Board/board.png").convert_alpha()
        bw = int(self.sw * 0.8)
        bh = int(bw * raw.get_height() / raw.get_width())
        self.board_img = pygame.transform.smoothscale(raw, (bw, bh))
        self.board_rect = self.board_img.get_rect(center=(self.sw // 2, self.sh // 2))

        # ===== BUTTON =====
        self.buttons = []
        labels = ["A", "B", "C", "D"]

        temp = pygame.image.load("Images/Board/A_base.png").convert_alpha()
        btn_w = int(self.board_rect.width * 0.3)
        btn_h = int(btn_w * temp.get_height() / temp.get_width())

        bx = self.board_rect.left
        by = self.board_rect.top
        bw = self.board_rect.width
        bh = self.board_rect.height

        positions = [
            (bx + int(bw * 0.18), by + int(bh * 0.48)),
            (bx + int(bw * 0.52), by + int(bh * 0.48)),
            (bx + int(bw * 0.18), by + int(bh * 0.68)),
            (bx + int(bw * 0.52), by + int(bh * 0.68)),
        ]

        for i, label in enumerate(labels):
            imgs = {}
            for state in ["base", "hover", "pressed", "correct", "wrong"]:
                img = pygame.image.load(f"Images/Board/{label}_{state}.png").convert_alpha()
                imgs[state] = pygame.transform.smoothscale(img, (btn_w, btn_h))

            rect = imgs["base"].get_rect(topleft=positions[i])

            self.buttons.append({
                "imgs": imgs,
                "rect": rect,
                "hover": False,
                "pressed": False,
                "state": "base"
            })

        self.is_active = False
        self.question = None

        # result timing
        self.result_time = None
        self.result_delay = 500
        self.result_value = None

        # fade
        self.fade_alpha = 0
        self.fading = False

    # =====================================================
    def start_quiz(self, data):
        self.question = data
        self.is_active = True

        self.result_time = None
        self.result_value = None
        self.fade_alpha = 0
        self.fading = False

        for b in self.buttons:
            b["state"] = "base"
            b["hover"] = False
            b["pressed"] = False

    # =====================================================
    def _wrap_2_lines(self, text, font, max_w):
        words = text.split()
        lines, cur = [], ""

        for w in words:
            test = cur + w + " "
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                lines.append(cur)
                cur = w + " "
                if len(lines) == 2:
                    break

        if len(lines) < 2:
            lines.append(cur)

        while font.size(lines[-1] + "...")[0] > max_w and len(lines[-1]) > 0:
            lines[-1] = lines[-1][:-1]

        if lines[-1].strip() != cur.strip():
            lines[-1] = lines[-1].strip() + "..."

        return lines[:2]

    # =====================================================
    def handle_input(self, event):
        if not self.is_active or self.fading:
            return None

        mouse = pygame.mouse.get_pos()

        # chỉ cho 1 hover
        hovered = None
        for b in self.buttons:
            b["hover"] = False
            if b["rect"].collidepoint(mouse) and hovered is None:
                b["hover"] = True
                hovered = b

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.buttons:
                b["pressed"] = False
            if hovered:
                hovered["pressed"] = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for i, b in enumerate(self.buttons):
                if b["pressed"] and b["hover"] and self.result_time is None:
                    correct = i == self.question["correct_index"]

                    b["state"] = "correct" if correct else "wrong"
                    if not correct:
                        self.buttons[self.question["correct_index"]]["state"] = "correct"

                    self.result_time = pygame.time.get_ticks()
                    self.result_value = correct

            for b in self.buttons:
                b["pressed"] = False

        return None

    # =====================================================
    def update(self):
        if not self.is_active:
            return None

        now = pygame.time.get_ticks()

        if self.result_time and not self.fading:
            if now - self.result_time >= self.result_delay:
                self.fading = True

        if self.fading:
            self.fade_alpha += 12
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.is_active = False
                self.fading = False
                return self.result_value

        return None

    # =====================================================
    def draw(self, screen):
        if not self.is_active:
            return

        dark = pygame.Surface((self.sw, self.sh))
        dark.set_alpha(180)
        dark.fill((0, 0, 0))
        screen.blit(dark, (0, 0))

        screen.blit(self.board_img, self.board_rect)

        # question
        max_w = int(self.board_rect.width * 0.75)
        q_lines = self._wrap_2_lines(self.question["question"], self.font_q, max_w)
        y = self.board_rect.top + int(self.board_rect.height * 0.33)

        for l in q_lines:
            surf = self.font_q.render(l, True, WHITE)
            rect = surf.get_rect(center=(self.sw // 2, y))
            screen.blit(surf, rect)
            y += 32

        # buttons
        for i, b in enumerate(self.buttons):
            img = b["imgs"]["base"]
            if b["state"] in ("correct", "wrong"):
                img = b["imgs"][b["state"]]
            elif b["pressed"]:
                img = b["imgs"]["pressed"]
            elif b["hover"]:
                img = b["imgs"]["hover"]

            screen.blit(img, b["rect"])

            if i < len(self.question["options"]):
                padding = int(b["rect"].width * 0.42)
                avail = b["rect"].width - padding - 20
                lines = self._wrap_2_lines(self.question["options"][i], self.font_a, avail)

                ty = b["rect"].centery - (len(lines) * 18) // 2
                for line in lines:
                    surf = self.font_a.render(line, True, WHITE)
                    screen.blit(surf, (b["rect"].left + padding, ty))
                    ty += 18

        if self.fading:
            fade = pygame.Surface((self.sw, self.sh))
            fade.set_alpha(self.fade_alpha)
            fade.fill((0, 0, 0))
            screen.blit(fade, (0, 0))
