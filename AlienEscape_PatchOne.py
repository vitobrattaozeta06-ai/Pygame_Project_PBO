import pygame
import random
import sys
import math

# ─── Init ─────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

SW, SH = 900, 560
FPS    = 60

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("ALIEN ESCAPE")
clock  = pygame.time.Clock()

# ─── Warna ────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (200, 30,  30)
DARK_RED   = (120, 0,   0)
BLOOD_RED  = (80,  0,   0)
GREEN      = (50,  200, 80)
DARK_GREEN = (0,   80,  20)
CYAN       = (0,   220, 220)
YELLOW     = (255, 220, 0)
ORANGE     = (255, 130, 0)
PURPLE     = (160, 40,  220)
DARK_BLUE  = (5,   8,   25)
GRAY       = (100, 100, 100)
DARK_GRAY  = (40,  40,  40)
LIGHT_GRAY = (180, 180, 180)

# ─── Font ─────────────────────────────────────────────────
try:
    FONT_LG = pygame.font.SysFont("consolas", 46, bold=True)
    FONT_MD = pygame.font.SysFont("consolas", 26, bold=True)
    FONT_SM = pygame.font.SysFont("consolas", 17)
    FONT_XS = pygame.font.SysFont("consolas", 13)
except Exception:
    FONT_LG = pygame.font.Font(None, 50)
    FONT_MD = pygame.font.Font(None, 30)
    FONT_SM = pygame.font.Font(None, 20)
    FONT_XS = pygame.font.Font(None, 16)

# ─── Gravity ──────────────────────────────────────────────
GRAVITY = 820.0

# ─── Background Images ────────────────────────────────────
BG_IMAGES = {}
for _lvl in range(1, 6):
    try:
        _img = pygame.image.load(f"bg_level{_lvl}.jpg").convert()
        BG_IMAGES[_lvl] = pygame.transform.scale(_img, (900, 560))
    except Exception:
        BG_IMAGES[_lvl] = None

# ─── Space Player Sprite ──────────────────────────────────
try:
    _sp_img = pygame.image.load("spaceship.png").convert_alpha()
    SPACE_PLAYER_SPRITE = pygame.transform.scale(_sp_img, (42, 38))
except Exception as e:
    print(f"[WARN] Could not load spaceship.png: {e}")
    SPACE_PLAYER_SPRITE = None

# ─── Sound Effects ────────────────────────────────────────
def _load_sound(filename):
    """Load a sound file, returning None silently if it fails."""
    try:
        return pygame.mixer.Sound(filename)
    except Exception:
        return None

_SFX = {
    'pistol':               _load_sound("pistol.mp3"),
    'shotgun':              _load_sound("shotgun.mp3"),
    'rocket_launch':        _load_sound("rocket_Launch.mp3"),
    'rocket_explode':       _load_sound("Rocket_Grenade_explode.mp3"),
    'flamethrower':         _load_sound("flamethrower.mp3"),
    'scatter':              _load_sound("scatter.mp3"),
    'laser':                _load_sound("laser.mp3"),
    'enemy_death':          _load_sound("enemy_death.mp3"),
    'boss_death':           _load_sound("boss_death.mp3"),
    'player_damaged':       _load_sound("player_damaged.mp3"),
    'player_death':         _load_sound("player_death.mp3"),
    'space_player_shoot':   _load_sound("spacePlayer_shoot.mp3"),
    'space_spreadshot':     _load_sound("spacePlayer_spreadshot.mp3"),
    'space_enemy_death':    _load_sound("spaceEnemy_death.mp3"),
    'space_megaboss_death': _load_sound("spaceMegaBoss_death.mp3"),
}

def _play(name, volume=1.0):
    """Play a named sound effect at the given volume (0.0-1.0)."""
    sfx = _SFX.get(name)
    if sfx:
        sfx.set_volume(volume)
        sfx.play()

# ── Named sound-trigger functions ─────────────────────────

def play_pistol():
    _play('pistol', 0.6)

def play_shotgun():
    _play('shotgun', 0.7)

def play_rocket_launch():
    _play('rocket_launch', 0.8)

def play_rocket_explode():
    _play('rocket_explode', 0.9)

def play_flamethrower():
    _play('flamethrower', 0.5)

def play_scatter():
    _play('scatter', 0.65)

def play_laser():
    """Railgun / laser beam sound."""
    _play('laser', 0.8)

def play_enemy_death():
    _play('enemy_death', 0.7)

def play_boss_death():
    _play('boss_death', 1.0)

def play_player_damaged():
    _play('player_damaged', 0.8)

def play_player_death():
    _play('player_death', 1.0)

def play_space_player_shoot():
    _play('space_player_shoot', 0.55)

def play_space_spreadshot():
    _play('space_spreadshot', 0.6)

def play_space_enemy_death():
    _play('space_enemy_death', 0.65)

def play_space_megaboss_death():
    _play('space_megaboss_death', 1.0)

# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def draw_text(surf, txt, font, color, x, y, center=False):
    s = font.render(str(txt), True, color)
    if center:
        x -= s.get_width() // 2
    surf.blit(s, (x, y))

def draw_glow_rect(surf, color, rect, glow_size=6):
    gx = pygame.Surface((rect.width + glow_size*2, rect.height + glow_size*2), pygame.SRCALPHA)
    r, g, b = color
    pygame.draw.rect(gx, (r, g, b, 50), gx.get_rect(), border_radius=4)
    surf.blit(gx, (rect.x - glow_size, rect.y - glow_size))
    pygame.draw.rect(surf, color, rect)

def particle_burst(particles, x, y, color, count=12, speed_range=(50, 250)):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(*speed_range)
        particles.append({
            'x': x, 'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed - random.uniform(0, 80),
            'life': random.uniform(0.4, 0.9),
            'max_life': 0.8,
            'color': color,
            'size': random.randint(2, 5)
        })

def draw_vignette(surf):
    """Vignette efek horor di tepi layar."""
    v = pygame.Surface((SW, SH), pygame.SRCALPHA)
    for i in range(80):
        alpha = int(i * 2.2)
        r = max(0, 80 - i)
        pygame.draw.rect(v, (0, 0, 0, alpha), (r, r, SW - 2*r, SH - 2*r), 1)
    surf.blit(v, (0, 0))

def draw_scanlines(surf):
    """CRT scanlines efek."""
    sl = pygame.Surface((SW, SH), pygame.SRCALPHA)
    for y in range(0, SH, 4):
        pygame.draw.line(sl, (0, 0, 0, 30), (0, y), (SW, y))
    surf.blit(sl, (0, 0))

def shake_offset(timer, amount):
    if timer > 0:
        return random.randint(-amount, amount), random.randint(-amount, amount)
    return 0, 0

# ══════════════════════════════════════════════════════════
#  KONFIGURASI LEVEL
# ══════════════════════════════════════════════════════════

LEVEL_CFG = {
    1: {
        'name': 'LEVEL 1: THE CRASH SITE',
        'story': [
            "Kapalmu meledak saat mendarat paksa.",
            "Udara berbau belerang dan kematian.",
            "Bayangan-bayangan bergerak di kegelapan...",
            "Mereka mengintaimu. LARI!"
        ],
        'bg_top':    (8,  5,  18),
        'bg_bot':    (15, 5,  10),
        'ground':    (35, 15, 50),
        'rock':      (55, 25, 75),
        'fog':       (60,  0,  0, 25),
        'enemy_type': 'crawler',
        'enemy_count': 6,
        'boss': None,
        'world_w':   3200,
        'ambience':  (80, 0,  0),
    },
    2: {
        'name': 'LEVEL 2: THE FUNGAL SWAMP',
        'story': [
            "Lumpur hitam menelan setiap langkahmu.",
            "Spora beracun melayang di udara.",
            "Jamur-jamur raksasa... mereka bernapas.",
            "Mereka sadar. Dan lapar."
        ],
        'bg_top':    (4,  10, 4),
        'bg_bot':    (8,  18, 5),
        'ground':    (10, 30, 8),
        'rock':      (20, 50, 12),
        'fog':       (0,  50, 0, 30),
        'enemy_type': 'spitter',
        'enemy_count': 8,
        'boss': None,
        'world_w':   3600,
        'ambience':  (0,  60, 0),
    },
    3: {
        'name': 'LEVEL 3: THE HIVE DEPTHS',
        'story': [
            "Lorong bionik berdenyut seperti jantung.",
            "Telur-telur alien menetes cairan asam.",
            "Suara menderu dari kedalaman...",
            "IBU KOLONI terbangun. Dia tahu kamu di sini."
        ],
        'bg_top':    (15, 4,  4),
        'bg_bot':    (20, 8,  5),
        'ground':    (40, 10, 10),
        'rock':      (70, 18, 18),
        'fog':       (100, 0, 0, 35),
        'enemy_type': 'hunter',
        'enemy_count': 9,
        'boss': 'HIVE QUEEN',
        'world_w':   4000,
        'ambience':  (120, 0, 0),
    },
    4: {
        'name': 'LEVEL 4: THE CRYSTAL CAVES',
        'story': [
            "Kristal hitam berdenyut dengan cahaya merah.",
            "Para Sentry — robot kuno planet ini — aktif.",
            "Sinyal targeting terkunci padamu.",
            "Sistem persenjataan aktif. TARGET: KAMU."
        ],
        'bg_top':    (4,  4,  18),
        'bg_bot':    (6,  8,  25),
        'ground':    (8,  12, 40),
        'rock':      (15, 20, 70),
        'fog':       (0,  0,  80, 30),
        'enemy_type': 'sentry',
        'enemy_count': 10,
        'boss': 'CRYSTAL GUARDIAN',
        'world_w':   4400,
        'ambience':  (0,  0,  100),
    },
    5: {
        'name': 'LEVEL 5: THE LAUNCH PAD',
        'story': [
            "Di sana — pesawat tua yang masih aktif!",
            "Ini satu-satunya kesempatanmu untuk kabur.",
            "Tapi SEMUANYA datang untukmu.",
            "Bunuh semuanya. Terbang. SELAMAT. HIDUP."
        ],
        'bg_top':    (10, 3,  3),
        'bg_bot':    (18, 5,  5),
        'ground':    (35, 8,  8),
        'rock':      (60, 15, 15),
        'fog':       (120, 0, 0, 40),
        'enemy_type': 'elite',
        'enemy_count': 12,
        'boss': 'PLANET LORD',
        'world_w':   5000,
        'ambience':  (150, 0, 0),
    }
}

# ══════════════════════════════════════════════════════════
#  BULLET
# ══════════════════════════════════════════════════════════

class Bullet:
    def __init__(self, x, y, vx, vy, dmg=1, color=CYAN,
                 w=10, h=4, life=1.5, btype='normal'):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.dmg   = dmg
        self.color = color
        self.w, self.h = w, h
        self.life  = life
        self.btype = btype
        self.alive = True

    def update(self, dt):
        self.x    += self.vx * dt
        self.y    += self.vy * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, surf, cam_x=0):
        if not self.alive:
            return
        rx = int(self.x - cam_x)
        r  = pygame.Rect(rx, int(self.y), self.w, self.h)
        if self.btype == 'flame':
            pygame.draw.circle(surf, self.color, (rx + self.w//2, int(self.y) + self.h//2), self.w//2)
        elif self.btype == 'rocket':
            pygame.draw.rect(surf, self.color, r, border_radius=3)
            tail = pygame.Rect(rx - 6, int(self.y) + 1, 8, self.h - 2)
            pygame.draw.rect(surf, YELLOW, tail)
        elif self.btype == 'rail':
            pygame.draw.rect(surf, CYAN, r)
            glow = pygame.Surface((self.w + 4, self.h + 4), pygame.SRCALPHA)
            pygame.draw.rect(glow, (0, 255, 255, 80), glow.get_rect())
            surf.blit(glow, (rx - 2, int(self.y) - 2))
        else:
            pygame.draw.rect(surf, self.color, r, border_radius=2)

# ══════════════════════════════════════════════════════════
#  GRENADE
# ══════════════════════════════════════════════════════════

class Grenade:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.life  = 2.5
        self.alive = True
        self.r     = 6

    def update(self, dt, platforms):
        self.x    += self.vx * dt
        self.y    += self.vy * dt
        self.vy   += GRAVITY * dt
        self.life -= dt
        gr = pygame.Rect(int(self.x) - self.r, int(self.y) - self.r, self.r*2, self.r*2)
        for pl in platforms:
            if gr.colliderect(pl.rect):
                self.vy = -abs(self.vy) * 0.4
                self.vx *= 0.7
                self.y   = pl.rect.top - self.r
        if self.life <= 0:
            self.alive = False

    def draw(self, surf, cam_x):
        if not self.alive:
            return
        if self.life < 0.8 and int(self.life * 15) % 2 == 0:
            col = RED
        else:
            col = (100, 200, 50)
        pygame.draw.circle(surf, col, (int(self.x - cam_x), int(self.y)), self.r)
        pygame.draw.circle(surf, WHITE, (int(self.x - cam_x), int(self.y)), self.r, 1)

# ══════════════════════════════════════════════════════════
#  PLATFORM
# ══════════════════════════════════════════════════════════

class Platform:
    def __init__(self, x, y, w, h, ptype='ground'):
        self.rect  = pygame.Rect(x, y, w, h)
        self.ptype = ptype

    def draw(self, surf, cam_x, cfg):
        r = pygame.Rect(self.rect.x - cam_x, self.rect.y,
                        self.rect.width, self.rect.height)
        if r.right < 0 or r.left > SW:
            return
        base = cfg['ground'] if self.ptype == 'ground' else cfg['rock']
        pygame.draw.rect(surf, base, r)
        lighter = tuple(min(255, c + 30) for c in base)
        pygame.draw.line(surf, lighter, (r.x, r.y), (r.right, r.y), 2)
        if self.ptype == 'ground':
            darker = tuple(max(0, c - 15) for c in base)
            for tx in range(0, self.rect.width, 30):
                dr = pygame.Rect(self.rect.x + tx - cam_x, self.rect.y, 30, self.rect.height)
                pygame.draw.rect(surf, darker, dr, 1)

# ══════════════════════════════════════════════════════════
#  PICKUP
# ══════════════════════════════════════════════════════════

WEAPON_COLORS = {
    'PISTOL':      YELLOW,
    'SHOTGUN':     ORANGE,
    'ROCKET':      RED,
    'FLAMETHROWER': (255, 100, 0),
    'RAILGUN':     CYAN,
    'SCATTER':     GREEN,
}

class Pickup:
    def __init__(self, x, y, ptype, weapon=None):
        self.x, self.y  = float(x), float(y)
        self.ptype      = ptype   # 'weapon' | 'health' | 'grenade'
        self.weapon     = weapon
        self.collected  = False
        self.bob_timer  = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.bob_timer += dt * 2.5

    def draw(self, surf, cam_x):
        if self.collected:
            return
        bx = int(self.x - cam_x)
        by = int(self.y + math.sin(self.bob_timer) * 5)
        if self.ptype == 'weapon':
            col = WEAPON_COLORS.get(self.weapon, YELLOW)
            gsurf = pygame.Surface((34, 22), pygame.SRCALPHA)
            pygame.draw.rect(gsurf, (*col, 60), gsurf.get_rect(), border_radius=4)
            surf.blit(gsurf, (bx - 17, by - 11))
            pygame.draw.rect(surf, col, (bx - 15, by - 9, 30, 18), border_radius=3)
            lbl = FONT_XS.render(self.weapon[:4], True, BLACK)
            surf.blit(lbl, (bx - lbl.get_width()//2, by - lbl.get_height()//2))
            pygame.draw.polygon(surf, WHITE, [(bx, by - 18), (bx - 6, by - 12), (bx + 6, by - 12)])
        elif self.ptype == 'health':
            pygame.draw.circle(surf, DARK_GREEN, (bx, by), 11)
            pygame.draw.circle(surf, GREEN,      (bx, by), 9)
            lbl = FONT_SM.render("+", True, WHITE)
            surf.blit(lbl, (bx - lbl.get_width()//2, by - lbl.get_height()//2))
        elif self.ptype == 'grenade':
            pygame.draw.circle(surf, (60, 160, 40), (bx, by), 9)
            lbl = FONT_XS.render("GR", True, WHITE)
            surf.blit(lbl, (bx - lbl.get_width()//2, by - lbl.get_height()//2))

# ══════════════════════════════════════════════════════════
#  ENEMY (Platformer)
# ══════════════════════════════════════════════════════════

class Enemy:
    COLORS = {
        'crawler': (100, 10,  10),
        'spitter': (10,  80,  10),
        'hunter':  (80,  10,  80),
        'sentry':  (10,  30,  100),
        'elite':   (100, 10,  60),
    }
    EYE_COLORS = {
        'crawler': RED,
        'spitter': GREEN,
        'hunter':  PURPLE,
        'sentry':  CYAN,
        'elite':   (255, 0, 180),
    }

    def __init__(self, x, y, etype, level):
        self.x, self.y   = float(x), float(y)
        self.etype        = etype
        self.w, self.h    = 34, 38
        max_hp = level * 2 + {'crawler':1,'spitter':2,'hunter':3,'sentry':4,'elite':6}.get(etype, 2)
        self.hp = self.max_hp = max_hp
        self.spd          = 60 + level * 12 + random.uniform(0, 30)
        self.vx, self.vy  = 0.0, 0.0
        self.on_ground    = False
        self.alive        = True
        self.facing       = -1
        self.aggro        = False
        self.aggro_range  = 220 + level * 20
        self.shoot_timer  = random.uniform(1.0, 2.5)
        self.bullets      = []
        self.anim_t       = 0.0
        self.pain_t       = 0.0
        self.patrol_min   = x - 110
        self.patrol_max   = x + 110
        self.score_value  = 50 + level * 10

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, player, platforms, particles, cam_x):
        if not self.alive:
            return
        self.anim_t  += dt
        self.pain_t   = max(0.0, self.pain_t - dt)
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < self.aggro_range:
            self.aggro = True
        if self.aggro:
            dx = player.x - self.x
            self.facing = 1 if dx > 0 else -1
            self.vx     = self.facing * self.spd
        else:
            if self.x <= self.patrol_min:
                self.facing = 1
            elif self.x >= self.patrol_max:
                self.facing = -1
            self.vx = self.facing * self.spd * 0.4
        if not self.on_ground:
            self.vy += GRAVITY * dt
        self.vy = min(self.vy, 900)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.on_ground = False
        for pl in platforms:
            self._resolve(pl.rect)
        if self.y > SH + 100:
            self.alive = False
            return
        if self.aggro and self.etype != 'crawler':
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.shoot_timer = 1.4 + random.uniform(-0.3, 0.6)
                self._shoot(player)
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.alive
                        and -50 < b.x - cam_x < SW + 50
                        and 0 < b.y < SH + 50]

    def _resolve(self, rect):
        er = self.get_rect()
        if not er.colliderect(rect):
            return
        ox = min(er.right - rect.left, rect.right - er.left)
        oy = min(er.bottom - rect.top, rect.bottom - er.top)
        if oy <= ox:
            if self.vy >= 0 and er.centery < rect.centery:
                self.y    = rect.top - self.h
                self.vy   = 0
                self.on_ground = True
            elif self.vy < 0:
                self.y   = rect.bottom
                self.vy  = 0
        else:
            if self.vx > 0:
                self.x  = rect.left - self.w
            else:
                self.x  = rect.right
            self.vx = 0

    def _shoot(self, player):
        cx = self.x + self.h//2
        cy = self.y + self.h//2
        tx = player.x + player.w//2
        ty = player.y + player.h//2
        angle = math.atan2(ty - cy, tx - cx)
        spd   = 220 + random.uniform(0, 80)
        self.bullets.append(Bullet(
            cx, cy,
            math.cos(angle)*spd, math.sin(angle)*spd,
            dmg=1, color=RED, w=7, h=7, life=2.5, btype='normal'
        ))

    def take_hit(self, dmg, particles):
        self.hp      -= dmg
        self.pain_t   = 0.2
        particle_burst(particles, self.x + self.w//2, self.y + self.h//2,
                       (180, 0, 0), count=6)
        if self.hp <= 0:
            self.alive = False
            play_enemy_death()
            particle_burst(particles, self.x + self.w//2, self.y + self.h//2,
                           (180, 0, 0), count=18, speed_range=(80, 300))
            return True
        return False

    def draw(self, surf, cam_x):
        if not self.alive:
            return
        rx = int(self.x - cam_x)
        ry = int(self.y)
        col = (230, 230, 230) if (self.pain_t > 0 and int(self.pain_t*20)%2==0) \
              else self.COLORS.get(self.etype, (80, 0, 0))
        body = pygame.Rect(rx, ry, self.w, self.h)
        pygame.draw.rect(surf, col, body, border_radius=4)
        seg_col = tuple(max(0, c - 30) for c in col)
        for i in range(3):
            seg = pygame.Rect(rx + 3, ry + 6 + i*10, self.w - 6, 7)
            pygame.draw.rect(surf, seg_col, seg, border_radius=2)
        eye_x = rx + (self.w - 10 if self.facing > 0 else 4)
        eye_col = self.EYE_COLORS.get(self.etype, RED)
        pygame.draw.rect(surf, eye_col, (eye_x, ry + 7, 8, 5))
        gs = pygame.Surface((12, 9), pygame.SRCALPHA)
        pygame.draw.rect(gs, (*eye_col, 80), gs.get_rect())
        surf.blit(gs, (eye_x - 2, ry + 5))
        bar_w = int(self.w * (self.hp / self.max_hp))
        pygame.draw.rect(surf, DARK_GRAY, (rx, ry - 8, self.w, 4))
        pygame.draw.rect(surf, RED,       (rx, ry - 8, bar_w, 4))

# ══════════════════════════════════════════════════════════
#  BOSS (Platformer)
# ══════════════════════════════════════════════════════════

class Boss:
    _LEVEL_CFG = {
        1: ( 60,  0.90, 0.65, 0.30, 90,  420),
        2: ( 75,  0.80, 0.55, 0.35, 100, 440),
        3: ( 80,  0.85, 0.65, 0.28, 95,  420),  # HIVE QUEEN 
        4: ( 92,  0.75, 0.58, 0.30, 105, 450),  # CRYSTAL GUARDIAN 
        5: (122,  0.60, 0.38, 0.45, 130, 520),  # PLANET LORD
    }

    def __init__(self, x, y, name, level):
        self.x, self.y   = float(x), float(y)
        self.name         = name
        self.w, self.h    = 80, 100

        hp_base, st_n, st_e, enr_pct, spd, jmp = self._LEVEL_CFG.get(
            level, (50 + level*18, 0.70, 0.40, 0.40, 110, 480))

        self.max_hp       = hp_base
        self.hp           = self.max_hp
        self.vx, self.vy  = 0.0, 0.0
        self.on_ground    = False
        self.alive        = True
        self.facing       = -1
        self.enraged      = False
        self.bullets      = []
        self.shoot_timer  = 0.5
        self._shoot_rate_normal  = st_n    # detik antar tembakan normal
        self._shoot_rate_enraged = st_e    # detik antar tembakan enraged
        self._enrage_pct         = enr_pct # threshold HP untuk enraged
        self.pattern      = 0
        self.pattern_t    = 3.5
        self.anim_t       = 0.0
        self.pain_t       = 0.0
        self.spd          = spd
        self._jump_v      = jmp
        self.score_value  = 500 + level * 100
        self.intro_shown  = False

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def _resolve(self, rect):
        er = self.get_rect()
        if not er.colliderect(rect):
            return
        ox = min(er.right - rect.left, rect.right - er.left)
        oy = min(er.bottom - rect.top, rect.bottom - er.top)
        if oy <= ox:
            if self.vy >= 0 and er.centery < rect.centery:
                self.y  = rect.top - self.h
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.y  = rect.bottom
                self.vy = 0
        else:
            if self.vx > 0:
                self.x = rect.left - self.w
            else:
                self.x = rect.right
            self.vx = 0

    def update(self, dt, player, platforms, particles, cam_x):
        if not self.alive:
            return
        self.anim_t  += dt
        self.pain_t   = max(0.0, self.pain_t - dt)
        if self.hp < self.max_hp * self._enrage_pct and not self.enraged:
            self.enraged = True
        dx = player.x - self.x
        self.facing = 1 if dx > 0 else -1
        spd = self.spd * (1.3 if self.enraged else 1.0)
        self.vx = self.facing * spd
        self.pattern_t -= dt
        if self.pattern_t <= 0:
            self.pattern_t = 3.0 + random.uniform(0, 2)
            if self.on_ground:
                self.vy = -(self._jump_v + random.uniform(0, 80))
        if not self.on_ground:
            self.vy += GRAVITY * dt
        self.vy = min(self.vy, 900)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.on_ground = False
        for pl in platforms:
            self._resolve(pl.rect)
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            rate = self._shoot_rate_enraged if self.enraged else self._shoot_rate_normal
            self.shoot_timer = rate
            self.pattern     = (self.pattern + 1) % 4
            self._shoot(player)
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.alive
                        and -50 < b.x - cam_x < SW + 50
                        and 0 < b.y < SH + 50]

    def _shoot(self, player):
        cx = self.x + self.w//2
        cy = self.y + self.h//2
        angle = math.atan2(player.y - cy, player.x - cx)
        col   = (255, 0, 200) if self.enraged else ORANGE

        if self.pattern == 0:
            spd = 200
            self.bullets.append(Bullet(cx, cy,
                math.cos(angle)*spd, math.sin(angle)*spd,
                dmg=1, color=col, w=10, h=10, life=3, btype='normal'))

        elif self.pattern == 1:
            for i in range(-1, 2):
                a = angle + i * 0.22
                self.bullets.append(Bullet(cx, cy,
                    math.cos(a)*260, math.sin(a)*260,
                    dmg=1, color=col, w=8, h=8, life=2.5, btype='normal'))

        elif self.pattern == 2:
            for i in range(6):
                a = (math.pi*2/6)*i
                self.bullets.append(Bullet(cx, cy,
                    math.cos(a)*170, math.sin(a)*170,
                    dmg=1, color=col, w=8, h=8, life=2.5, btype='normal'))

        else:
            spd = 420
            self.bullets.append(Bullet(cx, cy,
                math.cos(angle)*spd, math.sin(angle)*spd,
                dmg=1, color=col, w=12, h=12, life=2, btype='normal'))

    def take_hit(self, dmg, particles):
        self.hp     -= dmg
        self.pain_t  = 0.15
        particle_burst(particles, self.x + self.w//2, self.y + self.h//2,
                       (200, 0, 60), count=8)
        if self.hp <= 0:
            self.alive = False
            play_boss_death()
            particle_burst(particles, self.x + self.w//2, self.y + self.h//2,
                           (255, 50, 0), count=35, speed_range=(100, 400))
            return True
        return False

    def draw(self, surf, cam_x):
        if not self.alive:
            return
        rx = int(self.x - cam_x)
        ry = int(self.y)
        pulse = 0.8 + 0.2 * math.sin(self.anim_t * 6)
        col  = (120, 0, 100) if self.enraged else (80, 0, 60)
        col2 = (180, 0, 150) if self.enraged else (120, 0, 90)
        body = pygame.Rect(rx, ry, self.w, self.h)
        pygame.draw.rect(surf, col, body, border_radius=6)
        for i in range(4):
            seg = pygame.Rect(rx + 6, ry + 10 + i*22, self.w - 12, 16)
            pygame.draw.rect(surf, col2, seg, border_radius=3)
        if self.pain_t > 0 and int(self.pain_t * 20) % 2 == 0:
            s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            s.fill((255, 255, 255, 160))
            surf.blit(s, (rx, ry))
        eye_col = (255, 0, 200) if self.enraged else RED
        for ox2 in [12, self.w - 22]:
            pygame.draw.rect(surf, eye_col, (rx + ox2, ry + 14, 14, 10))
            gs = pygame.Surface((18, 14), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*eye_col, 100), gs.get_rect())
            surf.blit(gs, (rx + ox2 - 2, ry + 12))
        bar_w = int(self.w * (self.hp / self.max_hp))
        pygame.draw.rect(surf, DARK_GRAY, (rx, ry - 12, self.w, 6))
        hp_col = (255, 0, 200) if self.enraged else RED
        pygame.draw.rect(surf, hp_col, (rx, ry - 12, bar_w, 6))

# ══════════════════════════════════════════════════════════
#  PLAYER (Platformer)
# ══════════════════════════════════════════════════════════

class Player:
    SHOOT_RATES = {
        'PISTOL': 0.22, 'SHOTGUN': 0.45, 'ROCKET': 0.85,
        'FLAMETHROWER': 0.07, 'RAILGUN': 1.1, 'SCATTER': 0.28
    }

    def __init__(self, x, y):
        self.x, self.y     = float(x), float(y)
        self.w, self.h     = 24, 36
        self.vx, self.vy   = 0.0, 0.0
        self.on_ground     = False
        self.facing        = 1
        self.hp            = 3
        self.max_hp        = 3
        self.weapon        = 'PISTOL'
        self.ammo          = {
            'PISTOL': -1, 'SHOTGUN': 30, 'ROCKET': 10,
            'FLAMETHROWER': 60, 'RAILGUN': 15, 'SCATTER': 40
        }
        self.grenades      = 3
        self.bullets       = []
        self.grenade_list  = []
        self.invincible    = 0.0
        self.blink_v       = True
        self.blink_t       = 0.0
        self.shoot_t       = 0.0
        self.grenade_t     = 0.0
        self.dead          = False
        self.death_t       = 2.0
        self.anim_t        = 0.0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def _resolve(self, rect):
        er = self.get_rect()
        if not er.colliderect(rect):
            return
        ox = min(er.right - rect.left, rect.right - er.left)
        oy = min(er.bottom - rect.top, rect.bottom - er.top)
        if oy <= ox:
            if self.vy >= 0 and er.centery < rect.centery:
                self.y  = rect.top - self.h
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.y  = rect.bottom
                self.vy = 0
        else:
            if self.vx > 0:
                self.x = rect.left - self.w
            else:
                self.x = rect.right
            self.vx = 0

    def update(self, dt, keys, platforms, particles):
        if self.dead:
            self.death_t -= dt
            return
        self.anim_t += dt
        SPD = 210.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -SPD; self.facing = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = SPD;  self.facing = 1
        else:
            self.vx *= 0.75
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) \
                and self.on_ground:
            self.vy        = -490
            self.on_ground = False
        if not self.on_ground:
            self.vy += GRAVITY * dt
        self.vy  = min(self.vy, 900)
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.on_ground = False
        for pl in platforms:
            self._resolve(pl.rect)
        self.x = max(0, self.x)
        if self.y > SH + 200:
            self.hp = 0
            self.dead = True
        self.shoot_t = max(0.0, self.shoot_t - dt)
        if (keys[pygame.K_z] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) \
                and self.shoot_t <= 0:
            self._shoot(particles)
            self.shoot_t = self.SHOOT_RATES.get(self.weapon, 0.25)
        self.grenade_t = max(0.0, self.grenade_t - dt)
        if keys[pygame.K_x] and self.grenades > 0 and self.grenade_t <= 0:
            g = Grenade(self.x + self.w//2, self.y, self.facing * 320, -380)
            self.grenade_list.append(g)
            self.grenades    -= 1
            self.grenade_t    = 0.7
        if self.invincible > 0:
            self.invincible -= dt
            self.blink_t    += dt
            if self.blink_t >= 0.09:
                self.blink_v = not self.blink_v
                self.blink_t = 0.0
        else:
            self.blink_v = True
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.alive]

    def _shoot(self, particles):
        if self.weapon != 'PISTOL':
            if self.ammo.get(self.weapon, 0) <= 0:
                self.weapon = 'PISTOL'
                return
            self.ammo[self.weapon] -= 1
        bx = self.x + (self.w if self.facing > 0 else 0)
        by = self.y + self.h * 0.4
        w = self.weapon
        if w == 'PISTOL':
            play_pistol()
            self.bullets.append(Bullet(
                bx, by, self.facing*600, random.uniform(-30, 30),
                dmg=1, color=YELLOW, w=12, h=4, life=1.4, btype='normal'))
        elif w == 'SHOTGUN':
            play_shotgun()
            for i in range(6):
                ang = random.uniform(-0.2, 0.2)
                self.bullets.append(Bullet(
                    bx, by,
                    self.facing*600*math.cos(ang), 600*math.sin(ang)+random.uniform(-60, 60),
                    dmg=1, color=ORANGE, w=7, h=4, life=0.35, btype='normal'))
        elif w == 'ROCKET':
            play_rocket_launch()
            self.bullets.append(Bullet(
                bx, by, self.facing*420, 0,
                dmg=4, color=RED, w=18, h=8, life=2.2, btype='rocket'))
        elif w == 'FLAMETHROWER':
            play_flamethrower()
            for _ in range(4):
                ang = random.uniform(-0.25, 0.25)
                spd = random.uniform(180, 320)
                c   = (255, random.randint(60, 140), 0)
                self.bullets.append(Bullet(
                    bx + random.uniform(-4, 4), by + random.uniform(-6, 6),
                    self.facing*spd*math.cos(ang), spd*math.sin(ang),
                    dmg=1, color=c, w=16, h=16, life=random.uniform(0.3, 0.55), btype='flame'))
        elif w == 'RAILGUN':
            play_laser()
            self.bullets.append(Bullet(
                bx, by, self.facing*1300, 0,
                dmg=9999, color=CYAN, w=28, h=5, life=0.45, btype='rail'))
        elif w == 'SCATTER':
            play_scatter()
            for i in range(5):
                vy_val = (i - 2) * 110
                self.bullets.append(Bullet(
                    bx, by, self.facing*500, vy_val,
                    dmg=1, color=GREEN, w=7, h=5, life=0.7, btype='normal'))

    def take_damage(self, dmg, particles):
        if self.invincible > 0 or self.dead:
            return
        self.hp         -= dmg
        self.invincible  = 1.6
        self.blink_v     = True
        self.blink_t     = 0.0
        particle_burst(particles, self.x + self.w//2, self.y + self.h//2, RED, count=10)
        if self.hp <= 0:
            self.dead   = True
            self.death_t = 2.0
            play_player_death()
            particle_burst(particles, self.x + self.w//2, self.y + self.h//2,
                           RED, count=30, speed_range=(100, 400))
        else:
            play_player_damaged()

    def draw(self, surf, cam_x):
        if not self.blink_v:
            return
        rx = int(self.x - cam_x)
        ry = int(self.y)
        leg_anim = int(self.anim_t * 12) % 2 if abs(self.vx) > 10 else 0
        leg_col  = (50, 70, 140)
        pygame.draw.rect(surf, leg_col,
                         (rx + (2 if leg_anim else 10), ry + self.h - 10, 8, 10))
        pygame.draw.rect(surf, leg_col,
                         (rx + (10 if leg_anim else 2), ry + self.h - 10, 8, 10))
        pygame.draw.rect(surf, (80, 120, 200),
                         (rx, ry + 8, self.w, self.h - 18), border_radius=3)
        pygame.draw.rect(surf, (60, 100, 180),
                         (rx + 2, ry + 10, self.w - 4, 14), border_radius=2)
        pygame.draw.rect(surf, (100, 150, 220),
                         (rx + 3, ry - 2, self.w - 6, 14), border_radius=4)
        visor_x = rx + (self.w - 12 if self.facing > 0 else 2)
        pygame.draw.rect(surf, CYAN, (visor_x, ry + 1, 10, 7), border_radius=2)
        gs = pygame.Surface((14, 11), pygame.SRCALPHA)
        pygame.draw.rect(gs, (0, 255, 255, 80), gs.get_rect())
        surf.blit(gs, (visor_x - 2, ry - 1))
        gun_x = rx + (self.w if self.facing > 0 else -14)
        pygame.draw.rect(surf, GRAY, (gun_x, ry + 12, 14 * self.facing, 5))
        wc = WEAPON_COLORS.get(self.weapon, YELLOW)
        pygame.draw.rect(surf, wc, (gun_x, ry + 11, 6, 3))

    def draw_hud(self, surf, world_w, cam_x):
        for i in range(self.max_hp):
            col = RED if i < self.hp else DARK_GRAY
            hx  = 14 + i * 26
            pygame.draw.polygon(surf, col, [
                (hx+10, 8), (hx+18, 16), (hx+10, 22), (hx+2, 16)
            ])
        wc   = WEAPON_COLORS.get(self.weapon, YELLOW)
        ammo = 'INF' if self.ammo.get(self.weapon, -1) == -1 \
               else str(self.ammo.get(self.weapon, 0))
        draw_text(surf, f"{self.weapon}  {ammo}", FONT_SM, wc, 14, 28)
        draw_text(surf, "GRANAT: " + ("O" * self.grenades), FONT_XS, (100, 200, 50), 14, SH - 22)
        map_w, map_h = 160, 12
        map_x, map_y = SW - map_w - 10, SH - map_h - 8
        pygame.draw.rect(surf, (20, 20, 30), (map_x, map_y, map_w, map_h))
        pygame.draw.rect(surf, GRAY,         (map_x, map_y, map_w, map_h), 1)
        px2 = map_x + int((self.x / world_w) * map_w)
        pygame.draw.rect(surf, CYAN, (px2 - 2, map_y + 2, 4, map_h - 4))
        draw_text(surf, "MAP", FONT_XS, GRAY, map_x, map_y - 14)

# ══════════════════════════════════════════════════════════
#  STORY TEXT DISPLAYER
# ══════════════════════════════════════════════════════════

class StoryDisplay:
    def __init__(self):
        self.lines   = []
        self.timer   = 0.0
        self.active  = False

    def show(self, lines, duration=5.0):
        self.lines   = lines
        self.timer   = duration
        self.active  = True

    def update(self, dt):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False

    def draw(self, surf):
        if not self.active:
            return
        alpha = min(255, int(255 * min(1.0, self.timer / 0.5)))
        box_w, box_h = 700, len(self.lines) * 22 + 20
        bx = (SW - box_w) // 2
        by = SH - box_h - 15
        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, int(200 * (alpha/255))))
        surf.blit(bg, (bx, by))
        pygame.draw.rect(surf, (80, 0, 0), (bx, by, box_w, box_h), 1)
        for i, line in enumerate(self.lines):
            t = FONT_XS.render(line, True, (200, 200, 200))
            t.set_alpha(alpha)
            surf.blit(t, (bx + 10, by + 10 + i * 22))

# ══════════════════════════════════════════════════════════
#  PLATFORMER LEVEL
# ══════════════════════════════════════════════════════════

class PlatformerLevel:
    def __init__(self, level_num):
        self.level_num  = level_num
        cfg             = LEVEL_CFG[level_num]
        self.cfg        = cfg
        self.world_w    = cfg['world_w']
        self.platforms  = []
        self.pickups    = []
        self.enemies    = []
        self.boss       = None
        self._generate()

    def _generate(self):
        cfg = self.cfg
        ww  = self.world_w
        gh  = SH - 60
        self.platforms.append(Platform(0, gh, ww, 60, 'ground'))
        px = 280
        while px < ww - 400:
            pw = int(80 + random.random() * 130)
            py = gh - int(90 + random.random() * 170)
            self.platforms.append(Platform(px, py, pw, 18, 'platform'))
            if random.random() > 0.55:
                self.platforms.append(Platform(
                    px + 70, py - int(60 + random.random()*70),
                    int(60 + random.random()*70), 18, 'platform'))
            px += int(130 + random.random() * 150)
        wlist = ['SHOTGUN','ROCKET','FLAMETHROWER','RAILGUN','SCATTER']
        for i in range(3):
            wx = int(400 + i * (ww // 4) + random.uniform(-60, 60))
            self.pickups.append(Pickup(wx, gh - 60, 'weapon', random.choice(wlist)))
        for _ in range(5):
            hx = int(200 + random.random() * (ww - 400))
            self.pickups.append(Pickup(hx, gh - 60, 'health'))
        for _ in range(3):
            gx = int(300 + random.random() * (ww - 500))
            self.pickups.append(Pickup(gx, gh - 60, 'grenade'))
        etype = self.cfg['enemy_type']
        SAFE_ZONE = 500
        for i in range(self.cfg['enemy_count']):
            ex = int(SAFE_ZONE + (i / self.cfg['enemy_count']) * (ww - SAFE_ZONE - 400)
                     + random.uniform(-60, 60))
            ex = max(SAFE_ZONE, ex)   # pastikan tidak lebih kecil dari safe zone
            self.enemies.append(Enemy(ex, gh - 45, etype, self.level_num))
        if self.cfg['boss']:
            bx = ww - 350
            self.boss = Boss(bx, gh - 110, self.cfg['boss'], self.level_num)
        self.exit_rect = pygame.Rect(ww - 180, gh - 80, 55, 80)

# ══════════════════════════════════════════════════════════
#  PLATFORMER SCENE
# ══════════════════════════════════════════════════════════

class PlatformerScene:
    def __init__(self, level_num, carried_score=0):
        self.level_num    = level_num
        self.lv           = PlatformerLevel(level_num)
        self.player       = Player(100, SH - 200)
        self.camera_x     = 0.0
        self.particles    = []
        self.score        = carried_score
        self.story        = StoryDisplay()
        self.shake_t      = 0.0
        self.shake_amt    = 0
        self.done         = False
        self.dead         = False
        self.boss_hud_shown = False
        self.bg_stars     = [(random.randint(0, self.lv.world_w),
                              random.randint(0, SH - 80),
                              random.randint(1, 3), random.uniform(0.2, 1.0))
                             for _ in range(200)]
        self.fog = [{'x': random.uniform(0, SW),
                     'y': SH - 60 - random.uniform(0, 120),
                     'spd': random.uniform(8, 25),
                     'size': random.randint(25, 90),
                     'alpha': random.uniform(0.04, 0.14)}
                    for _ in range(22)]
        self.between_sign_t = 0.0

    def screen_shake(self, amount, duration=0.25):
        self.shake_t   = duration
        self.shake_amt = amount

    def _explode_rocket(self, bx, by):
        self.screen_shake(8, 0.35)
        play_rocket_explode()
        particle_burst(self.particles, bx, by, ORANGE, 25, (100, 350))
        particle_burst(self.particles, bx, by, RED,    12, (50, 200))
        for e in self.lv.enemies:
            d = math.hypot(e.x - bx, e.y - by)
            if d < 130 and e.alive:
                e.take_hit(3, self.particles)
                self.score += 50 if not e.alive else 0
        if self.lv.boss and self.lv.boss.alive:
            d = math.hypot(self.lv.boss.x - bx, self.lv.boss.y - by)
            if d < 130:
                killed = self.lv.boss.take_hit(3, self.particles)
                if killed:
                    self.score += self.lv.boss.score_value

    def _explode_grenade(self, gx, gy):
        self.screen_shake(10, 0.4)
        play_rocket_explode()
        particle_burst(self.particles, gx, gy, ORANGE, 30, (100, 400))
        particle_burst(self.particles, gx, gy, YELLOW, 15, (60, 250))
        for e in self.lv.enemies:
            d = math.hypot(e.x - gx, e.y - gy)
            if d < 140 and e.alive:
                killed = e.take_hit(5, self.particles)
                if killed:
                    self.score += e.score_value
        if self.lv.boss and self.lv.boss.alive:
            d = math.hypot(self.lv.boss.x - gx, self.lv.boss.y - gy)
            if d < 140:
                killed = self.lv.boss.take_hit(5, self.particles)
                if killed:
                    self.score += self.lv.boss.score_value

    def update(self, dt, keys):
        self.story.update(dt)
        if self.shake_t > 0:
            self.shake_t -= dt
        p = self.player
        p.update(dt, keys, self.lv.platforms, self.particles)
        if p.dead:
            self.dead = True
            return
        target_cx = p.x - SW // 3
        self.camera_x = clamp(
            self.camera_x + (target_cx - self.camera_x) * min(1.0, dt*8),
            0, self.lv.world_w - SW
        )
        for g in p.grenade_list:
            g.update(dt, self.lv.platforms)
        for g in p.grenade_list:
            if not g.alive:
                self._explode_grenade(g.x, g.y)
        p.grenade_list = [g for g in p.grenade_list if g.alive]
        for b in p.bullets:
            if not b.alive:
                continue
            br = b.get_rect().move(-int(self.camera_x), 0)
            for e in self.lv.enemies:
                if not e.alive:
                    continue
                er = e.get_rect().move(-int(self.camera_x), 0)
                if br.colliderect(er):
                    b.alive = False
                    if b.btype == 'rocket':
                        self._explode_rocket(b.x, b.y)
                    else:
                        killed = e.take_hit(b.dmg, self.particles)
                        if killed:
                            self.score += e.score_value
                    break
            if b.alive and self.lv.boss and self.lv.boss.alive:
                bsr = self.lv.boss.get_rect().move(-int(self.camera_x), 0)
                if br.colliderect(bsr):
                    b.alive = False
                    if b.btype == 'rocket':
                        self._explode_rocket(b.x, b.y)
                    else:
                        killed = self.lv.boss.take_hit(b.dmg, self.particles)
                        if killed:
                            self.score     += self.lv.boss.score_value
                            self.screen_shake(12, 0.6)
        for e in [*self.lv.enemies, self.lv.boss]:
            if not e or not e.alive:
                continue
            pr = p.get_rect().move(-int(self.camera_x), 0)
            for b in e.bullets:
                br = b.get_rect().move(-int(self.camera_x), 0)
                if b.alive and br.colliderect(pr):
                    b.alive = False
                    p.take_damage(1, self.particles)
                    self.screen_shake(5, 0.2)
        pr2 = p.get_rect().move(-int(self.camera_x), 0)
        for e in self.lv.enemies:
            if not e.alive:
                continue
            er2 = e.get_rect().move(-int(self.camera_x), 0)
            if e.aggro and pr2.colliderect(er2):
                p.take_damage(1, self.particles)
                self.screen_shake(4, 0.2)
        for e in self.lv.enemies:
            e.update(dt, p, self.lv.platforms, self.particles, self.camera_x)
        if self.lv.boss and self.lv.boss.alive:
            self.lv.boss.update(dt, p, self.lv.platforms, self.particles, self.camera_x)
            if not self.boss_hud_shown:
                self.boss_hud_shown = True
                self.story.show([f"!! {self.lv.boss.name} !!",
                                 "Boss muncul! Habisi dia!"])
        pr3 = p.get_rect()
        for pk in self.lv.pickups:
            if pk.collected:
                continue
            pkr = pygame.Rect(pk.x - 18, pk.y - 20, 36, 40)
            if pr3.colliderect(pkr):
                pk.collected = True
                if pk.ptype == 'weapon':
                    p.weapon = pk.weapon
                    p.ammo[pk.weapon] = p.ammo.get(pk.weapon, 0) + 30
                    self.story.show([f"SENJATA: {pk.weapon}!", "+30 ammo"])
                elif pk.ptype == 'health':
                    p.hp = min(p.max_hp, p.hp + 1)
                    particle_burst(self.particles, int(pk.x), int(pk.y), GREEN, count=10)
                elif pk.ptype == 'grenade':
                    p.grenades = min(5, p.grenades + 2)
                    self.story.show(["+2 Granat!"])
        for pt in self.particles:
            pt['x']    += pt['vx'] * dt
            pt['y']    += pt['vy'] * dt
            pt['vy']   += 180 * dt
            pt['life'] -= dt
        self.particles = [pt for pt in self.particles if pt['life'] > 0]
        for f in self.fog:
            f['x'] += f['spd'] * dt
            if f['x'] > self.camera_x + SW + f['size']:
                f['x'] = self.camera_x - f['size']
        for pk in self.lv.pickups:
            pk.update(dt)
        pr4 = p.get_rect()
        boss_dead = (self.lv.boss is None or not self.lv.boss.alive)
        if boss_dead and pr4.colliderect(self.lv.exit_rect):
            self.done = True
        if self.lv.boss and self.lv.boss.alive and not boss_dead:
            ex = self.lv.exit_rect
            dist_to_exit = abs(p.x - ex.centerx)
            if dist_to_exit < 300:
                self.story.show(["!! Kalahkan BOSS terlebih dahulu!"])

    def draw(self, surf):
        ox, oy = shake_offset(self.shake_t, self.shake_amt)
        cfg = self.lv.cfg
        bg_img = BG_IMAGES.get(self.level_num)
        if bg_img:
            surf.blit(bg_img, (ox, oy))
            dim = pygame.Surface((SW, SH), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 80))
            surf.blit(dim, (ox, oy))
        else:
            bg_surf = pygame.Surface((SW, SH))
            for y in range(SH):
                t   = y / SH
                col = tuple(int(cfg['bg_top'][i] + (cfg['bg_bot'][i]-cfg['bg_top'][i])*t)
                            for i in range(3))
                pygame.draw.line(bg_surf, col, (0, y), (SW, y))
            surf.blit(bg_surf, (ox, oy))
        if cfg.get('ambience') and self.level_num in (1, 4, 5):
            for sx, sy, ss, sa in self.bg_stars:
                screen_x = int(sx - self.camera_x * 0.15) % SW
                if sa > 0.3:
                    c = int(sa * 200)
                    pygame.draw.rect(surf, (c,c,c), (screen_x+ox, sy+oy, ss, ss))
        cx = int(self.camera_x)
        if not BG_IMAGES.get(self.level_num):
            rock_col = cfg['rock']
            for i in range(12):
                rx = int((i * 210 - cx * 0.35) % (self.lv.world_w + SW)) - 40
                rh = int(70 + (i * 73) % 130)
                pts = [(rx+ox, SH-60+oy), (rx+70+ox, SH-60-rh+oy), (rx+140+ox, SH-60+oy)]
                pygame.draw.polygon(surf, rock_col, pts)
        fog_col = cfg['fog']
        for f in self.fog:
            fx    = int(f['x'] - cx) + ox
            alpha = int(f['alpha'] * 255 * (0.6 + 0.4*math.sin(f['x']*0.01)))
            fs    = pygame.Surface((int(f['size']*2), int(f['size']*2)), pygame.SRCALPHA)
            pygame.draw.ellipse(fs,
                                (fog_col[0], fog_col[1], fog_col[2], alpha),
                                fs.get_rect())
            surf.blit(fs, (fx - int(f['size']), int(f['y']) + oy))
        for pl in self.lv.platforms:
            pl.draw(surf, cx - ox, cfg)
        for i in range(0, self.lv.world_w, 28):
            if random.Random(i).random() > 0.97:
                sx = i - cx + ox
                if -10 < sx < SW + 10:
                    pygame.draw.polygon(surf, (100, 0, 0),
                        [(sx, SH-60+oy), (sx+8, SH-60-18+oy), (sx+16, SH-60+oy)])
        for pk in self.lv.pickups:
            pk.draw(surf, cx - ox)
        ex  = self.lv.exit_rect
        exr = pygame.Rect(ex.x - cx + ox, ex.y + oy, ex.w, ex.h)
        boss_dead = (self.lv.boss is None or not self.lv.boss.alive)
        ecol = (0, 255, 100) if boss_dead else (60, 60, 60)
        if self.level_num == 5:
            pygame.draw.polygon(surf, ecol,
                [(exr.x+exr.w//2, exr.y),
                 (exr.x+exr.w, exr.y+exr.h*0.6),
                 (exr.x+exr.w*0.7, exr.y+exr.h),
                 (exr.x+exr.w*0.3, exr.y+exr.h),
                 (exr.x, exr.y+exr.h*0.6)])
            t = FONT_XS.render("SHIP" if boss_dead else "BOSS!", True, WHITE)
            surf.blit(t, (exr.x + exr.w//2 - t.get_width()//2, exr.y + 28))
            if boss_dead:
                gs = pygame.Surface((20, 10), pygame.SRCALPHA)
                pygame.draw.ellipse(gs, (0, 200, 255, 120), gs.get_rect())
                surf.blit(gs, (exr.x+exr.w//2-10, exr.y+exr.h-5))
        else:
            pygame.draw.rect(surf, ecol, exr, border_radius=4)
            t = FONT_XS.render("EXIT" if boss_dead else "BOSS!", True, WHITE)
            surf.blit(t, (exr.x + exr.w//2 - t.get_width()//2, exr.y + 10))
        for e in self.lv.enemies:
            if e.alive:
                e.draw(surf, cx - ox)
                for b in e.bullets:
                    b.draw(surf, cx - ox)
        if self.lv.boss and self.lv.boss.alive:
            self.lv.boss.draw(surf, cx - ox)
            for b in self.lv.boss.bullets:
                b.draw(surf, cx - ox)
            bw  = 380
            bx2 = (SW - bw) // 2
            by2 = SH - 36
            pygame.draw.rect(surf, (20, 10, 20), (bx2 - 4, by2 - 22, bw+8, 40))
            ratio = self.lv.boss.hp / self.lv.boss.max_hp
            hcol  = (255, 0, 200) if self.lv.boss.enraged else RED
            pygame.draw.rect(surf, hcol, (bx2, by2, int(bw*ratio), 14))
            pygame.draw.rect(surf, GRAY, (bx2, by2, bw, 14), 1)
            ename = ("!! " if self.lv.boss.enraged else "") + \
                    self.lv.boss.name + \
                    (" -- ENRAGED!" if self.lv.boss.enraged else "")
            draw_text(surf, ename, FONT_XS,
                      (255,0,200) if self.lv.boss.enraged else (255,80,80),
                      bx2, by2 - 18)
        self.player.draw(surf, cx - ox)
        for b in self.player.bullets:
            b.draw(surf, cx - ox)
        for g in self.player.grenade_list:
            g.draw(surf, cx - ox)
        for pt in self.particles:
            alpha = min(1.0, pt['life'])
            r, g2, b2 = pt['color']
            s = pygame.Surface((pt['size']*2, pt['size']*2), pygame.SRCALPHA)
            pygame.draw.rect(s,
                             (r, g2, b2, int(alpha*220)),
                             s.get_rect())
            surf.blit(s, (int(pt['x'] - cx + ox) - pt['size'],
                          int(pt['y'] + oy) - pt['size']))
        self.player.draw_hud(surf, self.lv.world_w, cx)
        draw_text(surf, f"SCORE  {self.score:06d}", FONT_SM, WHITE, SW - 210, 8)
        draw_text(surf, cfg['name'], FONT_XS, LIGHT_GRAY, SW//2, 8, center=True)
        self.story.draw(surf)
        draw_vignette(surf)
        draw_scanlines(surf)
        if self.player.hp == 1:
            pulse = 0.25 + 0.25 * math.sin(pygame.time.get_ticks() * 0.003)
            bv    = pygame.Surface((SW, SH), pygame.SRCALPHA)
            for i in range(60):
                a = int(i * 3 * pulse)
                rr = max(0, 60 - i)
                pygame.draw.rect(bv, (120, 0, 0, a), (rr, rr, SW-2*rr, SH-2*rr), 1)
            surf.blit(bv, (0, 0))

# ══════════════════════════════════════════════════════════
#  SPACE ENEMY
# ══════════════════════════════════════════════════════════

class SpaceEnemy:
    def __init__(self, x, y, wave):
        self.x, self.y   = float(x), float(y)
        self.is_elite     = (wave >= 3 and random.random() < 0.25)
        self.w            = 44 if self.is_elite else 36
        self.h            = 38 if self.is_elite else 30
        self.hp = self.max_hp = 1 + (wave-1)//3 + (4 if self.is_elite else 0)
        self.spd          = 80 + wave * 15
        self.amplitude    = random.uniform(30, 80)
        self.freq         = random.uniform(1.4, 3.0)
        self.origin_y     = y
        self.t            = 0.0
        self.alive        = True
        self.shoot_t      = random.uniform(0.8, 2.2)
        self.bullets      = []
        self.score_val    = 100 if self.is_elite else 30
        self.pain_t       = 0.0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, player):
        self.t   += dt
        self.x   -= self.spd * dt
        self.y    = self.origin_y + self.amplitude * math.sin(self.freq * self.t)
        self.pain_t = max(0, self.pain_t - dt)
        if self.x < -self.w - 10:
            self.alive = False
            return
        self.shoot_t -= dt
        if self.shoot_t <= 0:
            self.shoot_t = 1.4 + random.uniform(-0.3, 0.6)
            cx  = self.x
            cy  = self.y + self.h//2
            ang = math.atan2(player.y + player.h//2 - cy,
                             player.x + player.w//2 - cx)
            spd = 200 + random.uniform(0, 80)
            cnt = 3 if self.is_elite else 1
            for i in range(cnt):
                a = ang + (i - cnt//2) * 0.18
                self.bullets.append(Bullet(
                    cx, cy,
                    math.cos(a)*spd, math.sin(a)*spd,
                    dmg=1, color=RED, w=8, h=8, life=3.0))
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.alive and 0 < b.y < SH]

    def draw(self, surf):
        if not self.alive:
            return
        rx, ry = int(self.x), int(self.y)
        col    = (100, 0, 160) if self.is_elite else (140, 0, 0)
        if self.pain_t > 0 and int(self.pain_t*20)%2==0:
            col = WHITE
        cx2, cy2 = rx + self.w//2, ry + self.h//2
        pts = [(rx + self.w//2, ry),
               (rx + self.w, ry + self.h//2),
               (rx + self.w//2, ry + self.h),
               (rx, ry + self.h//2)]
        pygame.draw.polygon(surf, col, pts)
        ic = tuple(min(255, c+50) for c in col)
        pts2 = [(cx2, ry+8),(rx+self.w-8,cy2),(cx2,ry+self.h-8),(rx+8,cy2)]
        pygame.draw.polygon(surf, ic, pts2)
        pygame.draw.circle(surf, RED, (cx2, cy2), 6)
        pygame.draw.circle(surf, (255,80,80), (cx2, cy2), 3)
        if self.is_elite:
            bw = int(self.w * (self.hp / self.max_hp))
            pygame.draw.rect(surf, DARK_GRAY, (rx, ry-7, self.w, 4))
            pygame.draw.rect(surf, RED,       (rx, ry-7, bw,    4))
        for b in self.bullets:
            b.draw(surf)

# ══════════════════════════════════════════════════════════
#  MEGA BOSS (Space)
# ══════════════════════════════════════════════════════════

class MegaBoss:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.w, self.h = 120, 110
        self.hp = self.max_hp = 80
        self.alive    = True
        self.enraged  = False
        self.bullets  = []
        self.shoot_t  = 0.5
        self.t        = 0.0
        self.pattern  = 0
        self.target_x = SW - 230.0
        self.pain_t   = 0.0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, player):
        self.t += dt
        self.pain_t = max(0, self.pain_t - dt)
        if self.x > self.target_x:
            self.x -= 90 * dt
        self.y = SH//2 - self.h//2 + math.sin(self.t * 0.55) * (SH//3)
        self.y = clamp(self.y, 20, SH - self.h - 20)
        if self.hp < self.max_hp * 0.4 and not self.enraged:
            self.enraged = True
        self.shoot_t -= dt
        if self.shoot_t <= 0:
            rate = 0.28 if self.enraged else 0.55
            self.shoot_t = rate
            self._shoot(player)
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets
                        if b.alive and -20<b.x<SW+20 and -20<b.y<SH+20]

    def _shoot(self, player):
        cx = self.x
        cy = self.y + self.h//2
        ang = math.atan2(player.y + player.h//2 - cy,
                         player.x + player.w//2 - cx)
        col = (255, 0, 220) if self.enraged else ORANGE
        self.pattern = (self.pattern + 1) % 4
        if self.pattern == 0:
            self.bullets.append(Bullet(cx,cy, math.cos(ang)*380,math.sin(ang)*380,
                dmg=1,color=col,w=11,h=11,life=3))
        elif self.pattern == 1:
            for i in range(-2,3):
                a = ang + i*0.17
                self.bullets.append(Bullet(cx,cy, math.cos(a)*300,math.sin(a)*300,
                    dmg=1,color=col,w=9,h=9,life=2.5))
        elif self.pattern == 2:
            for i in range(8):
                a = (math.pi*2/8)*i + self.t
                self.bullets.append(Bullet(cx,cy, math.cos(a)*220,math.sin(a)*220,
                    dmg=1,color=col,w=9,h=9,life=2))
        else:
            for i in range(3):
                self.bullets.append(Bullet(cx, cy + (i-1)*22,
                    -310, (i-1)*90,
                    dmg=1,color=col,w=10,h=10,life=2.5))

    def draw(self, surf):
        if not self.alive:
            return
        cx2 = int(self.x + self.w//2)
        cy2 = int(self.y + self.h//2)
        r   = self.w // 2
        pulse = 0.85 + 0.15 * math.sin(self.t * 7)
        col = (120, 0, 120) if self.enraged else (60, 0, 90)
        if self.pain_t > 0 and int(self.pain_t*20)%2==0:
            col = WHITE
        pts = []
        for i in range(6):
            a = math.radians(60*i - 30)
            pts.append((cx2 + r*math.cos(a), cy2 + r*math.sin(a)))
        pygame.draw.polygon(surf, col, pts)
        edge_col = (255,0,255) if self.enraged else WHITE
        pygame.draw.polygon(surf, edge_col, pts, 3)
        inner_pts = []
        for i in range(6):
            a = math.radians(60*i - 30 + self.t*40)
            inner_pts.append((cx2 + (r*0.6)*math.cos(a),
                              cy2 + (r*0.6)*math.sin(a)))
        pygame.draw.polygon(surf, tuple(min(255,c+80) for c in col), inner_pts, 2)
        core_r = int(22 * pulse)
        pygame.draw.circle(surf, CYAN,  (cx2, cy2), core_r)
        pygame.draw.circle(surf, WHITE, (cx2, cy2), int(core_r * 0.45))
        for b in self.bullets:
            b.draw(surf)

# ══════════════════════════════════════════════════════════
#  SPACE PLAYER
# ══════════════════════════════════════════════════════════

class SpacePlayer:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.w, self.h = 42, 38
        self.hp = self.max_hp = 5
        self.bullets    = []
        self.shoot_t    = 0.0
        self.invincible = 0.0
        self.blink_v    = True
        self.blink_t    = 0.0
        self.power_lvl  = 1
        self.power_t    = 0.0
        self.dead       = False
        self.t          = 0.0

    def update(self, dt, keys):
        if self.dead:
            return
        self.t += dt
        spd = 290.0
        vx, vy = 0.0, 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: vx = -spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: vx =  spd
        if keys[pygame.K_UP]    or keys[pygame.K_w]: vy = -spd
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: vy =  spd
        self.x = clamp(self.x + vx*dt, 0, SW - self.w)
        self.y = clamp(self.y + vy*dt, 0, SH - self.h)
        self.shoot_t = max(0.0, self.shoot_t - dt)
        if (keys[pygame.K_SPACE] or keys[pygame.K_z]) and self.shoot_t <= 0:
            self._shoot()
            self.shoot_t = 0.07 if self.power_lvl == 2 else 0.17
        if self.invincible > 0:
            self.invincible -= dt
            self.blink_t    += dt
            if self.blink_t >= 0.08:
                self.blink_v = not self.blink_v
                self.blink_t = 0.0
        else:
            self.blink_v = True
        if self.power_t > 0:
            self.power_t -= dt
            if self.power_t <= 0:
                self.power_lvl = 1
        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if b.alive]

    def _shoot(self):
        bx = self.x + self.w
        cy = self.y + self.h//2 - 2
        if self.power_lvl == 1:
            play_space_player_shoot()
            self.bullets.append(Bullet(bx,cy, 640,0, dmg=1,color=CYAN, w=14,h=4))
        else:
            play_space_spreadshot()
            self.bullets.append(Bullet(bx,cy-10, 620,-18, dmg=1,color=CYAN, w=11,h=3))
            self.bullets.append(Bullet(bx,cy,    640,  0, dmg=1,color=YELLOW,w=14,h=4))
            self.bullets.append(Bullet(bx,cy+10, 620, 18, dmg=1,color=CYAN, w=11,h=3))

    def take_damage(self, particles):
        if self.invincible > 0 or self.dead:
            return
        self.hp -= 1
        self.invincible = 2.0
        particle_burst(particles, int(self.x+self.w//2), int(self.y+self.h//2),
                       RED, count=12)
        if self.hp <= 0:
            self.dead = True
            play_player_death()
            particle_burst(particles, int(self.x+self.w//2), int(self.y+self.h//2),
                           CYAN, count=30, speed_range=(100,400))
        else:
            play_player_damaged()

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, surf):
        if not self.blink_v:
            return
        rx, ry = int(self.x), int(self.y)
        w, h   = self.w, self.h

        if SPACE_PLAYER_SPRITE:
            surf.blit(SPACE_PLAYER_SPRITE, (rx, ry))
            ecol    = YELLOW if self.power_lvl == 2 else ORANGE
            flicker = 5 + int(3 * math.sin(self.t * 20))
            pygame.draw.circle(surf, ecol, (rx + 4, ry + h//2), flicker)
        else:
            # Fallback: original drawn shapes
            pygame.draw.polygon(surf, (30, 60, 180), [
                (rx+w, ry+h//2),
                (rx,   ry+h),
                (rx+w//2, ry+h-8),
                (rx,   ry),
            ])
            pygame.draw.rect(surf, CYAN, (rx+w//2, ry+h//2-5, w//2-4, 10), border_radius=3)
            ecol    = YELLOW if self.power_lvl == 2 else ORANGE
            flicker = 5 + int(3 * math.sin(self.t * 20))
            pygame.draw.circle(surf, ecol, (rx + 8, ry + h//2), flicker)

        # HUD hearts (unchanged)
        for i in range(self.max_hp):
            col = RED if i < self.hp else DARK_GRAY
            hx  = 14 + i * 22
            pygame.draw.polygon(surf, col, [(hx+8,8),(hx+16,16),(hx+8,22),(hx,16)])

# ══════════════════════════════════════════════════════════
#  SPACE SHOOTER SCENE
# ══════════════════════════════════════════════════════════

class SpaceShooterScene:
    def __init__(self, carry_score=0):
        self.player      = SpacePlayer(80, SH//2 - 20)
        self.enemies     = []
        self.powerups    = []
        self.particles   = []
        self.story       = StoryDisplay()
        self.score       = carry_score
        self.wave        = 1
        self.spawn_t     = 0.0
        self.spawn_int   = 1.2
        self.spawned     = 0
        self.per_wave    = 10
        self.between     = False
        self.wave_clr_t  = 0.0
        self.mega_boss   = None
        self.boss_spawned= False
        self.won         = False
        self.won_t       = 0.0
        self.shake_t     = 0.0
        self.shake_amt   = 0
        self.t           = 0.0
        self.stars       = [
            {'x': random.uniform(0, SW), 'y': random.uniform(0, SH),
             'spd': random.uniform(30, 160), 'sz': random.choice([1,1,1,2]),
             'br': random.randint(80, 255)}
            for _ in range(180)
        ]
        self.story.show([
            "Berhasil kabur dari planet neraka!",
            "Tapi armada alien mengejarmu di luar angkasa.",
            "Tembak semua yang menghalangi jalur pelarianmu!",
            "SPACE/Z = Tembak    WASD = Gerak"
        ], 6.0)

    def screen_shake(self, amt, dur=0.25):
        self.shake_t   = dur
        self.shake_amt = amt

    def update(self, dt, keys):
        self.t     += dt
        self.story.update(dt)
        if self.shake_t > 0:
            self.shake_t -= dt
        p = self.player
        p.update(dt, keys)
        if p.dead:
            return
        for s in self.stars:
            s['x'] -= s['spd'] * dt
            if s['x'] < 0:
                s['x'] = SW
                s['y'] = random.uniform(0, SH)
        if not self.between and not self.boss_spawned:
            self.spawn_t -= dt
            if self.spawn_t <= 0 and self.spawned < self.per_wave:
                y = random.uniform(30, SH - 30)
                self.enemies.append(SpaceEnemy(SW + 50, y, self.wave))
                self.spawned  += 1
                self.spawn_t   = self.spawn_int
            alive = [e for e in self.enemies if e.alive]
            if self.spawned >= self.per_wave and not alive:
                self.between    = True
                self.wave_clr_t = 2.5
        elif not self.boss_spawned:
            self.wave_clr_t -= dt
            if self.wave_clr_t <= 0:
                self.wave       += 1
                self.spawned     = 0
                self.per_wave    = 10 + self.wave * 2
                self.spawn_int   = max(0.4, 1.2 - self.wave*0.08)
                self.between     = False
                if self.wave % 5 == 0:
                    self.mega_boss   = MegaBoss(SW + 160, SH//2 - 55)
                    self.boss_spawned = True
                    self.story.show(["!! MEGA BOSS MUNCUL!!",
                                     "Armada terakhir -- hancurkan mereka!"])
        for e in self.enemies:
            if e.alive:
                e.update(dt, p)
            else:
                for b in e.bullets:
                    b.update(dt)
                e.bullets = [b for b in e.bullets if b.alive and 0 < b.y < SH]
        self.enemies = [e for e in self.enemies if e.alive or e.bullets]
        if self.mega_boss:
            if self.mega_boss.alive:
                self.mega_boss.update(dt, p)
            if not self.mega_boss.alive and not self.won:
                self.won   = True
                self.won_t = 3.5
                self.screen_shake(15, 1.0)
                self.story.show(["MEGA BOSS DIKALAHKAN!",
                                 "Kamu berhasil melarikan diri!",
                                 "SELAMAT -- KAMU MENANG!"], 6.0)
        if self.won:
            self.won_t -= dt
        pr = p.get_rect()
        for b in p.bullets:
            if not b.alive:
                continue
            br = b.get_rect()
            for e in self.enemies:
                if not e.alive:
                    continue
                if br.colliderect(e.get_rect()):
                    b.alive = False
                    e.hp   -= b.dmg
                    e.pain_t = 0.2
                    particle_burst(self.particles, int(e.x+e.w//2), int(e.y+e.h//2),
                                   (180,0,0), count=6)
                    if e.hp <= 0:
                        e.alive  = False
                        self.score += e.score_val
                        play_space_enemy_death()
                        particle_burst(self.particles, int(e.x+e.w//2), int(e.y+e.h//2),
                                       RED, count=15, speed_range=(80,300))
                        if random.random() < 0.25:
                            dx_to_player = p.x - e.x
                            dist = max(1, abs(dx_to_player))
                            # Kecepatan horizontal proporsional, max 160px/s ke kiri
                            vx_drop = clamp((dx_to_player / dist) * 120, -160, 160)
                            self.powerups.append({
                                'x': e.x, 'y': e.y,
                                'vx': vx_drop,
                                'vy': 50,
                                'kind': random.choice(['spread','heal']),
                                'life': 8.0, 'spin': 0.0
                            })
                    break
            if b.alive and self.mega_boss and self.mega_boss.alive:
                if br.colliderect(self.mega_boss.get_rect()):
                    b.alive             = False
                    self.mega_boss.hp  -= b.dmg
                    self.mega_boss.pain_t = 0.15
                    if self.mega_boss.hp <= 0:
                        self.mega_boss.alive = False
                        self.score          += 3000
                        play_space_megaboss_death()
                        self.screen_shake(18, 0.8)
                        particle_burst(self.particles,
                                       int(self.mega_boss.x + self.mega_boss.w//2),
                                       int(self.mega_boss.y + self.mega_boss.h//2),
                                       PURPLE, count=50, speed_range=(100,500))
        for e in [*self.enemies, self.mega_boss]:
            if not e:
                continue
            for b in e.bullets:
                if b.alive and b.get_rect().colliderect(pr):
                    b.alive = False
                    p.take_damage(self.particles)
                    self.screen_shake(5, 0.2)
            if hasattr(e, 'alive') and e.alive and e.get_rect().colliderect(pr):
                e.alive = False
                p.take_damage(self.particles)
                self.screen_shake(5, 0.2)
        for pu in self.powerups:
            pu['x']   += pu.get('vx', 0) * dt
            pu['y']   += pu['vy'] * dt
            pu['spin']+= dt * 90
            pu['life']-= dt
            pur = pygame.Rect(int(pu['x']), int(pu['y']), 22, 22)
            if pur.colliderect(pr):
                pu['life'] = -1
                if pu['kind'] == 'spread':
                    p.power_lvl = 2
                    p.power_t   = 8.0
                    particle_burst(self.particles, int(pu['x']), int(pu['y']),
                                   YELLOW, count=12)
                elif p.hp < p.max_hp:
                    p.hp += 1
                    particle_burst(self.particles, int(pu['x']), int(pu['y']),
                                   GREEN, count=12)
        self.powerups = [pu for pu in self.powerups if pu['life'] > 0]
        for pt in self.particles:
            pt['x']   += pt['vx'] * dt
            pt['y']   += pt['vy'] * dt
            pt['life']-= dt
        self.particles = [pt for pt in self.particles if pt['life'] > 0]

    def draw(self, surf):
        ox, oy = shake_offset(self.shake_t, self.shake_amt)
        surf.fill(DARK_BLUE)
        nb = pygame.Surface((SW, SH), pygame.SRCALPHA)
        cx2 = SW//2 + int(math.sin(self.t*0.25)*120)
        cy2 = SH//2 + int(math.cos(self.t*0.18)*70)
        for i in range(5):
            r2 = 180 - i*30
            nb.fill((0,0,0,0))
            pygame.draw.ellipse(nb, (30, 0, 50, 18+i*6),
                                (cx2 - r2, cy2 - r2//2, r2*2, r2))
            surf.blit(nb, (ox, oy))
        for s in self.stars:
            c   = s['br']
            px2 = int(s['x']) + ox
            py2 = int(s['y']) + oy
            if 0 <= px2 < SW and 0 <= py2 < SH:
                pygame.draw.rect(surf, (c,c,c), (px2, py2, s['sz'], s['sz']))
        for e in self.enemies:
            if e.alive:
                e.draw(surf)
            for b in e.bullets:
                b.draw(surf)
        if self.mega_boss and self.mega_boss.alive:
            self.mega_boss.draw(surf)
            for b in self.mega_boss.bullets:
                b.draw(surf)
            bw  = 380
            bx3 = (SW - bw)//2
            by3 = SH - 36
            ratio = self.mega_boss.hp / self.mega_boss.max_hp
            pygame.draw.rect(surf, (20,10,20), (bx3-4, by3-22, bw+8, 40))
            hcol2 = (255,0,220) if self.mega_boss.enraged else RED
            pygame.draw.rect(surf, hcol2, (bx3, by3, int(bw*ratio), 14))
            pygame.draw.rect(surf, GRAY,   (bx3, by3, bw, 14), 1)
            lbl2 = "!! MEGA BOSS -- ENRAGED! !!" if self.mega_boss.enraged else "!! MEGA BOSS !!"
            draw_text(surf, lbl2, FONT_XS, hcol2, bx3, by3-18)
        for pu in self.powerups:
            cx3 = int(pu['x']) + 11
            cy3 = int(pu['y']) + 11
            col2 = YELLOW if pu['kind'] == 'spread' else GREEN
            pts  = []
            for i in range(8):
                a  = math.radians(pu['spin'] + i*45)
                rr = 11 if i%2==0 else 5
                pts.append((cx3 + rr*math.cos(a), cy3 + rr*math.sin(a)))
            pygame.draw.polygon(surf, col2, pts)
        self.player.draw(surf)
        for b in self.player.bullets:
            b.draw(surf)
        for pt in self.particles:
            a  = min(1.0, pt['life'])
            r2, g2, b2 = pt['color']
            sz = pt['size']
            ps2 = pygame.Surface((sz*2, sz*2), pygame.SRCALPHA)
            pygame.draw.rect(ps2, (r2,g2,b2,int(a*200)), ps2.get_rect())
            surf.blit(ps2, (int(pt['x'])+ox-sz, int(pt['y'])+oy-sz))
        draw_text(surf, f"SCORE  {self.score:06d}", FONT_SM, WHITE, SW-220, 8)
        draw_text(surf, f"WAVE {self.wave}", FONT_SM, LIGHT_GRAY, SW//2, 8, center=True)
        if self.player.power_lvl == 2:
            draw_text(surf, f"SPREAD SHOT  {self.player.power_t:.1f}s",
                      FONT_XS, YELLOW, 14, SH - 22)
        if self.between:
            ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
            ov.fill((0,0,0,120))
            surf.blit(ov, (0,0))
            draw_text(surf, f"WAVE {self.wave} CLEAR!", FONT_LG, YELLOW,
                      SW//2, SH//2 - 30, center=True)
            draw_text(surf, "Bersiap...", FONT_MD, LIGHT_GRAY,
                      SW//2, SH//2 + 30, center=True)
        self.story.draw(surf)
        draw_vignette(surf)
        draw_scanlines(surf)

# ══════════════════════════════════════════════════════════
#  TRANSITION SCREEN
# ══════════════════════════════════════════════════════════

class TransitionScreen:
    LINES = [
        "> Mendeteksi sinyal pesawat tua...",
        "> Mengaktifkan sistem propulsi...",
        "> PERINGATAN: Armada alien terdeteksi!",
        "> Sistem senjata otomatis aktif...",
        "> Koordinat jalur pelarian terkunci.",
        "> MELARIKAN DIRI DARI ATMOSFER...",
        "",
        "[ MODE: SPACE SHOOTER AKTIF ]",
        "",
        "Tekan ENTER untuk lanjut...",
    ]

    def __init__(self):
        self.shown_lines = 0
        self.t           = 0.0
        self.done        = False

    def update(self, dt, keys):
        self.t += dt
        self.shown_lines = min(len(self.LINES), int(self.t / 0.45))
        if (keys[pygame.K_RETURN] or keys[pygame.K_SPACE]) \
                and self.shown_lines >= len(self.LINES):
            self.done = True

    def draw(self, surf):
        surf.fill(BLACK)
        draw_text(surf, "PESAWAT DITEMUKAN!", FONT_LG, RED, SW//2, 60, center=True)
        for i, line in enumerate(self.LINES[:self.shown_lines]):
            col = CYAN if "[" in line else (0, 200, 0)
            draw_text(surf, line, FONT_SM, col, 120, 140 + i * 32)
        if self.shown_lines >= len(self.LINES):
            if int(pygame.time.get_ticks() / 500) % 2 == 0:
                draw_text(surf, "[ ENTER / SPACE untuk lanjut ]",
                          FONT_MD, YELLOW, SW//2, SH - 60, center=True)
        draw_vignette(surf)
        draw_scanlines(surf)

# ══════════════════════════════════════════════════════════
#  LEVEL LOADING SCREEN
# ══════════════════════════════════════════════════════════

class LevelLoadingScreen:
    FADE_IN_DUR  = 0.6
    HOLD_DUR     = 3.2
    FADE_OUT_DUR = 0.8
    TOTAL        = FADE_IN_DUR + HOLD_DUR + FADE_OUT_DUR

    def __init__(self, level_num):
        self.level_num   = level_num
        self.t           = 0.0
        self.done        = False
        cfg              = LEVEL_CFG[level_num]
        self.level_name  = cfg['name']
        self.story_lines = cfg['story']
        self.accent      = {
            1: (160, 30,  30),
            2: (30,  140, 30),
            3: (160, 30,  100),
            4: (30,  60,  200),
            5: (200, 50,  30),
        }.get(level_num, (120, 120, 120))
        # Partikel dekorasi latar
        self.sparks = [
            {'x': random.uniform(0, SW), 'y': random.uniform(0, SH),
             'vx': random.uniform(-18, 18), 'vy': random.uniform(-12, 12),
             'life': random.uniform(1.5, 4.0), 'max_life': 4.0,
             'size': random.randint(1, 3),
             'col': tuple(min(255, c + random.randint(-30, 30)) for c in self.accent)}
            for _ in range(55)
        ]
        self.visible_lines = 0
        self.LINE_INTERVAL = 0.52

    def update(self, dt):
        self.t = min(self.t + dt, self.TOTAL)
        if self.t >= self.TOTAL:
            self.done = True
            return
        # Typewriter: munculkan baris story satu per satu selama HOLD
        hold_elapsed = max(0, self.t - self.FADE_IN_DUR)
        self.visible_lines = min(
            len(self.story_lines),
            int(hold_elapsed / self.LINE_INTERVAL) + 1
        )
        for sp in self.sparks:
            sp['x']    += sp['vx'] * dt
            sp['y']    += sp['vy'] * dt
            sp['life'] -= dt
            if sp['life'] <= 0:
                sp['x']    = random.uniform(0, SW)
                sp['y']    = random.uniform(0, SH)
                sp['life'] = random.uniform(2.0, 4.0)

    def _alpha(self):
        """Hitung alpha overlay: 255=hitam penuh, 0=transparan."""
        if self.t < self.FADE_IN_DUR:
            return int(255 * (1.0 - self.t / self.FADE_IN_DUR))
        elif self.t < self.FADE_IN_DUR + self.HOLD_DUR:
            return 0
        else:
            progress = (self.t - self.FADE_IN_DUR - self.HOLD_DUR) / self.FADE_OUT_DUR
            return int(255 * min(1.0, progress))

    def draw(self, surf):
        surf.fill((4, 4, 10))

        # Sparks dekoratif
        for sp in self.sparks:
            a = min(1.0, sp['life'] / sp['max_life'])
            r, g, b = sp['col']
            pygame.draw.rect(surf, (int(r*a), int(g*a), int(b*a)),
                             (int(sp['x']), int(sp['y']), sp['size'], sp['size']))

        # Garis aksen atas judul
        ac = self.accent
        for i, thickness in enumerate([1, 3, 1]):
            yy = SH//2 - 90 + i * 4
            pygame.draw.line(surf, ac, (60, yy), (SW - 60, yy), thickness)

        # Label level kecil
        draw_text(surf, f"LEVEL  {self.level_num}  /  5",
                  FONT_XS, tuple(min(255, c + 80) for c in ac),
                  SW//2, SH//2 - 108, center=True)

        # Nama level besar
        draw_text(surf, self.level_name, FONT_LG, WHITE,
                  SW//2, SH//2 - 78, center=True)

        # Garis aksen bawah judul
        pygame.draw.line(surf, ac, (60, SH//2 - 42), (SW - 60, SH//2 - 42), 1)

        # Story lines typewriter
        for i in range(self.visible_lines):
            is_latest = (i == self.visible_lines - 1)
            col = WHITE if is_latest else tuple(min(255, c + 40) for c in ac)
            draw_text(surf, self.story_lines[i], FONT_SM, col,
                      SW//2, SH//2 - 14 + i * 26, center=True)

        # Loading bar
        bar_x, bar_y = SW//2 - 200, SH//2 + 125
        bar_w, bar_h = 400, 6
        hold_elapsed = max(0.0, self.t - self.FADE_IN_DUR)
        fill_ratio   = min(1.0, hold_elapsed / self.HOLD_DUR)
        pygame.draw.rect(surf, (20, 22, 35), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(surf, ac,           (bar_x, bar_y, int(bar_w * fill_ratio), bar_h))
        pygame.draw.rect(surf, GRAY,         (bar_x, bar_y, bar_w, bar_h), 1)
        draw_text(surf, f"MEMUAT...  {int(fill_ratio * 100)}%",
                  FONT_XS, GRAY, SW//2, bar_y + 14, center=True)

        # Hint kontrol muncul di akhir loading
        if fill_ratio > 0.85:
            draw_text(surf,
                      "WASD / Arrow = Gerak   Z / Ctrl = Tembak   X = Granat",
                      FONT_XS, (80, 80, 80), SW//2, SH - 30, center=True)

        # Fade overlay
        alpha = self._alpha()
        if alpha > 0:
            ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, alpha))
            surf.blit(ov, (0, 0))

        draw_scanlines(surf)


# ══════════════════════════════════════════════════════════
#  LEVEL SELECT SCREEN
# ══════════════════════════════════════════════════════════

LEVEL_SELECT_INFO = {
    1: ("THE CRASH SITE",   "crawler",  "Tidak ada boss",       (80,  20, 120)),
    2: ("THE FUNGAL SWAMP", "spitter",  "Tidak ada boss",       (20,  80, 20)),
    3: ("THE HIVE DEPTHS",  "hunter",   "Boss: HIVE QUEEN",     (120, 20, 80)),
    4: ("THE CRYSTAL CAVES","sentry",   "Boss: CRYSTAL GUARDIAN",(20, 40, 140)),
    5: ("THE LAUNCH PAD",   "elite",    "Boss: PLANET LORD",    (160, 20, 20)),
}

class LevelSelectScreen:
    def __init__(self):
        self.t          = 0.0
        self.selected   = 0          # 0-indexed (level 1–5)
        self.confirmed  = False
        self.chosen_lvl = 1
        self.stars      = [(random.randint(0,SW), random.randint(0,SH),
                            random.uniform(15,80), random.randint(1,2),
                            random.uniform(0.3,1.0)) for _ in range(160)]

    def update(self, dt, keys):
        self.t += dt
        for i, (x, y, spd, sz, br) in enumerate(self.stars):
            x -= spd * dt
            if x < 0:
                x = SW; y = random.randint(0, SH)
            self.stars[i] = (x, y, spd, sz, br)

    def handle_key(self, key):
        if key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % 5
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % 5
        elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
            self.chosen_lvl = self.selected + 1
            self.confirmed  = True
        elif key == pygame.K_ESCAPE:
            return 'back'
        return None

    def draw(self, surf):
        surf.fill((4, 4, 14))
        for (x, y, _, sz, br) in self.stars:
            c = int(br * 160)
            pygame.draw.rect(surf, (c,c,c), (int(x), int(y), sz, sz))

        draw_text(surf, "PILIH LEVEL", FONT_LG, (220, 30, 30), SW//2, 38, center=True)
        draw_text(surf, "UP/DOWN = Pilih    ENTER = Mulai    ESC = Kembali",
                  FONT_XS, GRAY, SW//2, 82, center=True)

        card_w, card_h = 560, 62
        cx = SW//2 - card_w//2
        for i in range(5):
            cy   = 110 + i * (card_h + 10)
            lvl  = i + 1
            name, etype, boss_txt, accent = LEVEL_SELECT_INFO[lvl]
            sel  = (i == self.selected)

            # Card background
            bg_alpha = 200 if sel else 120
            bg_surf  = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if sel:
                pulse = 0.6 + 0.4 * math.sin(self.t * 4)
                bg_surf.fill((*accent, int(60 * pulse)))
            else:
                bg_surf.fill((10, 12, 22, bg_alpha))
            surf.blit(bg_surf, (cx, cy))

            # Border
            border_col = tuple(min(255, c + 80) for c in accent) if sel else (30, 35, 55)
            pygame.draw.rect(surf, border_col, (cx, cy, card_w, card_h), 2 if sel else 1)

            # Left accent bar
            bar_col = tuple(min(255, c + 40) for c in accent)
            pygame.draw.rect(surf, bar_col, (cx, cy, 4, card_h))

            # Level number badge
            badge_col = accent if sel else (30, 35, 55)
            pygame.draw.rect(surf, badge_col, (cx + 12, cy + 14, 34, 34), border_radius=4)
            draw_text(surf, str(lvl), FONT_MD,
                      WHITE if sel else LIGHT_GRAY,
                      cx + 29, cy + 18, center=True)

            # Level name & info
            name_col = WHITE if sel else LIGHT_GRAY
            draw_text(surf, f"LEVEL {lvl}: {name}", FONT_SM, name_col, cx + 58, cy + 10)
            draw_text(surf, f"Enemy: {etype}   |   {boss_txt}",
                      FONT_XS, GRAY, cx + 58, cy + 34)

            # Arrow indicator
            if sel:
                ax = cx + card_w - 24
                ay = cy + card_h//2
                pulse_off = int(5 * math.sin(self.t * 6))
                pygame.draw.polygon(surf, WHITE, [
                    (ax + pulse_off, ay),
                    (ax - 6 + pulse_off, ay - 7),
                    (ax - 6 + pulse_off, ay + 7),
                ])

        # Preview box
        _, _, _, accent = LEVEL_SELECT_INFO[self.selected + 1]
        prev_y = 110 + 5 * (card_h + 10) + 10
        prev_surf = pygame.Surface((card_w, 50), pygame.SRCALPHA)
        prev_surf.fill((0, 0, 0, 140))
        surf.blit(prev_surf, (cx, prev_y))
        pygame.draw.rect(surf, (30, 35, 55), (cx, prev_y, card_w, 50), 1)
        story_lines = LEVEL_CFG[self.selected + 1]['story']
        draw_text(surf, story_lines[0] if story_lines else "",
                  FONT_XS, tuple(min(255, c+60) for c in accent),
                  cx + 12, prev_y + 10)
        draw_text(surf, story_lines[-1] if len(story_lines) > 1 else "",
                  FONT_XS, GRAY, cx + 12, prev_y + 28)

        draw_vignette(surf)
        draw_scanlines(surf)




class TitleScreen:
    def __init__(self):
        self.t    = 0.0
        self.stars= [(random.randint(0,SW), random.randint(0,SH),
                      random.uniform(20,100), random.randint(1,2),
                      random.uniform(0.2,1.0)) for _ in range(200)]

    def update(self, dt, keys):
        self.t += dt
        for i, (x, y, spd, sz, br) in enumerate(self.stars):
            x -= spd * dt
            if x < 0:
                x = SW
                y = random.randint(0, SH)
            self.stars[i] = (x, y, spd, sz, br)

    def draw(self, surf):
        surf.fill((4, 4, 14))
        for (x, y, _, sz, br) in self.stars:
            c = int(br * 180)
            pygame.draw.rect(surf, (c,c,c), (int(x), int(y), sz, sz))
        pg2 = pygame.Surface((SW, SH), pygame.SRCALPHA)
        for i in range(8):
            r2 = 260 - i*28
            pygame.draw.ellipse(pg2, (100, 0, 0, 12),
                                (SW//2 - r2, SH//2 - r2//2 + 60, r2*2, r2))
        surf.blit(pg2, (0, 0))
        draw_text(surf, "ALIEN ESCAPE", FONT_LG, (220, 30, 30), SW//2, 100, center=True)
        draw_text(surf, "SURVIVE  OR  DIE", FONT_MD, (140, 0, 0), SW//2, 158, center=True)
        info_surf = pygame.Surface((640, 110), pygame.SRCALPHA)
        info_surf.fill((0, 0, 0, 160))
        surf.blit(info_surf, ((SW-640)//2, 200))
        pygame.draw.rect(surf, (80,0,0), ((SW-640)//2, 200, 640, 110), 1)
        texts = [
            ("Kamu terdampar di planet asing yang gelap.", LIGHT_GRAY),
            ("5 level ketakutan -- temukan senjata, bunuh semua monster.", LIGHT_GRAY),
            ("", LIGHT_GRAY),
            ("WASD/Arrow: Gerak  Z/Ctrl: Tembak  X: Granat  Space: Lompat", GRAY),
        ]
        for i, (t2, col) in enumerate(texts):
            draw_text(surf, t2, FONT_XS, col, SW//2, 212 + i*22, center=True)

        # Menu buttons
        blink = int(self.t / 0.55) % 2 == 0
        if blink:
            draw_text(surf, "[ ENTER / SPACE ]  Mulai dari Level 1",
                      FONT_SM, YELLOW, SW//2, SH - 110, center=True)
            draw_text(surf, "[ L ]  Pilih Level",
                      FONT_SM, CYAN,   SW//2, SH - 78,  center=True)

        cx3 = SW//2
        cy3 = 68
        pygame.draw.polygon(surf, CYAN, [
            (cx3+20, cy3), (cx3+40, cy3+18),
            (cx3+28, cy3+14), (cx3+12, cy3+14),
            (cx3, cy3+18)
        ])
        pygame.draw.circle(surf, ORANGE, (cx3+20, cy3+20),
                           4 + int(2*math.sin(self.t*8)))
        draw_vignette(surf)
        draw_scanlines(surf)

# ══════════════════════════════════════════════════════════
#  GAME OVER / WIN
# ══════════════════════════════════════════════════════════

def draw_gameover(surf, score, level, t):
    surf.fill((5, 0, 0))
    random.seed(42)
    for i in range(20):
        x  = random.randint(0, SW)
        h2 = random.randint(20, 120)
        pygame.draw.line(surf, BLOOD_RED, (x, 0), (x, h2), 2)
    pulse = 0.7 + 0.3*math.sin(t*3)
    draw_text(surf, "KAMU  MATI", FONT_LG,
              (int(220*pulse), 0, 0), SW//2, 140, center=True)
    draw_text(surf, "Planet asing telah mengklaim korban baru...",
              FONT_SM, (120,0,0), SW//2, 220, center=True)
    draw_text(surf, f"SCORE :  {score:06d}", FONT_MD, WHITE, SW//2, 280, center=True)
    draw_text(surf, f"LEVEL :  {level} / 5",  FONT_MD, LIGHT_GRAY, SW//2, 320, center=True)
    if int(t/0.6)%2==0:
        draw_text(surf, "[ R ] Restart      [ ESC ] Keluar",
                  FONT_SM, YELLOW, SW//2, 410, center=True)
    draw_vignette(surf)
    draw_scanlines(surf)

def draw_win(surf, score, t):
    surf.fill((0, 5, 15))
    for i in range(180):
        sx = random.Random(i*7).randint(0, SW)
        sy = random.Random(i*13).randint(0, SH)
        c  = random.Random(i).randint(100, 255)
        pygame.draw.rect(surf, (c,c,c), (sx,sy,2,2))
    pulse = 0.8 + 0.2*math.sin(t*2)
    draw_text(surf, "SELAMAT!", FONT_LG,
              (0, int(200*pulse), int(100*pulse)), SW//2, 120, center=True)
    draw_text(surf, "Kamu berhasil melarikan diri dari planet neraka", FONT_SM,
              LIGHT_GRAY, SW//2, 200, center=True)
    draw_text(surf, "dan menghancurkan seluruh armada alien!", FONT_SM,
              LIGHT_GRAY, SW//2, 230, center=True)
    draw_text(surf, f"FINAL SCORE :  {score:06d}", FONT_LG,
              YELLOW, SW//2, 300, center=True)
    if int(t/0.6)%2==0:
        draw_text(surf, "[ ENTER ] Main Lagi      [ ESC ] Keluar",
                  FONT_SM, CYAN, SW//2, 420, center=True)
    draw_vignette(surf)
    draw_scanlines(surf)

# ══════════════════════════════════════════════════════════
#  MAIN GAME LOOP
# ══════════════════════════════════════════════════════════

def main():
    state        = 'TITLE'
    level        = 1
    score        = 0
    scene        = None
    title        = TitleScreen()
    lvl_select   = None
    loading      = None      
    transition   = None
    shooter      = None
    gameover_t   = 0.0
    win_t        = 0.0
    paused       = False
    cheat_buffer = ''        

    while True:
        dt   = clock.tick(FPS) / 1000.0
        dt   = min(dt, 0.05)
        keys = pygame.key.get_pressed()

        # ── Events ──────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # ── Cheat buffer ───────────────────────────
                if event.unicode.isalpha():
                    cheat_buffer = (cheat_buffer + event.unicode.lower())[-10:]
                else:
                    cheat_buffer = ''
                if state == 'PLATFORMER' and scene and 'railgun' in cheat_buffer:
                    scene.player.weapon = 'RAILGUN'
                    scene.player.ammo['RAILGUN'] = 999
                    scene.story.show(["[CHEAT] RAILGUN EQUIPPED!", "999 ammo loaded."])
                    cheat_buffer = ''
                if state == 'SHOOTER' and shooter and 'spread' in cheat_buffer:
                    shooter.player.power_lvl = 2
                    shooter.player.power_t   = 99999.0
                    shooter.story.show(["[CHEAT] SPREAD SHOT ACTIVATED!"])
                    cheat_buffer = ''
                if event.key == pygame.K_ESCAPE:
                    if state == 'LEVEL_SELECT':
                        state = 'TITLE'
                        title = TitleScreen()
                    else:
                        pygame.quit()
                        sys.exit()

                # ── Title ──────────────────────────────────
                if state == 'TITLE':
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        level   = 1
                        score   = 0
                        loading = LevelLoadingScreen(level)
                        state   = 'LOADING'
                    elif event.key == pygame.K_l:
                        state      = 'LEVEL_SELECT'
                        lvl_select = LevelSelectScreen()

                # ── Level Select ────────────────────────────
                elif state == 'LEVEL_SELECT':
                    result = lvl_select.handle_key(event.key)
                    if result == 'back':
                        state = 'TITLE'
                        title = TitleScreen()
                    if lvl_select.confirmed:
                        level   = lvl_select.chosen_lvl
                        score   = 0
                        loading = LevelLoadingScreen(level)
                        state   = 'LOADING'

                # ── Platformer ──────────────────────────────
                elif state == 'PLATFORMER':
                    if event.key == pygame.K_p:
                        paused = not paused

                # ── Game Over ───────────────────────────────
                elif state == 'GAMEOVER':
                    if event.key == pygame.K_r:
                        state  = 'TITLE'
                        title  = TitleScreen()
                        level  = 1
                        score  = 0

                # ── Win ─────────────────────────────────────
                elif state == 'WIN':
                    if event.key == pygame.K_RETURN:
                        state  = 'TITLE'
                        title  = TitleScreen()
                        level  = 1
                        score  = 0

        # ── Update ──────────────────────────────────────────
        if state == 'TITLE':
            title.update(dt, keys)
        elif state == 'LEVEL_SELECT':
            lvl_select.update(dt, keys)
        elif state == 'LOADING':
            loading.update(dt)
            if loading.done:
                scene = PlatformerScene(level, score)
                state = 'PLATFORMER'
        elif state == 'PLATFORMER':
            if not paused:
                scene.update(dt, keys)
                score = scene.score
            if scene.done:
                if level < 5:
                    level  += 1
                    score   = scene.score
                    loading = LevelLoadingScreen(level)
                    state   = 'LOADING'
                else:
                    score       = scene.score
                    transition  = TransitionScreen()
                    state       = 'TRANSITION'
            if scene.dead:
                state      = 'GAMEOVER'
                gameover_t = 0.0
        elif state == 'TRANSITION':
            transition.update(dt, keys)
            if transition.done:
                shooter = SpaceShooterScene(carry_score=score)
                state   = 'SHOOTER'
        elif state == 'SHOOTER':
            shooter.update(dt, keys)
            score = shooter.score
            if shooter.player.dead:
                state      = 'GAMEOVER'
                gameover_t = 0.0
            if shooter.won and shooter.won_t <= 0:
                state  = 'WIN'
                win_t  = 0.0
        elif state == 'GAMEOVER':
            gameover_t += dt
        elif state == 'WIN':
            win_t += dt

        # ── Draw ────────────────────────────────────────────
        if state == 'TITLE':
            title.draw(screen)
        elif state == 'LEVEL_SELECT':
            lvl_select.draw(screen)
        elif state == 'LOADING':
            loading.draw(screen)
        elif state == 'PLATFORMER':
            scene.draw(screen)
            if paused:
                ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
                ov.fill((0,0,0,150))
                screen.blit(ov, (0,0))
                draw_text(screen, "PAUSE", FONT_LG, WHITE, SW//2, SH//2-40, center=True)
                draw_text(screen, "P untuk lanjut", FONT_SM, GRAY, SW//2, SH//2+20, center=True)
        elif state == 'TRANSITION':
            transition.draw(screen)
        elif state == 'SHOOTER':
            shooter.draw(screen)
        elif state == 'GAMEOVER':
            if scene:
                scene.draw(screen)
            ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, min(200, int(gameover_t * 160))))
            screen.blit(ov, (0,0))
            if gameover_t > 0.8:
                draw_gameover(screen, score, level, gameover_t)
        elif state == 'WIN':
            if shooter:
                shooter.draw(screen)
            ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
            ov.fill((0, 0, 0, min(200, int(win_t * 150))))
            screen.blit(ov, (0,0))
            if win_t > 0.6:
                draw_win(screen, score, win_t)

        pygame.display.flip()

if __name__ == "__main__":
    main()