import os
import sys
import pygame
import random

# --- 1. SETTINGS & STABILITY ---
if sys.platform.startswith('win'):
    os.environ['SDL_AUDIODRIVER'] = 'directsound'

pygame.init()
try:
    pygame.mixer.init()
except:
    print("Audio system unavailable.")

WIDTH, HEIGHT = 450, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Faisal's Bird: Mobile Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 32, bold=True)
small_font = pygame.font.SysFont("Arial", 22, bold=True)
HS_FILE = "highscore.txt"

# --- 2. ASSET LOADERS & PERSISTENCE ---
def load_snd(name):
    if not pygame.mixer.get_init(): return None
    try:
        if os.path.exists(name):
            s = pygame.mixer.Sound(name)
            s.set_volume(0.4)
            return s
    except: return None
    return None

jump_snd = load_snd("jump.wav")
crash_snd = load_snd("crash.wav")
score_snd = load_snd("score.wav")

def get_high_score():
    if not os.path.exists(HS_FILE): return 0
    try:
        with open(HS_FILE, "r") as f: return int(f.read())
    except: return 0

def save_high_score(new_score):
    current = get_high_score()
    if new_score > current:
        with open(HS_FILE, "w") as f: f.write(str(new_score))

# --- 3. GAME CLASSES ---

class Background:
    def __init__(self):
        # Mountains: [x, y]
        self.mountains = [[i * 250, random.randint(420, 500)] for i in range(3)]
        # Clouds: [x, y, size]
        self.clouds = [[random.randint(0, WIDTH), random.randint(50, 220), random.randint(40, 65)] for i in range(4)]
        
    def draw(self, surf, state):
        surf.fill((100, 190, 255)) # Sky
        
        # Draw Clouds (Speed 0.5)
        for c in self.clouds:
            if state == "PLAYING": c[0] -= 0.5
            if c[0] < -120: 
                c[0] = WIDTH + 50
                c[1] = random.randint(50, 220)
            
            # Simple vector cloud
            pygame.draw.circle(surf, (255, 255, 255), (int(c[0]), int(c[1])), c[2])
            pygame.draw.circle(surf, (255, 255, 255), (int(c[0] + c[2]*0.7), int(c[1] - 5)), int(c[2]*0.8))
            pygame.draw.circle(surf, (255, 255, 255), (int(c[0] - c[2]*0.7), int(c[1] - 5)), int(c[2]*0.8))

        # Draw Mountains (Speed 1.0)
        for m in self.mountains:
            if state == "PLAYING": m[0] -= 1
            if m[0] < -400: m[0] = WIDTH + 50
            pygame.draw.ellipse(surf, (80, 160, 220), (m[0], m[1], 400, 300))

class Bird:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x, self.y = 70, HEIGHT // 2
        self.rect = pygame.Rect(self.x, self.y, 45, 35)
        self.vel = 0
        self.angle = 0

    def jump(self):
        self.vel = -7
        if jump_snd: jump_snd.play()

    def update(self):
        self.vel += 0.25
        self.y += self.vel
        self.rect.y = self.y
        self.angle = -self.vel * 4
        if self.angle > 30: self.angle = 30
        if self.angle < -60: self.angle = -60

    def draw(self, surf):
        # Draw the realistic bird from shapes
        b = pygame.Surface((70, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(b, (255, 215, 0), (10, 15, 45, 35)) # Body
        pygame.draw.circle(b, (255, 215, 0), (50, 25), 14)      # Head
        pygame.draw.circle(b, (255, 255, 255), (55, 22), 6)    # Eye
        pygame.draw.circle(b, (0, 0, 0), (57, 22), 3)          # Pupil
        pygame.draw.ellipse(b, (220, 170, 0), (15, 25, 22, 18)) # Wing
        pygame.draw.polygon(b, (255, 69, 0), [(60, 22), (72, 27), (60, 32)]) # Beak
        
        rotated = pygame.transform.rotate(b, self.angle)
        surf.blit(rotated, (self.x - 10, self.y - 10))

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 75
        self.gap = 210
        self.gap_y = random.randint(200, 500)
        self.passed = False
        self.top_rect = pygame.Rect(x, 0, self.width, self.gap_y - self.gap//2)
        self.bot_rect = pygame.Rect(x, self.gap_y + self.gap//2, self.width, HEIGHT)

    def draw(self, surf):
        G, LG, DG = (0, 140, 0), (0, 180, 0), (0, 70, 0)
        for r in [self.top_rect, self.bot_rect]:
            # Body
            pygame.draw.rect(surf, G, r)
            # Highlights
            pygame.draw.rect(surf, LG, (r.x + 8, r.y, 10, r.height)) 
            pygame.draw.rect(surf, DG, (r.x + self.width - 15, r.y, 8, r.height))
            # Pipe Cap (The realistic lip)
            cap_y = r.bottom - 25 if r == self.top_rect else r.top
            cap_rect = (self.x - 5, cap_y, self.width + 10, 25)
            pygame.draw.rect(surf, G, cap_rect)
            pygame.draw.rect(surf, (0, 0, 0), cap_rect, 2)

# --- 4. MAIN GAME LOOP ---

def main():
    bg = Background()
    bird = Bird()
    pipes = [Pipe(WIDTH + 150)]
    score = 0
    high_score = get_high_score()
    state = "START" # START, PLAYING, GAMEOVER

    while True:
        bg.draw(screen, state)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            # Responsive for Mouse (PC) and Finger (Mobile)
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                if state == "START":
                    state = "PLAYING"
                elif state == "PLAYING":
                    bird.jump()
                elif state == "GAMEOVER":
                    bird.reset()
                    pipes = [Pipe(WIDTH + 150)]
                    score = 0
                    high_score = get_high_score()
                    state = "START"

        if state == "PLAYING":
            bird.update()
            if pipes[-1].x < WIDTH - 280:
                pipes.append(Pipe(WIDTH))
            
            for pipe in pipes[:]:
                pipe.x -= 3.5
                pipe.top_rect.x = pipe.x
                pipe.bot_rect.x = pipe.x
                
                # Collision logic
                if bird.rect.colliderect(pipe.top_rect) or bird.rect.colliderect(pipe.bot_rect):
                    if crash_snd: crash_snd.play()
                    save_high_score(score)
                    state = "GAMEOVER"
                
                # Score logic
                if not pipe.passed and pipe.x < bird.x:
                    score += 1
                    pipe.passed = True
                    if score_snd: score_snd.play()
            
            # Floor/Ceiling crash
            if bird.y < 0 or bird.y > HEIGHT - 70:
                if crash_snd: crash_snd.play()
                save_high_score(score)
                state = "GAMEOVER"

        # Draw Pipe & Bird
        for pipe in pipes: pipe.draw(screen)
        pipes = [p for p in pipes if p.x > -100]
        bird.draw(screen)
        
        # Ground
        pygame.draw.rect(screen, (34, 139, 34), (0, HEIGHT-50, WIDTH, 50)) 

        # UI Overlay
        score_surf = font.render(f"{score}", True, (255, 255, 255))
        screen.blit(score_surf, (WIDTH//2 - 10, 50))
        
        hs_txt = small_font.render(f"BEST: {max(high_score, score)}", True, (255, 215, 0))
        screen.blit(hs_txt, (20, 20))

        if state == "START":
            msg = font.render("TAP TO START", True, (255, 255, 255))
            screen.blit(msg, (WIDTH//2 - 100, HEIGHT//2))
        
        if state == "GAMEOVER":
            msg = font.render("GAME OVER", True, (255, 50, 50))
            screen.blit(msg, (WIDTH//2 - 90, HEIGHT//2 - 20))
            retry = small_font.render("TAP TO RESTART", True, (255, 255, 255))
            screen.blit(retry, (WIDTH//2 - 95, HEIGHT//2 + 30))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()