import pygame
import sys
import math
import random
from json_data import highScoreManager
from button import Button

pygame.init()
clock = pygame.time.Clock()
infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Menu")

MAIN_MENU_BACKGROUND = pygame.image.load("assets/backgrounds/menu.png").convert()
MAIN_MENU_BACKGROUND = pygame.transform.scale(MAIN_MENU_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

PLAY_BACKGROUND = pygame.image.load("assets/backgrounds/play.png").convert()
PLAY_BACKGROUND = pygame.transform.scale(PLAY_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

font = pygame.font.Font("assets/fonts/font.ttf", 75)

pygame.mixer.init()
pygame.mixer.music.set_volume(0.3)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load("assets/sprites/player.png")
        self.image = pygame.transform.scale(self.image, (100, 100))

        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.health = 100
        self.speed = 5
        self.shadow = pygame.Surface((100, 100))
        self.shadow.fill((150, 150, 150))
        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_cooldown = 250

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_w] and self.rect.y - self.speed >= 0:  # up
            self.rect.y -= self.speed
        if keys_pressed[pygame.K_s] and self.rect.y + self.speed + self.rect.height <= SCREEN_HEIGHT:  # down
            self.rect.y += self.speed
        if keys_pressed[pygame.K_a] and self.rect.x - self.speed >= 0:  # left
            self.rect.x -= self.speed
        if keys_pressed[pygame.K_d] and self.rect.x + self.speed + self.rect.width <= SCREEN_WIDTH:  # right
            self.rect.x += self.speed

    def draw(self, surface):
        # Draw shadow
        surface.blit(self.shadow, (self.rect.x + 5, self.rect.y + 5))
        # Draw player
        surface.blit(self.image, self.rect)

    def draw_health_bar(self, surface):
        # Outer health bar
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 20, self.rect.width, 10))
        # Inner health bar
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 20, self.rect.width * (self.health / 100), 10))

    def create_bullet(self, target_pos):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            return Bullet(self.rect.center[0], self.rect.center[1], target_pos)
        else:
            return None


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, target_pos):
        super().__init__()
        self.image = pygame.Surface((50, 10))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(pos_x, pos_y))
        self.damage = 10
        self.speed = 10
        self.target_pos = target_pos

        # Calculate trajectory of bullet to target position
        x_diff = target_pos[0] - pos_x
        y_diff = target_pos[1] - pos_y
        angle = math.atan2(y_diff, x_diff)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

        # Rotate the bullet image to point towards the target direction
        self.image = pygame.transform.rotate(self.image, -math.degrees(angle))  # -angle because Pygame's y-axis is inverted.

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.x >= SCREEN_WIDTH + 200 or self.rect.x <= -200 or self.rect.y <= -200 or self.rect.y >= SCREEN_HEIGHT + 200:
            self.kill()

class Ghost(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        sprite_sheet = pygame.image.load('assets/sprites/ghost.png').convert_alpha()
        sprite_width, sprite_height = sprite_sheet.get_size()
        sprite_size = min(sprite_width, sprite_height)

        scaled_size = int(sprite_size * 1.8)
        self.images = []
        for i in range(sprite_width // sprite_size):
            image = sprite_sheet.subsurface(pygame.Rect(i * sprite_size, 0, sprite_size, sprite_size))
            scaled_image = pygame.transform.scale(image, (scaled_size, scaled_size))
            self.images.append(scaled_image)

        self.current_image = 0
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect()

        self.health = 100
        self.speed = 1
        self.damage = 2
        self.scaled_size = scaled_size

        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x = random.randint(0, SCREEN_WIDTH)
            y = -100
        elif side == "bottom":
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT
        elif side == "left":
            x = -100
            y = random.randint(0, SCREEN_HEIGHT)
        else:
            x = SCREEN_WIDTH
            y = random.randint(0, SCREEN_HEIGHT)

        self.rect.center = (x, y)

    def update(self):
        if self.health <= 0:
            self.kill()
        else:
            if self.rect.x < player.rect.x:
                self.rect.x += self.speed
            elif self.rect.x > player.rect.x:
                self.rect.x -= self.speed

            if self.rect.y < player.rect.y:
                self.rect.y += self.speed
            elif self.rect.y > player.rect.y:
                self.rect.y -= self.speed

            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]

    def draw_health_bar(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 10, self.scaled_size, 10))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, self.scaled_size * (self.health / 100), 10))

class Demon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('assets/sprites/demon.png').convert_alpha()
        self.rect = self.image.get_rect()

        self.health = 60
        self.speed = 3
        self.damage = 2

        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            x = random.randint(0, SCREEN_WIDTH)
            y = -100
        elif side == "bottom":
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT
        elif side == "left":
            x = -100
            y = random.randint(0, SCREEN_HEIGHT)
        else:
            x = SCREEN_WIDTH
            y = random.randint(0, SCREEN_HEIGHT)
        self.rect.center = (x, y)

    def update(self):
        if self.health <= 0:
            self.kill()
        else:
            dx, dy = self.calculate_movement_vector()
            self.rect.x += dx
            self.rect.y += dy
            self.prevent_collisions()

    def calculate_movement_vector(self):
        dx = 0
        dy = 0
        if self.rect.x < player.rect.x:
            dx = self.speed
        elif self.rect.x > player.rect.x:
            dx = -self.speed
        if self.rect.y < player.rect.y:
            dy = self.speed
        elif self.rect.y > player.rect.y:
            dy = -self.speed
        return dx, dy

    def prevent_collisions(self):
        for demon in demon_group:
            if demon != self and pygame.sprite.collide_rect(self, demon):
                dx = self.rect.x - demon.rect.x
                dy = self.rect.y - demon.rect.y
                distance = math.hypot(dx, dy)
                if distance == 0:
                    distance = 1
                nx = dx / distance
                ny = dy / distance
                overlap = (self.rect.width + demon.rect.width) / 2 - distance
                self.rect.x += overlap * nx
                self.rect.y += overlap * ny


    def draw_health_bar(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 10, 100, 10))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, 100 * (self.health / 60), 10))

player = Player()
player_group = pygame.sprite.GroupSingle(player)
bullet_group = pygame.sprite.Group()
ghost_group = pygame.sprite.Group()
demon_group = pygame.sprite.Group()

SPAWN_GHOST = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_GHOST, random.randint(8000, 12000))  # 6-10 seconds

score_font = pygame.font.Font("assets/fonts/font.ttf", 30)
high_score_font = pygame.font.Font("assets/fonts/font.ttf", 30)

def spawn_ghost():
    ghost = Ghost()
    ghost_group.add(ghost)

def spawn_demon():
    demon = Demon()
    demon_group.add(demon)

high_score_manager = highScoreManager("highScore.json")

def play():
    ghost_group.empty()
    demon_group.empty()
    for _ in range(2):
        spawn_ghost()

    player_group.sprite.rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)

    pygame.mixer.stop()
    pygame.mixer.music.load("assets/sounds/music/main_theme.wav")
    pygame.mixer.music.play(0,0)

    spawn_demon_time = pygame.time.get_ticks()

    while True:
        SCREEN.blit(PLAY_BACKGROUND, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                high_score_manager.update_high_score(high_score_manager.score)
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    bullet = player.create_bullet(MOUSE_POS)
                    if bullet is not None:
                        bullet_group.add(bullet)

            if event.type == SPAWN_GHOST:
                spawn_ghost()

        keys_pressed = pygame.key.get_pressed()
        player_group.update(keys_pressed)
        bullet_group.update()

        for bullet in bullet_group:
            ghost_hit_list = pygame.sprite.spritecollide(bullet, ghost_group, False)
            for ghost in ghost_hit_list:
                ghost.health -= bullet.damage
                bullet.kill()
                if ghost.health <= 0:
                    high_score_manager.score += 1
                    high_score_manager.update_high_score(high_score_manager.score)

        for bullet in bullet_group:
            demon_hit_list = pygame.sprite.spritecollide(bullet, demon_group, False)
            for demon in demon_hit_list:
                demon.health -= bullet.damage
                bullet.kill()
                if demon.health <= 0:
                    high_score_manager.score += 1
                    high_score_manager.update_high_score(high_score_manager.score)

        for player in player_group:
            ghost_touch_list = pygame.sprite.spritecollide(player, ghost_group, False)
            for ghost in ghost_touch_list:
                player.health -= ghost.damage
                if player.health <= 0:
                    high_score_manager.update_high_score(high_score_manager.score)
                    high_score_manager.score=0
                    main_menu()

        for player in player_group:
            demon_touch_list = pygame.sprite.spritecollide(player, demon_group, False)
            for demon in demon_touch_list:
                player.health -= demon.damage
                if player.health <= 0:
                    high_score_manager.update_high_score(high_score_manager.score)
                    main_menu()

        if pygame.time.get_ticks() - spawn_demon_time > random.randint(12000, 15000):
            spawn_demon()
            spawn_demon_time = pygame.time.get_ticks()

        bullet_group.draw(SCREEN)
        player_group.draw(SCREEN)
        for player in player_group:
            player.draw_health_bar(SCREEN)

        ghost_group.update()
        ghost_group.draw(SCREEN)
        for ghost in ghost_group:
            ghost.draw_health_bar(SCREEN)

        demon_group.update()
        demon_group.draw(SCREEN)
        for demon in demon_group:
            demon.draw_health_bar(SCREEN)

        score_text = score_font.render("Score: " + str(high_score_manager.score), True, (255, 255, 255))
        SCREEN.blit(score_text, (10, 10))

        high_score_text = high_score_font.render("High Score: " + str(high_score_manager.high_score), True, (255, 255, 255))
        SCREEN.blit(high_score_text, (10, 50))  # Adjust the position as needed

        pygame.display.update()
        clock.tick(60)

def options():
    while True:
        SCREEN.blit(MAIN_MENU_BACKGROUND, (0, 0))
        
        OPTIONS_TEXT = font.render("Options", True, "#b68f40")
        SCREEN.blit(OPTIONS_TEXT, (500, 20))

        RESET_TEXT = font.render("Reset high score", True, "white")
        RESET_TEXT = pygame.transform.scale(RESET_TEXT, (650, 70))
        reset_text_pos = SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 3
        SCREEN.blit(RESET_TEXT, reset_text_pos)

        HIGH_SCORE_RESET = Button(image=pygame.image.load("assets/menu/Quit_Rect.png"), pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 
            text_input="RESET", font=font, base_color="#d7fcd4", hovering_color="white")
        for button in [HIGH_SCORE_RESET]:
            button.changeColor(pygame.mouse.get_pos())
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                high_score_manager.update_high_score(high_score_manager.score)
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if HIGH_SCORE_RESET.checkForInput(pygame.mouse.get_pos()):
                    high_score_manager.reset_high_score()
                    high_score_manager.reset_current_score()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()
        
        pygame.display.update()
        clock.tick(60)

def main_menu():
    MENU_TEXT = font.render("Shadow Siege", True, "#b68f40")
    MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5))

    PLAY_BUTTON = Button(image=pygame.image.load("assets/menu/Play_Rect.png"), pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 
        text_input="PLAY", font=font, base_color="#d7fcd4", hovering_color="White")
    QUIT_BUTTON = Button(image=pygame.image.load("assets/menu/Quit_Rect.png"), pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5), 
        text_input="QUIT", font=font, base_color="#d7fcd4", hovering_color="White")
    OPTIONS_BUTTON = Button(image=pygame.image.load("assets/menu/Options_Rect.png"), pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.2), 
        text_input="OPTIONS", font=font, base_color="#d7fcd4", hovering_color="White")

    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/sounds/music/menu_theme.wav")
    pygame.mixer.music.play(0,0)

    while True:
        SCREEN.blit(MAIN_MENU_BACKGROUND, (0, 0))
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON, OPTIONS_BUTTON]:
            button.changeColor(pygame.mouse.get_pos())
            button.update(SCREEN)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                high_score_manager.update_high_score(high_score_manager.score)
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(pygame.mouse.get_pos()):
                    play()
                if QUIT_BUTTON.checkForInput(pygame.mouse.get_pos()):
                    high_score_manager.update_high_score(high_score_manager.score)
                    pygame.quit()
                    sys.exit()
                if OPTIONS_BUTTON.checkForInput(pygame.mouse.get_pos()):
                    options()

        pygame.display.flip()
        clock.tick(60)

main_menu()