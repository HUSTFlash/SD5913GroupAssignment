import pygame
import random
import math
import sys

# Constants
enemy_num = 50
enemy_size_min = 1
enemy_size_max = 5
screen_width = 1280
screen_height = 720
YELLOW_BALL_GENERATION_EVENT = pygame.USEREVENT + 1
YELLOW_BALL_GENERATION_INTERVAL = 1000  # 1000 milliseconds = 1 second

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Eat Ball Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 80)

# Start yellow ball generation event
pygame.time.set_timer(YELLOW_BALL_GENERATION_EVENT, YELLOW_BALL_GENERATION_INTERVAL)

# Class definitions
class Ball:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.status = True

    def eat(self, target_ball):
        if self != target_ball and self.status and target_ball.status:
            distance = math.sqrt((self.x - target_ball.x)**2 + (self.y - target_ball.y)**2)
            if distance <= self.size:
                target_ball.status = False
                self.size += target_ball.size

    def get_speed(self):
        base_speed = 2  # Base speed factor
        return base_speed / (self.size / 25 + 1)  # Speed decreases as size increases

class PlayerBall(Ball):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", (int(self.x), int(self.y)), self.size)

class EnemyBall(Ball):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)

    def draw(self, screen):
        pygame.draw.circle(screen, "yellow", (int(self.x), int(self.y)), self.size)

class AIBall(Ball):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)

    def draw(self, screen):
        pygame.draw.circle(screen, "blue", (int(self.x), int(self.y)), self.size)

    def find_nearest_ball(self, balls, player_ball):
        nearest_ball = None
        min_distance = float('inf')
        for ball in balls:
            if ball.status and ball != self and ball.size <= self.size:
                distance = math.sqrt((self.x - ball.x) ** 2 + (self.y - ball.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_ball = ball
        if player_ball.status and player_ball.size <= self.size:
            distance = math.sqrt((self.x - player_ball.x) ** 2 + (self.y - player_ball.y) ** 2)
            if distance < min_distance:
                min_distance = distance
                nearest_ball = player_ball
        return nearest_ball

    def move_toward_ball(self, target_ball):
        if target_ball:
            dx, dy = target_ball.x - self.x, target_ball.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            speed = self.get_speed()
            if distance > 0:
                self.x += speed * (dx / distance)
                self.y += speed * (dy / distance)
            # Keep AI within screen bounds
            self.x = max(self.size, min(self.x, screen_width - self.size))
            self.y = max(self.size, min(self.y, screen_height - self.size))

    def move_away_from_ball(self, target_ball):
        if target_ball:
            dx, dy = self.x - target_ball.x, self.y - target_ball.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
            speed = self.get_speed()
            if distance > 0:
                self.x += speed * (dx / distance)
                self.y += speed * (dy / distance)
            # Keep AI within screen bounds
            self.x = max(self.size, min(self.x, screen_width - self.size))
            self.y = max(self.size, min(self.y, screen_height - self.size))

    def ai_logic(self, balls, player_ball):
        nearest_ball = self.find_nearest_ball(balls, player_ball)
        if nearest_ball:
            if nearest_ball.size < self.size:
                self.move_toward_ball(nearest_ball)
            else:
                self.move_away_from_ball(nearest_ball)

# Functions
def create_player_ball():
    initial_position_x = screen_width / 2
    initial_position_y = screen_height / 2
    player_initial_size = 10  # Separate player size
    player_ball = PlayerBall(initial_position_x, initial_position_y, player_initial_size)
    return player_ball

def create_enemy_ball(balls, num=1):
    for _ in range(num):
        enemy_position_x = random.randint(0, screen_width)
        enemy_position_y = random.randint(0, screen_height)
        enemy_size = random.randint(enemy_size_min, enemy_size_max)  # Separate enemy size
        enemy_ball = EnemyBall(enemy_position_x, enemy_position_y, enemy_size)
        balls.append(enemy_ball)

def create_ai_balls(num_ai):
    ai_balls = []
    for _ in range(num_ai):
        ai_x = random.randint(0, screen_width)
        ai_y = random.randint(0, screen_height)
        ai_size = random.randint(enemy_size_min + 5, enemy_size_max + 5)  # Separate AI size
        ai_ball = AIBall(ai_x, ai_y, ai_size)
        ai_balls.append(ai_ball)
    return ai_balls

def player_move(player_ball):
    speed = player_ball.get_speed()
    key = pygame.key.get_pressed()
    if key[pygame.K_UP] and player_ball.y - speed > 0:
        player_ball.y -= speed
    if key[pygame.K_DOWN] and player_ball.y + speed < screen_height:
        player_ball.y += speed
    if key[pygame.K_LEFT] and player_ball.x - speed > 0:
        player_ball.x -= speed
    if key[pygame.K_RIGHT] and player_ball.x + speed < screen_width:
        player_ball.x += speed

def player_eat(player_ball, balls):
    for ball in balls:
        player_ball.eat(ball)

def draw_screen(player_ball, balls, screen):
    screen.fill("black")
    if player_ball.status:
        player_ball.draw(screen)
    for ball in balls:
        if ball.status:
            ball.draw(screen)

def check_game_end(player_ball, enemy_balls, ai_balls):
    if not player_ball.status:
        return "lose"  # Player lost

    # Check if all AI balls have been eaten
    if all(not ai_ball.status for ai_ball in ai_balls):
        return "win"  # Player won

    return None  # Game is not over yet

def main():
    enemy_balls = []
    ai_balls = create_ai_balls(8)  # Adding AI balls
    try:
        replay_img = pygame.image.load("Replay_Button.png").convert_alpha()
        exit_img = pygame.image.load("Exit_Button.png").convert_alpha()
    except pygame.error as e:
        print(f"Error loading images: {e}")
        pygame.quit()
        sys.exit()

    player_ball = create_player_ball()
    game_end = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == YELLOW_BALL_GENERATION_EVENT:
                # Generate 2 to 5 yellow balls every second
                num_new_balls = random.randint(2, 5)
                create_enemy_ball(enemy_balls, num_new_balls)
                # Optional: Limit total number of enemy balls to prevent overflow
                if len(enemy_balls) > enemy_num:
                    enemy_balls = enemy_balls[-enemy_num:]
        
        if not game_end:
            draw_screen(player_ball, enemy_balls + ai_balls, screen)
            player_move(player_ball)
            player_eat(player_ball, enemy_balls + ai_balls)

            for ai_ball in ai_balls:
                ai_ball.ai_logic(enemy_balls + ai_balls, player_ball)
                ai_ball.eat(player_ball)
                for ball in enemy_balls:
                    ai_ball.eat(ball)
                for other_ai_ball in ai_balls:
                    ai_ball.eat(other_ai_ball)
            
            game_end = game_end = check_game_end(player_ball, enemy_balls, ai_balls)
        
        if game_end:
            end_text = 'Congratulations! You have eaten all balls!' if game_end == "win" else 'You lose. Try again!'
            gameover_text = font.render(end_text, True, "red")
            text_rect = gameover_text.get_rect(center=(screen_width // 2, screen_height // 3))
            screen.blit(gameover_text, text_rect)
            screen.blit(replay_img, (440, 310))
            screen.blit(exit_img, (440, 460))
            pygame.display.flip()
            # Pause the game loop until the user clicks replay or exit
            while game_end:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        pos = pygame.mouse.get_pos()
                        if 440 < pos[0] < 918 and 310 < pos[1] < 410:
                            main()  # Restart the game
                        elif 440 < pos[0] < 918 and 460 < pos[1] < 560:
                            pygame.quit()
                            sys.exit()
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
