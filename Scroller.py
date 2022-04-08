import pygame
import os

pygame.init()

WIDTH = 800
HEIGHT = int(WIDTH * 0.8)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Knight Runner')

# setting framerate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75
TILE_SIZE = 40

# define player action variables
moving_left = False
moving_right = False
attack = False

# load images
# slash
slash_img = pygame.image.load('PlayerModel/Slash/0.png').convert_alpha()
#pick up boxes
heal_box_img = pygame.image.load('Items/health_box.png').convert_alpha()
sword_box = pygame.image.load('Items/sword_box.png').convert_alpha()
item_boxes = {
    'Health'    : heal_box_img,
    'Sword'     : sword_box
}


# defining colors

BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# define font
font = pygame.font.SysFont('Futura', 30)


def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0, 300), (WIDTH, 300))


class Knight(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.attack_cooldown = 0
        self.health = 100  # could add as an argument within the class if you want different health compared to enemies
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players

        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'{self.char_type}/{animation}/{animation}{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        # the image will be drawn inside this rectangle
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()

        # tells where the rect will be
        self.rect.center = (x, y)


    def update(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1


    def move(self, moving_left, moving_right):
        # reset movement movement variables
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump
        if self.jump == True and self.in_air == False:
            self.vel_y = -16
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def attack(self):
        if self.attack_cooldown == 0 and self.ammo > 0:
            self.attack_cooldown = 20
            slash = Slash(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            slash_group.add(slash)
            # reduce ammo
            self.ammo -= 1



    def ai(self):
        if self.alive and player.alive:
            # handles the logic of the ai
            if self.direction == 1:
                ai_moving_right = True
            else:
                ai_moving_right = False
            ai_moving_left = not ai_moving_right
            self.move(ai_moving_left, ai_moving_right)

    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 250
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            # stops death animation reset using the frame index
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to th previous one
        if new_action != self.action:
            self.action = new_action
            # update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

        # shows the hitbox of the players
        # pygame.draw.rect(screen, RED, self.rect, 1)

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of box it was
            if self.item_type == 'Health':
                # print(player.health)
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
                    # print(player.health)
            elif self.item_type == 'Sword':
                player.ammo += 15
            # delete the item box
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # update with new health
        self.health = health
        # calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Slash(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = slash_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move slash
        self.rect.x += (self.direction * self.speed)
        # check if attack has gone off screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, slash_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, slash_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    print(enemy.health)
                    self.kill()




# create sprite groups
slash_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()



# temp - create item boxes
item_box = ItemBox('Health', 100, 250)
item_box_group.add(item_box)
item_box = ItemBox('Sword', 400, 250)
item_box_group.add(item_box)

# creates the instance of the player
player = Knight('PlayerModel', 200, 200, 1.65, 2, 20)
health_bar = HealthBar(10, 10, player.health, player.health)


enemy = Knight('EnemyModel', 400, 200, 1.65, 2, 20)
enemy2 = Knight('EnemyModel', 500, 300, 1.65, 2, 20)
enemy_group.add(enemy)
enemy_group.add(enemy2)


run = True
while run:

    clock.tick(FPS)

    draw_bg()
    # show player health
    health_bar.draw(player.health)
    # show ammo
    draw_text('SLASHs:  ', font, WHITE, 10, 35)
    for x in range(player.ammo):
        # shows the img of 'bullets' instead of having a number
        screen.blit(slash_img, (130 + (x * 30), 40))

    # pulling from the draw instance
    player.update()

    player.draw()

    player.move(moving_left, moving_right)

    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()

    slash_group.update()
    item_box_group.update()

    slash_group.draw(screen)
    item_box_group.draw(screen)

    # update player actions
    if player.alive:
        # attack
        if attack:
            player.attack()
        if player.in_air:
            player.update_action(2)  # 2: Jump
        elif moving_left or moving_right:
            player.update_action(1)  # 1: RUN
        else:
            player.update_action(0)  # 0: Idle
        player.move(moving_left, moving_right)

    for event in pygame.event.get():
        # to close game
        if event.type == pygame.QUIT:
            run = False
        # keyboard movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True

            if event.key == pygame.K_d:
                moving_right = True

            if event.key == pygame.K_SPACE:
                attack = True

            if event.key == pygame.K_w and player.alive:
                player.jump = True

            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboard button release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False

            if event.key == pygame.K_SPACE:
                attack = False

    pygame.display.update()

pygame.quit()
