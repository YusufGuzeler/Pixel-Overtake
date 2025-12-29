import pygame
import random
import time


# GENEL AYARLAR

WIDTH, HEIGHT = 1280, 720
FPS = 60

PLAY_AREA_WIDTH = 512
LANE_COUNT = 4

SPAWN_MIN = 60
SPAWN_MAX = 110
MIN_DISTANCE = 220
LANE_CHANGE_DISTANCE = 160

BASE_SPEED = 3.0
MAX_SPEED = 16.0
ACC = 0.12
DEC = 0.08

# INIT
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)

CH_TURBO   = pygame.mixer.Channel(0)
CH_AMB     = pygame.mixer.Channel(1)
CH_POL     = pygame.mixer.Channel(2)
CH_START   = pygame.mixer.Channel(3)
CH_CRASH   = pygame.mixer.Channel(4)

sfx_turbo  = pygame.mixer.Sound("car-engine-speeding.mp3")
sfx_amb    = pygame.mixer.Sound("ambulance-2.mp3")
sfx_pol    = pygame.mixer.Sound("police-sirenss.mp3")
sfx_start  = pygame.mixer.Sound("car-engine.mp3")
sfx_crash  = pygame.mixer.Sound("car-crash.mp3")

sfx_turbo.set_volume(0.6)
sfx_amb.set_volume(0.7)
sfx_pol.set_volume(0.7)
sfx_start.set_volume(0.7)
sfx_crash.set_volume(0.9)

turbo_playing = False
amb_playing = False
pol_playing = False

last_crash_t = 0.0
CRASH_CD = 0.35

def stop_all_loops():
    global turbo_playing, amb_playing, pol_playing
    CH_TURBO.stop(); turbo_playing = False
    CH_AMB.stop();   amb_playing = False
    CH_POL.stop();   pol_playing = False
# ======================================================

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Overtake")
clock = pygame.time.Clock()

FONT_PATH = "Pixeltype.ttf"

credits_title_font = pygame.font.Font(FONT_PATH, 48)
credits_name_font = pygame.font.Font(FONT_PATH, 40)

score_font = pygame.font.Font(FONT_PATH, 32)
title_font = pygame.font.Font(FONT_PATH, 36)

# PLAY AREA & LANES

PLAY_AREA_LEFT = (WIDTH - PLAY_AREA_WIDTH) // 2
LANE_WIDTH = PLAY_AREA_WIDTH // LANE_COUNT
LANES = [
    PLAY_AREA_LEFT + LANE_WIDTH * i + LANE_WIDTH // 2
    for i in range(LANE_COUNT)
]

# PLAYER

car_img = pygame.image.load("car.png").convert_alpha()
CAR_W, CAR_H = car_img.get_width(), car_img.get_height()

player_x = LANES[1]
player_y = HEIGHT - CAR_H - 40
MOVE_SPEED = 6

LEFT_LIMIT = PLAY_AREA_LEFT + CAR_W // 2
RIGHT_LIMIT = PLAY_AREA_LEFT + PLAY_AREA_WIDTH - CAR_W // 2

player_rect = pygame.Rect(player_x - CAR_W // 2, player_y, CAR_W, CAR_H)
player_mask = pygame.mask.from_surface(car_img)


# OBSTACLE

obstacle_defs = [
    {
        "img": pygame.image.load("obstacle_car1.png").convert_alpha(),
        "speed": (3.5, 5.0),
        "weight": 50
    },
    {
        "img": pygame.image.load("obstacle_car2.png").convert_alpha(),
        "speed": (3.5, 5.0),
        "weight": 50
    },
    {
        "img": pygame.image.load("obstacle_truck.png").convert_alpha(),
        "speed": (1.5, 2.5),
        "weight": 20
    },
    {
        "img": pygame.image.load("sinop.png").convert_alpha(),
        "speed": (3.5, 5.0),
        "weight": 20
    },
    {
        "img": pygame.image.load("gs.png").convert_alpha(),
        "speed": (3.5, 5.0),
        "weight": 20
    },
    {
        "img": pygame.image.load("fb.png").convert_alpha(),
        "speed": (3.5, 5.0),
        "weight": 20
    },
    {
        "img": pygame.image.load("bjk.png").convert_alpha(),
        "speed": (3.5, 5.0),
        "weight": 20
    },
    {
        "img": pygame.image.load("polis.png").convert_alpha(),
        "speed": (3.5, 5.0),
        "weight": 20
    },
    {
        "img": pygame.image.load("ambulans.png").convert_alpha(),
        "speed": (3.5, 5.0),
        "weight": 50
    }
]

# OBSTACLE TYPE MAP (EK)

IMG_TYPE = {
    id(obstacle_defs[7]["img"]): "police",
    id(obstacle_defs[8]["img"]): "ambulance",
}

# MENU & UI

menu_bg = pygame.transform.scale(
    pygame.image.load("menu_bg.png").convert(),
    (WIDTH, HEIGHT)
)

logo_img = pygame.image.load("logo.png").convert_alpha()

play_raw = pygame.image.load("Play.png").convert_alpha()
PLAY_SCALE = 0.2
play_img = pygame.transform.scale(
    play_raw,
    (int(play_raw.get_width() * PLAY_SCALE),
     int(play_raw.get_height() * PLAY_SCALE))
)

exit_raw = pygame.image.load("exit.png").convert_alpha()

EXIT_SCALE = 0.2  # 500x500 → 100x100 civarı (istersen 0.25 yap)
exit_img = pygame.transform.smoothscale(
    exit_raw,
    (int(exit_raw.get_width() * EXIT_SCALE),
     int(exit_raw.get_height() * EXIT_SCALE))
)



FINAL_W = play_img.get_width()
FINAL_H = play_img.get_height()

try_raw = pygame.image.load("try_again.png").convert_alpha()
retry_img = pygame.transform.smoothscale(try_raw, (FINAL_W, FINAL_H))


menu_raw = pygame.image.load("menu.png").convert_alpha()
menu_button_img = pygame.transform.smoothscale(menu_raw, (FINAL_W, FINAL_H))


credits_raw = pygame.image.load("credits.png").convert_alpha()
credits_img = pygame.transform.smoothscale(credits_raw, (FINAL_W, FINAL_H))




# --- DİĞER GÖSTERGELER ---
score_bg_raw = pygame.image.load("score_bg.png").convert_alpha()
score_bg = pygame.transform.scale(
    score_bg_raw,
    (int(score_bg_raw.get_width() * 0.2),
     int(score_bg_raw.get_height() * 0.2))
)
score_bg_rect = score_bg.get_rect(topright=(WIDTH - 20, 20))

speed_bg_raw = pygame.image.load("speed_bg.png").convert_alpha()
speed_bg = pygame.transform.scale(
    speed_bg_raw,
    (int(speed_bg_raw.get_width() * 0.4),
     int(speed_bg_raw.get_height() * 0.4))
)
speed_bg_rect = speed_bg.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))

# --- KONUMLAR (RECT) ---
cx, cy = WIDTH // 2, HEIGHT // 2

logo_rect = logo_img.get_rect(center=(cx, cy - 140))
play_rect = play_img.get_rect(center=(cx, cy + 140))
credits_rect = credits_img.get_rect(center=(cx, cy + 260))
exit_rect = exit_img.get_rect(center=(cx, cy + 330))

# Butonların yerleşimi
retry_rect = retry_img.get_rect(center=(WIDTH // 2, 360))
menu_button_rect = menu_button_img.get_rect(center=(WIDTH // 2, 480))
MENU_BTN_Y_NORMAL = menu_button_rect.centery
MENU_BTN_Y_CREDITS = 100  # yukarıda dursun istediğin değer

# ROAD

road_img = pygame.image.load("road.png").convert()
ROAD_H = road_img.get_height()
ROAD_X = (WIDTH - road_img.get_width()) // 2
road_offset = 0.0



# OBSTACLE CLASS

class Obstacle:
    def __init__(self, lane):
        data = random.choices(
            obstacle_defs,
            weights=[d["weight"] for d in obstacle_defs],
            k=1
        )[0]

        self.image = data["img"]
        self.type = IMG_TYPE.get(id(self.image), "normal")  # (EK)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = random.uniform(*data["speed"])

        self.w = self.image.get_width()
        self.h = self.image.get_height()

        self.lane = lane
        self.target_lane = lane

        self.x = LANES[lane]
        self.y = -self.h - random.randint(40, 120)

        self.rect = pygame.Rect(
            self.x - self.w // 2,
            self.y,
            self.w,
            self.h
        )

    def check_lane_change(self):
        for o in obstacles:
            if o == self:
                continue
            if o.lane == self.lane and 0 < o.y - self.y < LANE_CHANGE_DISTANCE:
                if self.lane > 0 and is_lane_free(self.lane - 1, self.y):
                    self.target_lane = self.lane - 1
                elif self.lane < LANE_COUNT - 1 and is_lane_free(self.lane + 1, self.y):
                    self.target_lane = self.lane + 1
                break

    def update(self):
        self.y += current_speed - self.speed
        self.check_lane_change()

        tx = LANES[self.target_lane]
        if abs(self.x - tx) < 2:
            self.x = tx
            self.lane = self.target_lane
        elif self.x < tx:
            self.x += 2
        else:
            self.x -= 2

        self.rect.topleft = (self.x - self.w // 2, self.y)

    def draw(self):
        screen.blit(self.image, self.rect.topleft)


# HELPERS

def is_lane_free(lane, y):
    for o in obstacles:
        if o.lane == lane and abs(o.y - y) < MIN_DISTANCE:
            return False
    return True


def can_spawn(lane):
    for o in obstacles:
        if o.lane == lane and o.y < MIN_DISTANCE:
            return False
    return True


# RESET GAME
def reset_game():
    global obstacles, spawn_timer, current_speed, score, player_x

    obstacles.clear()
    spawn_timer = 0
    current_speed = BASE_SPEED
    score = 0
    player_x = LANES[1]


# GAME OVER SCREEN
def draw_gameover():
    screen.blit(menu_bg, (0, 0))

    over_txt = score_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(over_txt, over_txt.get_rect(center=(WIDTH // 2, 180)))

    score_txt = score_font.render(f"SCORE: {int(final_score)}", True, (255, 215, 0))
    screen.blit(score_txt, score_txt.get_rect(center=(WIDTH // 2, 240)))

    screen.blit(retry_img, retry_rect)
    screen.blit(menu_button_img, menu_button_rect)

def draw_credits():
    screen.blit(menu_bg, (0, 0))

    y = 160
    line_gap = 42

    credits = [
        ("Game Director", "Battal Kaan Erol"),
        ("Lead Programmer", "Suheda Enhar Acikel"),
        ("Lead Art Designer", "Aliyar Tasc,oglu"),
        ("UI Design", "Yagiz Hayirlioglu, Battal Kaan Erol, Yusuf Guzeler"),
        ("Gameplay Mechanics", "Kadirhan Yaman, Efe Gulbeyaz, Eren Utku Husmen"),
        ("Audio Design", "Kagan Ozer"),
    ]

    for title, names in credits:
        title_txt = credits_title_font.render(title, False, (255, 215, 0))
        name_txt = credits_name_font.render(names, False, (0, 0, 0))

        screen.blit(title_txt, title_txt.get_rect(center=(WIDTH // 2, y)))
        y += line_gap
        screen.blit(name_txt, name_txt.get_rect(center=(WIDTH // 2, y)))
        y += line_gap + 12

    screen.blit(menu_button_img, menu_button_rect)



# GAME STATE

game_state = "menu"
final_score = 0
obstacles = []
spawn_timer = 0
score = 0.0
current_speed = BASE_SPEED
running = True

# MAIN LOOP

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # --- MENÜ ---
            if game_state == "menu":
                if play_rect.collidepoint(event.pos):
                    game_state = "game"
                    reset_game()
                    stop_all_loops()
                    CH_START.play(sfx_start)

                if credits_rect.collidepoint(event.pos):
                    game_state = "credits"
                    menu_button_rect.centery = MENU_BTN_Y_CREDITS
                    stop_all_loops()

                if exit_rect.collidepoint(event.pos):
                    running = False

            if game_state == "gameover":
                if retry_rect.collidepoint(event.pos):
                    reset_game()
                    game_state = "game"
                    stop_all_loops()
                    CH_START.play(sfx_start)

                if menu_button_rect.collidepoint(event.pos):
                    game_state = "menu"

                    stop_all_loops()

            if game_state == "credits":
                if menu_button_rect.collidepoint(event.pos):
                    game_state = "menu"
                    menu_button_rect.centery = MENU_BTN_Y_NORMAL

                    stop_all_loops()

    # GÖRÜNTÜLEME
    if game_state == "menu":
        screen.blit(menu_bg, (0, 0))
        screen.blit(logo_img, logo_rect)
        screen.blit(play_img, play_rect)
        screen.blit(credits_img, credits_rect)
        screen.blit(exit_img, exit_rect)
        pygame.display.update()

        continue

    if game_state == "credits":
        draw_credits()
        pygame.display.update()
        continue

    if game_state == "gameover":
        draw_gameover()
        pygame.display.update()
        continue

    # OYUN İÇİ INPUT
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        current_speed = min(MAX_SPEED, current_speed + ACC)
    else:
        current_speed = max(BASE_SPEED, current_speed - DEC)

    if keys[pygame.K_UP]:
        if not turbo_playing:
            CH_TURBO.play(sfx_turbo, loops=-1)
            turbo_playing = True
    else:
        if turbo_playing:
            CH_TURBO.stop()
            turbo_playing = False

    if keys[pygame.K_LEFT]:
        player_x -= MOVE_SPEED
    if keys[pygame.K_RIGHT]:
        player_x += MOVE_SPEED

    player_x = max(LEFT_LIMIT, min(RIGHT_LIMIT, player_x))
    player_rect.x = player_x - CAR_W // 2

    # UPDATE
    score += current_speed * 0.1
    road_offset = (road_offset - current_speed) % ROAD_H

    spawn_timer += 1
    if spawn_timer > random.randint(SPAWN_MIN, SPAWN_MAX):
        lane = random.randint(0, LANE_COUNT - 1)
        if can_spawn(lane):
            obstacles.append(Obstacle(lane))
            spawn_timer = 0

    for o in obstacles:
        o.update()

    obstacles = [o for o in obstacles if o.y < HEIGHT]

    # SIREN LOOP (EK)
    any_amb = any(o.type == "ambulance" for o in obstacles)
    any_pol = any(o.type == "police" for o in obstacles)

    if any_amb and not amb_playing:
        CH_AMB.play(sfx_amb, loops=-1)
        amb_playing = True
    if (not any_amb) and amb_playing:
        CH_AMB.stop()
        amb_playing = False

    if any_pol and not pol_playing:
        CH_POL.play(sfx_pol, loops=-1)
        pol_playing = True
    if (not any_pol) and pol_playing:
        CH_POL.stop()
        pol_playing = False

    #  DRAW
    y = -road_offset
    while y < HEIGHT:
        screen.blit(road_img, (ROAD_X, y))
        y += ROAD_H

    for o in obstacles:
        o.draw()

        if o.rect.colliderect(player_rect):
            offset = (o.rect.x - player_rect.x,
                      o.rect.y - player_rect.y)
            if player_mask.overlap(o.mask, offset):

                # (EK) crash one-shot + loop stop
                now = time.monotonic()
                if (now - last_crash_t) >= CRASH_CD:
                    CH_CRASH.play(sfx_crash)
                    last_crash_t = now
                stop_all_loops()

                final_score = score
                game_state = "gameover"

    screen.blit(car_img, (player_x - CAR_W // 2, player_y))

    screen.blit(score_bg, score_bg_rect)
    txt = score_font.render(str(int(score)), True, (255, 215, 0))
    screen.blit(
        txt,
        txt.get_rect(center=(score_bg_rect.centerx,
                             score_bg_rect.y + int(score_bg_rect.height * 0.72)))
    )

    screen.blit(speed_bg, speed_bg_rect)
    speed_kmh = int(current_speed * 10)
    speed_txt = score_font.render(str(speed_kmh), True, (255, 215, 0))
    box_center_y = speed_bg_rect.y + int(speed_bg_rect.height * 0.68)
    screen.blit(
        speed_txt,
        speed_txt.get_rect(center=(speed_bg_rect.centerx, box_center_y))
    )

    pygame.display.update()

pygame.quit()