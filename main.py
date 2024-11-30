import pygame
import random
import math
import sys

import pygame.image

ai_num = 3
player_initial_size = 20
enemy_num = 20
enemy_size_min = 12
enemy_size_max = 20
enemy_refresh_min = 1
screen_width = 1280
screen_height = 720
skill_ball_num = 3
skill_ball_size = 18
skill_refresh_min = 1

max_speed = 1
speedup_mag = 1.5
flash_distance = 100
speedup_duration = 10000
invincible_duration = 10000

player_img_1 = pygame.image.load("./Art/Player/player_1.png")
player_img_2 = pygame.image.load("./Art/Player/player_2.png")
player_img_3 = pygame.image.load("./Art/Player/player_3.png")
aiplayer_img = pygame.image.load("./Art/Player/Enemy.png")
playing_bg = pygame.image.load("./Art/UI/Background.png")
start_img = pygame.image.load("./Art/UI/Start.png")
success_img = pygame.image.load("./Art/UI/Win.png")
failure_img = pygame.image.load("./Art/UI/Fail.png")
apple = pygame.image.load("./Art/Ball/Apple.png")
blueberry = pygame.image.load("./Art/Ball/Blueberry.png")
kiwi = pygame.image.load("./Art/Ball/Kiwi.png")
orange = pygame.image.load("./Art/Ball/Orange.png")
watermalon = pygame.image.load("./Art/Ball/Watermalon.png")

start_button_rect = pygame.Rect(490, 420, 300, 88)
replay_button_rect = pygame.Rect(450, 400, 330, 75)  
exit_button_rect = pygame.Rect(500, 490, 280, 75)

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Eat Ball Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 96)

ADD_SKILLBALL_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ADD_SKILLBALL_EVENT, skill_refresh_min * 30 * 1000)

REFRESH_BALL_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(REFRESH_BALL_EVENT, enemy_refresh_min * 60 * 1000)



class Ball(object):
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.status = True
        self.skill_id = 0
        self.score = 0
        self.speedup = False
        self.invincible = False
        self.skill_start_time = None
        self.user_input = [0,0]

    def eat(self, target_ball):
        if self != target_ball and self.status and target_ball.status and target_ball.invincible == False:
            if math.sqrt((self.x - target_ball.x)**2 + (self.y - target_ball.y)**2) <= self.size:
                target_ball.status = False
                self.size += target_ball.size
                self.score += target_ball.size
    
    def get_skill(self, target_skill):
        if self.status and target_skill.status and self.skill_id == 0:
            if math.sqrt((self.x - target_skill.x)**2 + (self.y - target_skill.y)**2) <= self.size:
                target_skill.status = False
                self.skill_id = target_skill.skill_id
    
    def use_skill(self):
        match self.skill_id:
            case 1:
                self.skill_id = 0
                self.speedup = True
                self.skill_start_time = pygame.time.get_ticks()
            case 2:
                if self.user_input != [0,0]:
                    self.skill_id = 0
                    self.x += self.user_input[0] * flash_distance
                    self.y += self.user_input[1] * flash_distance
                    if self.y <= 0:
                        self.y = 0
                    if self.y >= screen_height:
                        self.y = screen_height
                    if self.x <= 0:
                        self.x = 0
                    if self.x >= screen_width:
                        self.x = screen_width
                    
            case 3:
                self.skill_id = 0
                self.invincible = True
                self.skill_start_time = pygame.time.get_ticks()
                
    def end_skill(self):
        if self.skill_start_time is None:
            return  # If no skill has been activated, skip the skill end check
    
        current_time = pygame.time.get_ticks()
        if self.speedup:
            if current_time - self.skill_start_time > speedup_duration:
                self.speedup = False
        else:
            if current_time - self.skill_start_time > invincible_duration:
                self.invincible = False
    
    def get_speed(self):
        if self.speedup:
            return max_speed * speedup_mag / (self.size / 12)
        else:
            return max_speed / (self.size / 12)
    
        
class PlayerBall(Ball):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)
        self.img_type = random.randint(1,3)

    def draw(self, screen):
        #pygame.draw.circle(screen, "white", (self.x, self.y), self.size)
        match self.img_type:
            case 1:
                player_image = pygame.transform.scale(player_img_1, (2 * self.size, 2 * self.size))
                player_rect = player_image.get_rect()
                player_rect.center = (self.x, self.y)
            case 2:
                player_image = pygame.transform.scale(player_img_2, (2 * self.size, 2 * self.size))
                player_rect = player_image.get_rect()
                player_rect.center = (self.x, self.y)
            case 3:
                player_image = pygame.transform.scale(player_img_3, (2 * self.size, 2 * self.size))
                player_rect = player_image.get_rect()
                player_rect.center = (self.x, self.y)
        screen.blit(player_image, player_rect)
                

class AIBall(Ball):
    def __init__(self, x, y, size):
        super().__init__(x, y, size)

    def draw(self, screen):
        #pygame.draw.circle(screen, "blue", (self.x, self.y), self.size)
        ai_image = pygame.transform.scale(aiplayer_img, (2 * self.size, 2 * self.size))
        ai_rect = ai_image.get_rect()
        ai_rect.center = (self.x, self.y)
        screen.blit(ai_image, ai_rect)

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
        self.fruit_class = random.randint(1,5)

    def draw(self, screen):
        #pygame.draw.circle(screen, "yellow", (self.x, self.y), self.size)
        match self.fruit_class:
            case 1:
                fruit_image = pygame.transform.scale(apple, (2 * self.size, 2 * self.size))
                fruit_rect = fruit_image.get_rect()
                fruit_rect.center = (self.x, self.y)
            case 2:
                fruit_image = pygame.transform.scale(blueberry, (2 * self.size, 2 * self.size))
                fruit_rect = fruit_image.get_rect()
                fruit_rect.center = (self.x, self.y)
            case 3:
                fruit_image = pygame.transform.scale(kiwi, (2 * self.size, 2 * self.size))
                fruit_rect = fruit_image.get_rect()
                fruit_rect.center = (self.x, self.y)
            case 4:
                fruit_image = pygame.transform.scale(orange, (2 * self.size, 2 * self.size))
                fruit_rect = fruit_image.get_rect()
                fruit_rect.center = (self.x, self.y)
            case 5:
                fruit_image = pygame.transform.scale(watermalon, (2 * self.size, 2 * self.size))
                fruit_rect = fruit_image.get_rect()
                fruit_rect.center = (self.x, self.y)
        screen.blit(fruit_image, fruit_rect)
                

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
    player_ball = PlayerBall(initial_position_x, initial_position_y, player_initial_size)
    return player_ball

def creat_ai_balls(ai_balls):
    while len(ai_balls) < ai_num:
        ai_position_x = random.randint(0, screen_width)
        ai_position_y = random.randint(0, screen_height)
        ai_ball = AIBall(ai_position_x, ai_position_y, player_initial_size)
        ai_balls.append(ai_ball)

def create_enemy_ball(balls):
    while len(balls) < enemy_num:
        enemy_position_x = random.randint(0, screen_width)
        enemy_position_y = random.randint(0, screen_height)
        enemy_size = random.randint(enemy_size_min, enemy_size_max)
        enemy_ball = EnemyBall(enemy_position_x, enemy_position_y, enemy_size)
        balls.append(enemy_ball)

def refresh_enemy_ball(balls):
    if len(balls) != 0:
        for ball in balls:
            if ball.status == False:
                balls.remove(ball)
     
def create_skill_ball(skill_balls):
    if len(skill_balls) != 0:
        for skill_ball in skill_balls:
            if skill_ball.status == False:
                skill_balls.remove(skill_ball)
    while len(skill_balls) < skill_ball_num:
        skill_position_x = random.randint(0, screen_width)
        skill_position_y = random.randint(0, screen_height)
        skill_ball = SkillBall(skill_position_x, skill_position_y, skill_ball_size)
        skill_balls.append(skill_ball)
        
def player_move(player_ball, speed):
    player_ball.user_input = [0,0]
    key = pygame.key.get_pressed()
    if key[pygame.K_UP]:
        player_ball.user_input[1] = -1
        if player_ball.y <= 0:
            player_ball.y = 0
        player_ball.y -= speed
    if key[pygame.K_DOWN]:
        player_ball.user_input[1] = 1
        if player_ball.y >= screen_height:
            player_ball.y = screen_height
        player_ball.y += speed
    if key[pygame.K_LEFT]:
        player_ball.user_input[0] = -1
        if player_ball.x <= 0:
            player_ball.x = 0
        player_ball.x -= speed
    if key[pygame.K_RIGHT]:
        player_ball.user_input[0] = 1
        if player_ball.x >= screen_width:
            player_ball.x = screen_width
        player_ball.x += speed
        
def player_eat(player_ball, ai_balls, balls, skill_balls):
    for ai_ball in ai_balls:
        player_ball.eat(ai_ball)
    for ball in balls:
        player_ball.eat(ball)
    for skill_ball in skill_balls:
        player_ball.get_skill(skill_ball)

def ai_ball_eat(ai_ball, player_ball, ai_balls, balls, skill_balls):
    ai_ball.eat(player_ball)
    for other_ball in ai_balls:
        if other_ball != ai_ball:
            ai_ball.eat(other_ball)
    for ball in balls:
        ai_ball.eat(ball)
    for skill_ball in skill_balls:
        ai_ball.get_skill(skill_ball)
        
def player_use_skill(player_ball):
    key = pygame.key.get_pressed()
    if key[pygame.K_LSHIFT]:
        if player_ball.skill_id != 0 and player_ball.speedup == False and player_ball.invincible == False:
            player_ball.use_skill()

def draw_screen(player_ball, ai_balls, balls, skill_balls, screen, background_img):
    screen.blit(background_img, (0, 0))
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

    game_end = False
    
    player_ball = create_player_ball()

    def start_page():
        start_button_rect = pygame.Rect(490, 420, 300, 88)  # Define the area for the start button
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if start_button_rect.collidepoint(mouse_pos):  # Check if start button is clicked
                        return  # Exit the start page and begin the game
            # Display the start page image
            screen.blit(start_img, (0, 0))  
            pygame.display.flip()  # Update the display to show the start page

    start_page()

    replay_button_rect = pygame.Rect(450, 400, 330, 75)  
    exit_button_rect = pygame.Rect(500, 490, 280, 75)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ADD_SKILLBALL_EVENT:
                create_skill_ball(skill_balls)
            if event.type == REFRESH_BALL_EVENT:
                refresh_enemy_ball(enemy_balls)

        if game_end == False:
            creat_ai_balls(ai_balls)
            create_enemy_ball(enemy_balls)
            draw_screen(player_ball, ai_balls, enemy_balls, skill_balls, screen, playing_bg)
            player_move(player_ball, player_ball.get_speed())
            player_eat(player_ball, ai_balls, enemy_balls, skill_balls)
            player_use_skill(player_ball)
            if player_ball.speedup or player_ball.invincible:
                player_ball.end_skill()
            for ai_ball in ai_balls:
                ai_ball.ai_movement(player_ball, ai_balls, enemy_balls)
                ai_ball_eat(ai_ball, player_ball, ai_balls, enemy_balls, skill_balls)
                if ai_ball.speedup or ai_ball.invincible:
                    ai_ball.end_skill()
            game_end, game_endding = check_game_end(player_ball, ai_balls)

        if game_end:
            if game_endding:
                screen.blit(success_img, (0, 0))

            else:
                screen.blit(failure_img,(0, 0))
             # Draw Testing
            #pygame.draw.rect(screen, "green", replay_button_rect)  
            #pygame.draw.rect(screen, "green", exit_button_rect)                 


            mouse_down = pygame.mouse.get_pressed()
            if mouse_down[0]:
                mouse_pos = pygame.mouse.get_pos()
                if replay_button_rect.collidepoint(mouse_pos):
                    main()  
                elif exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
    
if __name__ == "__main__":
    main()