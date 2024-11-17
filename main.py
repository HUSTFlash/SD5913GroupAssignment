import pygame
import random
import math
import sys

import pygame.image

ai_num = 4
enemy_num = 20
enemy_size_min = 5
enemy_size_max = 10
screen_width = 1280
screen_height = 720
skill_ball_num = 3
skill_ball_size = 10
skill_refresh_min = 2

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Eat Ball Game")
clock = pygame.time.Clock()
max_speed = 0.1
font = pygame.font.Font(None, 96)

ADD_SKILLBALL_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_SKILLBALL_EVENT, skill_refresh_min * 60 * 1000)

class Ball(object):
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.status = True
        self.skill_id = 0
        self.score = 0

    def eat(self, target_ball):
        if self != target_ball and self.status and target_ball.status:
            if math.sqrt((self.x - target_ball.x)**2 + (self.y - target_ball.y)**2) <= self.size:
                target_ball.status = False
                self.size += target_ball.size
    
    def get_skill(self, target_skill):
        if self.status and target_skill.status:
            if math.sqrt((self.x - target_skill.x)**2 + (self.y - target_skill.y)**2) <= self.size:
                target_skill.status = False
                self.skill_id = target_skill.skill_id
    
    def get_speed(self):
        return max_speed / (self.size / 12)
        
class PlayerBall(Ball):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", (self.x, self.y), self.size)

class AIBall(Ball):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)

    def draw(self, screen):
        pygame.draw.circle(screen, "blue", (self.x, self.y), self.size)

    def find_nearest_ball(self, player_ball, ai_balls, balls):
        distance_player = math.inf
        if self.size > player_ball.size:
            distance_player = math.sqrt((self.x - player_ball.x)**2 + (self.y - player_ball.y)**2)
        distance_otherball = math.inf
        nearest_otherball = None
        for ai_ball in ai_balls:
            if ai_ball == self:
                continue
            else:
                if self.size > ai_ball.size and ai_ball.status:
                    distance_other = math.sqrt((self.x - ai_ball.x)**2 + (self.y - ai_ball.y)**2)
                    if distance_other < distance_otherball:
                        nearest_otherball = ai_ball
                        distance_otherball = distance_other
        distance_enemyball = math.inf
        nearest_enemyball = None
        for ball in balls:
            distance_ball = math.sqrt((self.x - ball.x)**2 + (self.y - ball.y)**2)
            if distance_ball < distance_enemyball and ball.status:
                nearest_enemyball = ball
                distance_enemyball = distance_ball
        
        nearest_ball = None
        nearest_distance = min(distance_player, distance_otherball, distance_enemyball)
        if nearest_distance == distance_player:
            nearest_ball = player_ball
        elif nearest_distance == distance_otherball:
            nearest_ball = nearest_otherball
        else:
            nearest_ball = nearest_enemyball
        return nearest_ball
    
    def move_toward_ball(self, target_ball):
        if target_ball:
            dx = target_ball.x - self.x
            dy = target_ball.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            speed = self.get_speed()
            if self.x <= 0:
                self.x = 0
            elif self.x >= screen_width:
                self.x = screen_width
            else:
                self.x += speed * (dx / distance)
            
            if self.y <= 0:
                self.y = 0
            elif self.y >= screen_height:
                self.y = screen_height
            else:
                self.y += speed * (dy / distance)
    
    def ai_movement(self, player_ball, ai_balls, balls):
        nearest_ball = self.find_nearest_ball(player_ball, ai_balls, balls)
        self.move_toward_ball(nearest_ball)
            

class EnemyBall(Ball):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)

    def draw(self, screen):
        pygame.draw.circle(screen, "yellow", (self.x, self.y), self.size)

class SkillBall(Ball):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)
        skill = random.randint(1, 3)
        match skill:
            case 1: # 1 represents speedup
                self.skill_id = 1
            case 2: # 2 represents flash
                self.skill_id = 2
            case 3: # 3 represents invincible
                self.skill_id = 3

    def draw(self, screen):
        match self.skill_id:
            case 1:
                pygame.draw.circle(screen, "red", (self.x, self.y), self.size)
            case 2:
                pygame.draw.circle(screen, "green", (self.x, self.y), self.size)
            case 3:
                pygame.draw.circle(screen, "orange", (self.x, self.y), self.size)

def create_player_ball():
    initial_position_x = screen_width / 2
    initial_position_y = screen_height / 2
    player_initial_size = 12
    player_ball = PlayerBall(initial_position_x, initial_position_y, player_initial_size)
    return player_ball

def creat_ai_balls(ai_balls):
    if len(ai_balls) < ai_num:
        ai_position_x = random.randint(0, screen_width)
        ai_position_y = random.randint(0, screen_height)
        ai_size = 12
        ai_ball = AIBall(ai_position_x, ai_position_y, ai_size)
        ai_balls.append(ai_ball)

def create_enemy_ball(balls):
    if len(balls) < enemy_num:
        enemy_position_x = random.randint(0, screen_width)
        enemy_position_y = random.randint(0, screen_height)
        enemy_size = random.randint(enemy_size_min, enemy_size_max)
        enemy_ball = EnemyBall(enemy_position_x, enemy_position_y, enemy_size)
        balls.append(enemy_ball)
     
def create_skill_ball(skill_balls):
    if len(skill_balls) < skill_ball_num:
        skill_position_x = random.randint(0, screen_width)
        skill_position_y = random.randint(0, screen_height)
        skill_ball = SkillBall(skill_position_x, skill_position_y, skill_ball_size)
        skill_balls.append(skill_ball)
        
def player_move(player_ball, speed):
    key = pygame.key.get_pressed()
    if key[pygame.K_UP]:
        if player_ball.y <= 0:
            player_ball.y = 0
        player_ball.y -= speed
    if key[pygame.K_DOWN]:
        if player_ball.y >= screen_height:
            player_ball.y = screen_height
        player_ball.y += speed
    if key[pygame.K_LEFT]:
        if player_ball.x <= 0:
            player_ball.x = 0
        player_ball.x -= speed
    if key[pygame.K_RIGHT]:
        if player_ball.x >= screen_width:
            player_ball.x = screen_width
        player_ball.x += speed
        
def player_eat(player_ball, ai_balls, balls):
    for ai_ball in ai_balls:
        player_ball.eat(ai_ball)
    for ball in balls:
        player_ball.eat(ball)

def ai_ball_eat(ai_ball, player_ball, ai_balls, balls):
    ai_ball.eat(player_ball)
    for other_ball in ai_balls:
        if other_ball != ai_ball:
            ai_ball.eat(other_ball)
    for ball in balls:
        ai_ball.eat(ball)
        
def draw_screen(player_ball, ai_balls, balls, skill_balls, screen):
    screen.fill("black")
    if player_ball.status:
        player_ball.draw(screen)
    for ai_ball in ai_balls:
        if ai_ball.status:
            ai_ball.draw(screen)
    for ball in balls:
        if ball.status:
            ball.draw(screen)
    for skill_ball in skill_balls:
        if skill_ball.status:
            skill_ball.draw(screen)

def check_game_end(player_ball, ai_balls):
    gameover = True
    gameending = True
    player_gameover = False
    ai_gameover = True
    
    if player_ball.status == False:
        player_gameover = True
        gameending = False
        
    for ai_ball in ai_balls:
        if ai_ball.status:
            ai_gameover = False
    
    gameover = player_gameover or ai_gameover
    
    return gameover, gameending

def main():
    ai_balls = []
    enemy_balls = []
    skill_balls = []

    replay_img = pygame.image.load("Replay_Button.png")
    exit_img = pygame.image.load("Exit_Button.png")
    game_end = False
    
    player_ball = create_player_ball()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ADD_SKILLBALL_EVENT:
                create_skill_ball(skill_balls)

        if game_end == False:
            creat_ai_balls(ai_balls)
            create_enemy_ball(enemy_balls)
            draw_screen(player_ball, ai_balls, enemy_balls, skill_balls, screen)
            player_move(player_ball, player_ball.get_speed())
            player_eat(player_ball, ai_balls, enemy_balls)
            for ai_ball in ai_balls:
                ai_ball.ai_movement(player_ball, ai_balls, enemy_balls)
                ai_ball_eat(ai_ball, player_ball, ai_balls, enemy_balls)
            game_end = check_game_end(player_ball, ai_balls)

        if game_end:
            gameover_text = font.render('Congratulations! You have eat all balls!', True, "red")
            screen.blit(gameover_text, (0, 160))
            screen.blit(replay_img, (440, 310))
            screen.blit(exit_img, (440, 460))
            mouse_down = pygame.mouse.get_pressed()
            if mouse_down[0]:
                pos = pygame.mouse.get_pos()
                if 440 < pos[0] < 918 and 310 < pos[1] < 410:
                    main()
                elif 440 < pos[0] < 918 and 460 < pos[1] < 560:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
    
if __name__ == "__main__":
    main()