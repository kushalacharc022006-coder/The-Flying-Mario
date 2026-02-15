import pygame
import cv2
import sys
import random
import mediapipe as mp

# ---Mediapipe Setup---
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpdraw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# ---Pygame Setup---
pygame.init()

WIDTH, HEIGHT = 800, 600
GROUND_HEIGHT = 45
FPS = 90

WHITE = (0, 0, 255)
BLUE = (0, 225, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Mario Game")

clock = pygame.time.Clock()

# ---Load Assets---
mario_image = pygame.image.load("mario641.png")
mario_image = pygame.transform.scale(mario_image, (60, 80))
mario_flipped_image = pygame.transform.flip(mario_image, True, False)

enemy_image = pygame.image.load("enemy1.png")
enemy_image = pygame.transform.scale(enemy_image, (50, 60))

bullet_image = pygame.image.load("bullet1.png")
bullet_image = pygame.transform.scale(bullet_image, (20, 10))

cloud_image = pygame.image.load("cloud.png")
cloud_image = pygame.transform.scale(cloud_image, (120, 70))

sun_image = pygame.image.load("sun1.png")
sun_image = pygame.transform.scale(sun_image, (80, 80))

tree_image = pygame.image.load("tree.png")
tree_image = pygame.transform.scale(tree_image, (80, 120))

coin_image = pygame.image.load("coin.png")
coin_image = pygame.transform.scale(coin_image, (35, 35))

# ----Mario Setup---
mario_rect = mario_image.get_rect()
mario_rect.topleft = (100, HEIGHT - GROUND_HEIGHT - mario_rect.height)
mario_direction = "right"

mario_speed = 10

velocity_y = 0
fly_speed = -12
gravity_force = 0.8
max_fall_speed = 10

shoot_cooldown = 0

# ---Game Objects---
sky_enemies = []
max_sky_enemies = 5
sky_enemy_spawn_rate = 0.02
enemy_speed = 3

bullets = []
bullet_speed = 10

clouds = []
cloud_speed = 3

trees = []
tree_speed = 2

coins = []
max_coins = 5
coin_spawn_rate = 0.02

score = 0

sun_rect = sun_image.get_rect()
sun_rect.topleft = (50, 50)

# ---Functions---
def create_cloud():
    rect = cloud_image.get_rect()
    rect.topleft = (WIDTH, random.randint(50, 200))
    return rect

def create_tree():
    rect = tree_image.get_rect()
    rect.topleft = (WIDTH, HEIGHT - GROUND_HEIGHT - rect.height)
    return rect

def create_sky_enemy():
    rect = enemy_image.get_rect()
    rect.topleft = (random.randint(0, WIDTH - rect.width),
                    random.randint(0, HEIGHT // 2))
    return rect

def create_bullet():
    rect = bullet_image.get_rect()
    if mario_direction == "right":
        rect.topleft = (mario_rect.right,
                        mario_rect.centery - rect.height // 2)
    else:
        rect.topleft = (mario_rect.left - rect.width,
                        mario_rect.centery - rect.height // 2)
    return rect

def create_coin():
    rect = coin_image.get_rect()
    rect.topleft = (
        random.randint(0, WIDTH - rect.width),
        random.randint(0, HEIGHT - GROUND_HEIGHT - rect.height)
    )
    return rect

#Main Loop
while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if shoot_cooldown == 0:
                bullets.append(create_bullet())
                shoot_cooldown = 15

    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    # Clouds
    for c in clouds:
        c.x -= cloud_speed
    if not clouds or clouds[-1].right < WIDTH - 200:
        clouds.append(create_cloud())

    # Trees
    for t in trees:
        t.x -= tree_speed
    if not trees or trees[-1].right < WIDTH - 300:
        trees.append(create_tree())

    # Bullets
    for b in bullets:
        if mario_direction == "right":
            b.x += bullet_speed
        else:
            b.x -= bullet_speed
    bullets = [b for b in bullets if 0 < b.x < WIDTH]

    # Enemies
    if random.random() < sky_enemy_spawn_rate and len(sky_enemies) < max_sky_enemies:
        sky_enemies.append(create_sky_enemy())

    for e in sky_enemies:
        e.x += enemy_speed
    sky_enemies = [e for e in sky_enemies if 0 < e.x < WIDTH]

    # Bullet Collision
    for b in bullets[:]:
        for e in sky_enemies[:]:
            if b.colliderect(e):
                score += 20
                bullets.remove(b)
                sky_enemies.remove(e)

    # Mario Collision
    for e in sky_enemies:
        if mario_rect.colliderect(e):
            print("Score:", score)
            pygame.quit()
            sys.exit()

    # Coins
    if random.random() < coin_spawn_rate and len(coins) < max_coins:
        coins.append(create_coin())

    for c in coins[:]:
        if mario_rect.colliderect(c):
            score += 10
            coins.remove(c)

    # ---Flying---
    velocity_y += gravity_force
    if velocity_y > max_fall_speed:
        velocity_y = max_fall_speed

    mario_rect.y += velocity_y

    ground_level = HEIGHT - GROUND_HEIGHT - mario_rect.height
    if mario_rect.y >= ground_level:
        mario_rect.y = ground_level
        velocity_y = 0

    if mario_rect.y <= 0:
        mario_rect.y = 0
        velocity_y = 0

    # --- Hand Tracking ---
    success, img = cap.read()
    if success:
        img1 = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                x = []
                y = []
                h, w, c = img1.shape

                for lm in handLms.landmark:
                    x.append(int(lm.x * w))
                    y.append(int((1 - lm.y) * h))

                if len(y) > 20:

                    # Move Left
                    if ((x[2] > x[4]) and not(y[8] > y[6]) and
                        not(y[12] > y[10]) and not(y[16] > y[14]) and
                        not(y[20] > y[18]) and mario_rect.left > 0):
                        mario_direction = "left"
                        mario_rect.x -= mario_speed

                    # Move Right
                    elif (not(x[2] > x[4]) and not(y[8] > y[6]) and
                          not(y[12] > y[10]) and not(y[16] > y[14]) and
                          (y[20] > y[18]) and mario_rect.right < WIDTH):
                        mario_direction = "right"
                        mario_rect.x += mario_speed

                    # Fly 
                    elif ((x[2] > x[4]) and (y[8] > y[6]) and
                          (y[12] > y[10]) and (y[16] > y[14]) and
                          (y[20] > y[18])):
                        velocity_y = fly_speed

                    # Shoot 
                    elif (not(x[2] > x[4]) and
                          (y[8] > y[6]) and
                          not(y[12] > y[10]) and
                          not(y[16] > y[14]) and
                          not(y[20] > y[18]) and shoot_cooldown == 0):
                        bullets.append(create_bullet())
                        shoot_cooldown = 15

                mpdraw.draw_landmarks(img1, handLms,
                                      mpHands.HAND_CONNECTIONS)

        cv2.imshow("img", img1)
        cv2.waitKey(1)

# ---Draw---
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE,
                     (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))

    screen.blit(sun_image, sun_rect)

    if mario_direction == "right":
        screen.blit(mario_image, mario_rect)
    else:
        screen.blit(mario_flipped_image, mario_rect)

    for e in sky_enemies:
        screen.blit(enemy_image, e)

    for b in bullets:
        screen.blit(bullet_image, b)

    for c in clouds:
        screen.blit(cloud_image, c)

    for t in trees:
        screen.blit(tree_image, t)

    for c in coins:
        screen.blit(coin_image, c)

    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)
