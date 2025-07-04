import pygame
import random

pygame.init()

# 색상
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)
]

SHAPES = [
    [[1, 1, 1, 1]], [[1, 0, 0], [1, 1, 1]], [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]], [[0, 1, 1], [1, 1, 0]], [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]]
]

class Piece:
    def __init__(self, x, y, shape, color):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)

class TetrisGame:
    def __init__(self, fullscreen=False):
        display_info = pygame.display.Info()
        self.fullscreen = fullscreen
        if fullscreen:
            self.width, self.height = display_info.current_w, display_info.current_h
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            self.width, self.height = 384, 704
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

        pygame.display.set_caption("테트리스 (최종 버전)")
        self.clock = pygame.time.Clock()

        self.set_board_size()
        self.reset()

        # 키 반복 제어용 변수
        self.last_key = None
        self.last_move_time = 0
        self.key_repeat_delay = 120  # ms

    def set_board_size(self):
        min_columns = 10
        approx_block_size = 50
        self.columns = max(self.width // approx_block_size, min_columns)
        self.block_size = self.width // self.columns
        self.rows = self.height // self.block_size

    def reset(self):
        self.board = [[BLACK for _ in range(self.columns)] for _ in range(self.rows)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.fall_time = 0
        self.fall_speed = 0.5
        self.running = True
        self.score = 0
        self.game_over = False
        self.game_over_timer = 0
        self.game_over_visible = True

    def new_piece(self):
        idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[idx]
        color = COLORS[idx]
        rotations = self.get_rotations(shape)
        start_x = self.columns // 2 - len(rotations[0][0]) // 2
        return Piece(start_x, 0, rotations, color)

    def get_rotations(self, shape):
        rotations = []
        current = shape
        for _ in range(4):
            current = [list(row) for row in current]
            rotations.append(current)
            current = list(zip(*current[::-1]))
        return rotations

    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000  # 초 단위
            self.screen.fill(BLACK)
            self.handle_events()
            if not self.game_over:
                self.update(delta_time)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE and not self.fullscreen:
                self.width, self.height = event.w, event.h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.set_board_size()
                self.reset()
            elif event.type == pygame.KEYDOWN:
                if not self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.hard_drop()  # ✅ 스페이스바로 즉시 바닥까지
                    if event.key == pygame.K_UP:
                        self.rotate()
                    elif event.key == pygame.K_ESCAPE:
                        self.toggle_fullscreen()
                else:
                    if event.key == pygame.K_r:
                        self.reset()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        display_info = pygame.display.Info()
        if self.fullscreen:
            self.width, self.height = display_info.current_w, display_info.current_h
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        else:
            self.width, self.height = 384, 704
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.set_board_size()
        self.reset()

    def move(self, dx):
        new_x = self.current_piece.x + dx
        shape_width = len(self.current_piece.image()[0])
        if 0 <= new_x <= self.columns - shape_width:
            self.current_piece.x = new_x
            if not self.valid_move():
                self.current_piece.x -= dx

    def rotate(self):
        self.current_piece.rotate()
        if not self.valid_move():
            self.current_piece.rotation = (self.current_piece.rotation - 1) % len(self.current_piece.shape)

    def drop(self):
        self.current_piece.y += 1
        if not self.valid_move():
            self.current_piece.y -= 1
            self.lock_piece()
            self.score += 1  # 테트리스 조각이 고정될 때 점수 1점 추가
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
        if not self.valid_move():
            self.game_over = True

    def hard_drop(self):
     while True:
        self.current_piece.y += 1
        if not self.valid_move():
            self.current_piece.y -= 1
            self.lock_piece()
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            if not self.valid_move():
                self.game_over = True
            break
    def update(self, delta_time):
        self.fall_time += delta_time
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            if self.last_key != "left" or current_time - self.last_move_time > self.key_repeat_delay:
                self.move(-1)
                self.last_key = "left"
                self.last_move_time = current_time
        elif keys[pygame.K_RIGHT]:
            if self.last_key != "right" or current_time - self.last_move_time > self.key_repeat_delay:
                self.move(1)
                self.last_key = "right"
                self.last_move_time = current_time
        elif keys[pygame.K_DOWN]:
            if self.last_key != "down" or current_time - self.last_move_time > self.key_repeat_delay:
                self.drop()
                self.last_key = "down"
                self.last_move_time = current_time
                self.fall_time = 0
        else:
            self.last_key = None

        if self.fall_time >= self.fall_speed:
            self.fall_time = 0
            self.drop()

    def valid_move(self):
        shape = self.current_piece.image()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    x = self.current_piece.x + j
                    y = self.current_piece.y + i
                    if x < 0 or x >= self.columns or y >= self.rows:
                        return False
                    if y >= 0 and self.board[y][x] != BLACK:
                        return False
        return True

    def lock_piece(self):
        shape = self.current_piece.image()
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    x = self.current_piece.x + j
                    y = self.current_piece.y + i
                    if y >= 0:
                        self.board[y][x] = self.current_piece.color
        self.clear_lines()

    def clear_lines(self):
        new_board = []
        lines_cleared = 0
        for row in self.board:
            if BLACK not in row:
                lines_cleared += 1
            else:
                new_board.append(row)
        for _ in range(lines_cleared):
            new_board.insert(0, [BLACK for _ in range(self.columns)])
        self.board = new_board
        self.score += lines_cleared * 100

    def draw(self):
        for y in range(self.rows):
            for x in range(self.columns):
                pygame.draw.rect(self.screen, self.board[y][x],
                                 (x * self.block_size, y * self.block_size, self.block_size, self.block_size), 0)

        if not self.game_over:
            shape = self.current_piece.image()
            for i, row in enumerate(shape):
                for j, cell in enumerate(row):
                    if cell:
                        x = self.current_piece.x + j
                        y = self.current_piece.y + i
                        pygame.draw.rect(self.screen, self.current_piece.color,
                                         (x * self.block_size, y * self.block_size,
                                          self.block_size, self.block_size), 0)

        font = pygame.font.SysFont("arial", 24)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            self.game_over_timer += self.clock.get_time()
            if self.game_over_timer >= 500:
                self.game_over_timer = 0
                self.game_over_visible = not self.game_over_visible
            if self.game_over_visible:
                large_font = pygame.font.SysFont("arial", 72, bold=True)
                text_surface = large_font.render("GAME OVER", True, (255, 0, 0))
                text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
                self.screen.blit(text_surface, text_rect)

                small_font = pygame.font.SysFont("arial", 24)
                restart_text = small_font.render("Press R to Restart", True, WHITE)
                restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
                self.screen.blit(restart_text, restart_rect)

if __name__ == "__main__":
    game = TetrisGame(fullscreen=False)
    game.run()
