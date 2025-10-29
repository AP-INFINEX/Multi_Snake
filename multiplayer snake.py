import pygame
import random
import time

pygame.init()

# ---------------- SETTINGS ---------------- #
BLOCK_SIZE = 20
GRID_WIDTH = 48
GRID_HEIGHT = 28
WIDTH = BLOCK_SIZE * GRID_WIDTH
HEIGHT = BLOCK_SIZE * GRID_HEIGHT
FPS = 60
MOVE_DELAY = 5  # Slightly faster
MOVE_SPEED = 0.2  # More responsive interpolation
FONT = pygame.font.SysFont("consolas", 30)
TITLE_FONT = pygame.font.SysFont("consolas", 50)

# Colors
BLACK = (10, 10, 20)
WHITE = (240, 240, 240)
CYAN = (0, 255, 255)
LIGHT_GREEN = (100, 255, 100)
GOLD = (255, 215, 0)
RED = (255, 50, 50)
STEM = (0, 180, 0)
PINK = (255, 105, 180)  # Brighter pink for eyes
PURPLE = (147, 112, 219)  # For iris
BLACK_PUPIL = (0, 0, 0)  # For pupils

# ---------------- DISPLAY ---------------- #
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multiplayer Snake - Anubhav Edition")
clock = pygame.time.Clock()

# ---------------- CLASSES ---------------- #
class Snake:
    def __init__(self, color, start_pos, controls):
        x = (start_pos[0] // BLOCK_SIZE) * BLOCK_SIZE
        y = (start_pos[1] // BLOCK_SIZE) * BLOCK_SIZE
        self.color = color
        self.body = [(x, y)]
        self.visual_body = [(float(x), float(y))]
        self.direction = (BLOCK_SIZE, 0)
        self.controls = controls
        self.score = 0
        self.wins = 0
        self.move_counter = 0

    def move(self):
        # Smooth visual movement
        for i, (target_x, target_y) in enumerate(self.body):
            vx, vy = self.visual_body[i]
            dx = target_x - vx
            dy = target_y - vy
            
            # Handle screen wrapping for smooth movement
            if abs(dx) > WIDTH / 2:
                if dx > 0:
                    dx -= WIDTH
                else:
                    dx += WIDTH
            if abs(dy) > HEIGHT / 2:
                if dy > 0:
                    dy -= HEIGHT
                else:
                    dy += HEIGHT
            
            # Enhanced smooth interpolation with easing
            ease = 1 - (1 - MOVE_SPEED) * (1 - MOVE_SPEED)  # Quadratic easing
            new_x = vx + dx * ease
            new_y = vy + dy * ease
            
            # Wrap the visual position smoothly
            new_x = new_x % WIDTH
            new_y = new_y % HEIGHT
            
            self.visual_body[i] = (new_x, new_y)
        
        # Grid-based movement
        if self.move_counter >= MOVE_DELAY:
            self.move_counter = 0
            head_x, head_y = self.body[0]
            dx, dy = self.direction
            new_head = ((head_x + dx) % WIDTH, (head_y + dy) % HEIGHT)
            self.body.insert(0, new_head)
            self.visual_body.insert(0, self.visual_body[0])
            self.body.pop()
            self.visual_body.pop()
        self.move_counter += 1

    def draw(self):
        # Draw snake body
        for pos in self.visual_body:
            pygame.draw.rect(screen, self.color, (int(pos[0]), int(pos[1]), BLOCK_SIZE, BLOCK_SIZE))

    def grow(self):
        self.body.append(self.body[-1])
        self.visual_body.append(self.visual_body[-1])
        self.score += 1

    def draw(self):
        for segment in self.body:
            pygame.draw.rect(screen, self.color, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

        # Draw eyes
        head_x, head_y = self.body[0]
        eye_offset = BLOCK_SIZE // 3
        eye_size = BLOCK_SIZE // 5
        dx, dy = self.direction

        if dx > 0:  # moving right
            eyes = [(head_x + BLOCK_SIZE - eye_size - 2, head_y + eye_offset),
                    (head_x + BLOCK_SIZE - eye_size - 2, head_y + BLOCK_SIZE - eye_offset - eye_size)]
        elif dx < 0:  # moving left
            eyes = [(head_x + 2, head_y + eye_offset),
                    (head_x + 2, head_y + BLOCK_SIZE - eye_offset - eye_size)]
        elif dy > 0:  # moving down
            eyes = [(head_x + eye_offset, head_y + BLOCK_SIZE - eye_size - 2),
                    (head_x + BLOCK_SIZE - eye_offset - eye_size, head_y + BLOCK_SIZE - eye_size - 2)]
        else:  # moving up
            eyes = [(head_x + eye_offset, head_y + 2),
                    (head_x + BLOCK_SIZE - eye_offset - eye_size, head_y + 2)]

        for e in eyes:
            # Draw the white of the eye
            pygame.draw.ellipse(screen, PINK, (e[0], e[1], eye_size, eye_size))
            # Draw the pupil (smaller black circle)
            pupil_size = eye_size // 2
            pupil_x = e[0] + (eye_size - pupil_size) // 2
            pupil_y = e[1] + (eye_size - pupil_size) // 2
            pygame.draw.ellipse(screen, BLACK_PUPIL, (pupil_x, pupil_y, pupil_size, pupil_size))

    def handle_input(self, keys):
        for key, dir in self.controls.items():
            if keys[key]:
                if (dir[0] * -1, dir[1] * -1) != self.direction:
                    self.direction = dir


class Apple:
    def __init__(self):
        self.color = RED
        self.pos = self.random_pos()
        self.golden = False
        self.move_timer = 0

    def random_pos(self):
        return (random.randrange(GRID_WIDTH) * BLOCK_SIZE,
                random.randrange(GRID_HEIGHT) * BLOCK_SIZE)

    def move(self):
        self.move_timer += 1
        if self.move_timer >= MOVE_DELAY * 4:
            self.move_timer = 0
            if random.random() < 0.15:
                dx, dy = random.choice([(BLOCK_SIZE, 0), (-BLOCK_SIZE, 0), 
                                      (0, BLOCK_SIZE), (0, -BLOCK_SIZE)])
                self.pos = ((self.pos[0] + dx) % WIDTH,
                          (self.pos[1] + dy) % HEIGHT)

    def draw(self):
        pygame.draw.rect(screen, self.color, (*self.pos, BLOCK_SIZE, BLOCK_SIZE))
        # Stem
        pygame.draw.rect(screen, STEM, (self.pos[0] + BLOCK_SIZE // 2 - 2, self.pos[1] - 5, 4, 5))

    def set_golden(self, golden):
        self.golden = golden
        self.color = GOLD if golden else RED


# ---------------- UI FUNCTIONS ---------------- #
def draw_text_center(text, y, font=FONT, color=WHITE):
    render = font.render(text, True, color)
    screen.blit(render, (WIDTH / 2 - render.get_width() / 2, y))


def input_screen():
    name1, name2 = "", ""
    active = 1
    while True:
        screen.fill(BLACK)
        draw_text_center("ENTER PLAYER NAMES", 100, TITLE_FONT)
        draw_text_center(f"Player 1 (WASD): {name1 or '_'}", 250, FONT, CYAN if active == 1 else WHITE)
        draw_text_center(f"Player 2 (ARROWS): {name2 or '_'}", 320, FONT, LIGHT_GREEN if active == 2 else WHITE)
        draw_text_center("Press ENTER to switch, SPACE to start", 450, FONT)

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    active = 2 if active == 1 else 1
                elif e.key == pygame.K_SPACE and name1 and name2:
                    return name1, name2
                elif e.key == pygame.K_BACKSPACE:
                    if active == 1 and name1: name1 = name1[:-1]
                    elif active == 2 and name2: name2 = name2[:-1]
                elif e.unicode.isalpha() and len(e.unicode) == 1:
                    if active == 1 and len(name1) < 10: name1 += e.unicode.upper()
                    elif active == 2 and len(name2) < 10: name2 += e.unicode.upper()


def end_screen(p1, p2, n1, n2, total_wins):
    winner = n1 if p1.score > p2.score else n2 if p2.score > p1.score else None
    if winner:
        total_wins[winner] += 1
    
    texts = [
        ("GAME OVER", 100, TITLE_FONT, WHITE),
        (f"Winner: {winner}" if winner else "It's a TIE!", 200, FONT, GOLD if winner else WHITE),
        (f"{n1} - Score: {p1.score} | Total Wins: {total_wins[n1]}", 300, FONT, CYAN),
        (f"{n2} - Score: {p2.score} | Total Wins: {total_wins[n2]}", 350, FONT, LIGHT_GREEN),
        ("Press SPACE to play again or ESC to quit", 480, FONT, WHITE)
    ]
    
    screen.fill(BLACK)
    for text, y, font, color in texts:
        draw_text_center(text, y, font, color)
    pygame.display.flip()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE: return True
                if e.key == pygame.K_ESCAPE: return False


# ---------------- COUNTDOWN FUNCTION ---------------- #
def countdown():
    for i in range(3, 0, -1):
        screen.fill(BLACK)
        draw_text_center(str(i), HEIGHT//2, TITLE_FONT)
        pygame.display.flip()
        start_time = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_time < 1000:  # Wait for 1 second
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

# ---------------- MAIN GAME LOOP ---------------- #
def main():
    n1, n2 = input_screen()
    # Initialize total wins
    total_wins = {n1: 0, n2: 0}
    playing = True
    while playing:
        # Countdown
        countdown()
        
        # Init players + apple
        # Ensure starting positions are aligned to grid
        p1_start_x = ((WIDTH // 4) // BLOCK_SIZE) * BLOCK_SIZE
        p1_start_y = (HEIGHT // 2 // BLOCK_SIZE) * BLOCK_SIZE
        p2_start_x = ((3 * WIDTH // 4) // BLOCK_SIZE) * BLOCK_SIZE
        p2_start_y = (HEIGHT // 2 // BLOCK_SIZE) * BLOCK_SIZE
        
        p1 = Snake(CYAN, (p1_start_x, p1_start_y),
                   {pygame.K_a: (-BLOCK_SIZE, 0), pygame.K_d: (BLOCK_SIZE, 0),
                    pygame.K_w: (0, -BLOCK_SIZE), pygame.K_s: (0, BLOCK_SIZE)})

        p2 = Snake(LIGHT_GREEN, (p2_start_x, p2_start_y),
                   {pygame.K_LEFT: (-BLOCK_SIZE, 0), pygame.K_RIGHT: (BLOCK_SIZE, 0),
                    pygame.K_UP: (0, -BLOCK_SIZE), pygame.K_DOWN: (0, BLOCK_SIZE)})

        apple = Apple()
        level_up_timer = 0
        start_time = pygame.time.get_ticks()
        run = True

        while run:
            keys = pygame.key.get_pressed()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); exit()

            p1.handle_input(keys)
            p2.handle_input(keys)
            p1.move()
            p2.move()
            apple.move()

            # Apple collision
            for player in [p1, p2]:
                px, py = player.body[0]
                ax, ay = apple.pos
                if abs(px - ax) < BLOCK_SIZE and abs(py - ay) < BLOCK_SIZE:
                    if apple.golden:
                        player.score += 3
                    else:
                        player.grow()
                    apple.pos = apple.random_pos()
                    apple.set_golden(False)
                    if player.score % 5 == 0:
                        apple.set_golden(True)
                        level_up_timer = 45  # show "LEVEL UP!" for ~3 sec

            # Drawing
            screen.fill(BLACK)
            p1.draw()
            p2.draw()
            apple.draw()

            # Timer
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            remaining_time = max(60 - elapsed_time, 0)
            timer_text = FONT.render(f"Time: {remaining_time}s", True, WHITE)
            timer_rect = timer_text.get_rect(center=(WIDTH//2, 30))
            screen.blit(timer_text, timer_rect)

            # End game if timer runs out
            if remaining_time <= 0:
                run = False

            # Scores
            s1 = FONT.render(f"{n1}: {p1.score}", True, CYAN)
            s2 = FONT.render(f"{n2}: {p2.score}", True, LIGHT_GREEN)
            screen.blit(s1, (10, 10))
            screen.blit(s2, (WIDTH - s2.get_width() - 10, 10))

            # Level up message
            if level_up_timer > 0:
                draw_text_center("LEVEL UP!", 50, TITLE_FONT, GOLD)
                level_up_timer -= 1

            pygame.display.flip()
            clock.tick(FPS)

        # Show end screen and get play again choice
        playing = end_screen(p1, p2, n1, n2, total_wins)


if __name__ == "__main__":
    main()
