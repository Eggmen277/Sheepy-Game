import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 100, 255)
GRAY = (128, 128, 128)
DARK_RED = (139, 0, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (25, 25, 112)
GOLD = (255, 215, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Telesheepy vs Rocket Hair")
clock = pygame.time.Clock()

# Ground level
GROUND = SCREEN_HEIGHT - 100


class Particle:
    """Visual effect particle"""
    def __init__(self, x, y, color, vel_x=None, vel_y=None, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x if vel_x is not None else random.uniform(-2, 2)
        self.vel_y = vel_y if vel_y is not None else random.uniform(-2, 2)
        self.life = life
        self.max_life = life
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += 0.2  # Gravity
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0 and self.max_life > 0:
            alpha = int((self.life / self.max_life) * 255)
            size = max(1, int(self.size * (self.life / self.max_life)))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


class Lightning:
    def __init__(self, x, y, direction, enhanced=False):
        self.x = x
        self.y = y
        self.direction = direction
        self.width = 30
        self.height = 80
        self.damage = 15 if not enhanced else 25
        self.speed = 12 if not enhanced else 15
        self.active = True
        self.animation_frame = 0
        self.enhanced = enhanced
        self.particles = []
        self.branches = []
        
        # Create lightning branches
        if enhanced:
            for _ in range(3):
                branch_offset = random.randint(-20, 20)
                self.branches.append({
                    'offset': branch_offset,
                    'length': random.randint(20, 40)
                })
        
    def update(self):
        self.x += self.speed * self.direction
        self.animation_frame += 1
        
        # Generate electric particles
        if self.animation_frame % 2 == 0:
            particle_count = 5 if self.enhanced else 2
            for _ in range(particle_count):
                px = self.x + random.randint(-10, 10)
                py = self.y + random.randint(0, 60)
                self.particles.append(Particle(px, py, CYAN, 
                                              vel_x=random.uniform(-1, 1),
                                              vel_y=random.uniform(-1, 1),
                                              life=15))
        
        # Update particles
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        # Remove if off screen
        if self.x < -50 or self.x > SCREEN_WIDTH + 50:
            self.active = False
            
    def draw(self, screen):
        # Draw particles first (glow effect)
        for particle in self.particles:
            particle.draw(screen)
        
        # Main lightning bolt
        points = [
            (self.x, self.y),
            (self.x + 15 * self.direction, self.y + 25),
            (self.x + 5 * self.direction, self.y + 25),
            (self.x + 20 * self.direction, self.y + 60),
            (self.x + 10 * self.direction, self.y + 40),
            (self.x, self.y + 40)
        ]
        
        # Draw glow effect (larger transparent bolt)
        if self.enhanced:
            glow_points = [(p[0] + random.randint(-2, 2), p[1] + random.randint(-2, 2)) for p in points]
            pygame.draw.polygon(screen, CYAN, glow_points)
        
        # Flashing effect
        if self.animation_frame % 4 < 2:
            pygame.draw.polygon(screen, WHITE, points)
            pygame.draw.polygon(screen, CYAN if self.enhanced else YELLOW, points, 3)
        else:
            pygame.draw.polygon(screen, CYAN if self.enhanced else YELLOW, points)
            pygame.draw.polygon(screen, WHITE, points, 3)
        
        # Draw branches for enhanced lightning
        if self.enhanced:
            for branch in self.branches:
                branch_x = self.x + branch['offset'] * self.direction
                branch_y = self.y + 30
                end_x = branch_x + branch['length'] * self.direction
                end_y = branch_y + random.randint(-10, 10)
                
                if self.animation_frame % 4 < 2:
                    pygame.draw.line(screen, WHITE, (int(branch_x), int(branch_y)), (int(end_x), int(end_y)), 3)
                    pygame.draw.line(screen, CYAN, (int(branch_x), int(branch_y)), (int(end_x), int(end_y)), 1)
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Rocket:
    def __init__(self, x, y, direction, target_y):
        self.x = x
        self.y = y
        self.direction = direction
        self.target_y = target_y
        self.width = 40
        self.height = 20
        self.damage = 18
        self.speed_x = 8
        self.speed_y = 0
        self.active = True
        self.trail = []
        
    def update(self):
        self.x += self.speed_x * self.direction
        
        # Homing effect
        if self.y < self.target_y:
            self.speed_y += 0.3
        else:
            self.speed_y -= 0.3
            
        self.speed_y = max(-5, min(5, self.speed_y))
        self.y += self.speed_y
        
        # Add trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        # Remove if off screen
        if self.x < -50 or self.x > SCREEN_WIDTH + 50:
            self.active = False
            
    def draw(self, screen):
        # Draw smoke trail
        for i, pos in enumerate(self.trail):
            size = i + 2
            pygame.draw.circle(screen, GRAY, (int(pos[0]), int(pos[1])), size)
        
        # Draw rocket body
        if self.direction > 0:
            points = [
                (self.x, self.y),
                (self.x + 30, self.y - 8),
                (self.x + 40, self.y),
                (self.x + 30, self.y + 8)
            ]
        else:
            points = [
                (self.x, self.y),
                (self.x - 30, self.y - 8),
                (self.x - 40, self.y),
                (self.x - 30, self.y + 8)
            ]
            
        pygame.draw.polygon(screen, RED, points)
        pygame.draw.polygon(screen, DARK_RED, points, 2)
        
        # Draw flame
        flame_x = self.x
        if random.randint(0, 1):
            pygame.draw.circle(screen, ORANGE, (int(flame_x - 10 * self.direction), int(self.y)), 6)
            pygame.draw.circle(screen, YELLOW, (int(flame_x - 15 * self.direction), int(self.y)), 4)
    
    def get_rect(self):
        return pygame.Rect(self.x - 20, self.y - 10, self.width, self.height)


class Character:
    def __init__(self, x, y, controls, name):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 80
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = 15
        self.on_ground = False
        self.health = 100
        self.max_health = 100
        self.controls = controls
        self.name = name
        self.direction = 1
        self.attack_cooldown = 0
        self.is_attacking = False
        self.hit_cooldown = 0
        self.hypercharge_ready = True
        self.hypercharge_cooldown = 0
        self.hypercharge_active = False
        self.hypercharge_duration = 0
        
    def move(self, keys):
        # Speed boost during hypercharge
        speed_mult = 1.5 if self.hypercharge_active else 1.0
        
        # Horizontal movement
        self.vel_x = 0
        if keys[self.controls['left']]:
            self.vel_x = -self.speed * speed_mult
            self.direction = -1
        if keys[self.controls['right']]:
            self.vel_x = self.speed * speed_mult
            self.direction = 1
            
        # Jump
        if keys[self.controls['up']] and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False
            
        # Apply gravity
        self.vel_y += 0.8
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Boundaries
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            
        # Ground collision
        if self.y >= GROUND - self.height:
            self.y = GROUND - self.height
            self.vel_y = 0
            self.on_ground = True
            
        # Update cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        if self.hypercharge_cooldown > 0:
            self.hypercharge_cooldown -= 1
        else:
            self.hypercharge_ready = True
            
        # Update hypercharge duration
        if self.hypercharge_duration > 0:
            self.hypercharge_duration -= 1
        else:
            self.hypercharge_active = False
            
    def take_damage(self, damage):
        if self.hit_cooldown == 0:
            # Reduced damage during hypercharge
            actual_damage = damage * 0.5 if self.hypercharge_active else damage
            self.health -= actual_damage
            self.hit_cooldown = 20
            if self.health < 0:
                self.health = 0
                
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Telesheepy(Character):
    def __init__(self, x, y, controls):
        super().__init__(x, y, controls, "Telesheepy")
        self.lightnings = []
        self.ability_cooldowns = {'1': 0, '2': 0, '3': 0}
        self.particles = []
        
    def activate_hypercharge(self):
        if self.hypercharge_ready:
            self.hypercharge_active = True
            self.hypercharge_duration = 180  # 3 seconds at 60 FPS
            self.hypercharge_cooldown = 900  # 15 seconds
            self.hypercharge_ready = False
            
            # Create massive lightning storm
            for i in range(10):
                lightning = Lightning(self.x + self.width // 2, self.y + 20, self.direction, enhanced=True)
                lightning.y += random.randint(-30, 30)
                lightning.speed = 10 + random.uniform(-2, 2)
                lightning.damage = 30
                self.lightnings.append(lightning)
            
            # Spawn electric particles
            for _ in range(50):
                self.particles.append(Particle(
                    self.x + self.width // 2,
                    self.y + 40,
                    CYAN,
                    vel_x=random.uniform(-5, 5),
                    vel_y=random.uniform(-5, 5),
                    life=60
                ))
        
    def use_ability(self, keys):
        # Hypercharge (4)
        if keys[pygame.K_4]:
            self.activate_hypercharge()
        
        # Enhanced abilities during hypercharge
        damage_mult = 1.5 if self.hypercharge_active else 1.0
        
        # Lightning Strike (1) - Single bolt
        if keys[pygame.K_1] and self.ability_cooldowns['1'] == 0:
            lightning = Lightning(self.x + self.width // 2, self.y + 20, self.direction, self.hypercharge_active)
            lightning.damage *= damage_mult
            self.lightnings.append(lightning)
            self.ability_cooldowns['1'] = 40
            
        # Thunder Storm (2) - Multiple bolts
        if keys[pygame.K_2] and self.ability_cooldowns['2'] == 0:
            count = 3 if not self.hypercharge_active else 5
            for i in range(count):
                lightning = Lightning(self.x + self.width // 2, self.y + 20 - i * 15, self.direction, self.hypercharge_active)
                lightning.speed = 10 + i * 2
                lightning.damage *= damage_mult
                self.lightnings.append(lightning)
            self.ability_cooldowns['2'] = 80
            
        # Lightning Wave (3) - Spread attack
        if keys[pygame.K_3] and self.ability_cooldowns['3'] == 0:
            angles = [-20, 0, 20] if not self.hypercharge_active else [-30, -15, 0, 15, 30]
            for angle in angles:
                lightning = Lightning(self.x + self.width // 2, self.y + 20, self.direction, self.hypercharge_active)
                lightning.angle = angle
                lightning.damage *= damage_mult
                self.lightnings.append(lightning)
            self.ability_cooldowns['3'] = 60
            
        # Update cooldowns
        for key in self.ability_cooldowns:
            if self.ability_cooldowns[key] > 0:
                self.ability_cooldowns[key] -= 1
                
    def update_projectiles(self):
        for lightning in self.lightnings:
            lightning.update()
        self.lightnings = [l for l in self.lightnings if l.active]
        
        # Update particles
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        # Generate particles during hypercharge
        if self.hypercharge_active and random.random() < 0.3:
            self.particles.append(Particle(
                self.x + random.randint(0, self.width),
                self.y + random.randint(0, self.height),
                CYAN,
                vel_x=random.uniform(-2, 2),
                vel_y=random.uniform(-3, -1),
                life=30
            ))
        
    def draw(self, screen):
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw character with hit flash
        if self.hit_cooldown > 0 and self.hit_cooldown % 4 < 2:
            color_offset = (50, 50, 50)
        elif self.hypercharge_active:
            # Electric glow during hypercharge
            color_offset = (random.randint(0, 30), random.randint(0, 30), random.randint(50, 100))
        else:
            color_offset = (0, 0, 0)
            
        # Body (fluffy sheep)
        body_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate(WHITE))
        pygame.draw.ellipse(screen, body_color, (self.x, self.y + 30, self.width, 50))
        
        # Hypercharge aura
        if self.hypercharge_active:
            pygame.draw.ellipse(screen, CYAN, (self.x - 5, self.y + 25, self.width + 10, 60), 2)
        
        # Head
        pygame.draw.circle(screen, body_color, (int(self.x + self.width // 2), int(self.y + 20)), 20)
        
        # Teletubby ears
        ear_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate(PURPLE))
        # Left ear
        pygame.draw.circle(screen, ear_color, (int(self.x + 10), int(self.y + 5)), 8)
        pygame.draw.rect(screen, ear_color, (self.x + 5, self.y - 10, 10, 15))
        pygame.draw.circle(screen, ear_color, (int(self.x + 10), int(self.y - 10)), 5)
        
        # Right ear
        pygame.draw.circle(screen, ear_color, (int(self.x + 40), int(self.y + 5)), 8)
        pygame.draw.rect(screen, ear_color, (self.x + 35, self.y - 10, 10, 15))
        pygame.draw.circle(screen, ear_color, (int(self.x + 40), int(self.y - 10)), 5)
        
        # Face
        eye_offset = 5 if self.direction > 0 else -5
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width // 2 - 8 + eye_offset), int(self.y + 18)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width // 2 + 8 + eye_offset), int(self.y + 18)), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width // 2), int(self.y + 25)), 2)
        
        # Legs
        pygame.draw.rect(screen, GRAY, (self.x + 10, self.y + 70, 8, 15))
        pygame.draw.rect(screen, GRAY, (self.x + 32, self.y + 70, 8, 15))
        
        # Draw projectiles
        for lightning in self.lightnings:
            lightning.draw(screen)


class RocketHair(Character):
    def __init__(self, x, y, controls):
        super().__init__(x, y, controls, "Rocket Hair")
        self.rockets = []
        self.ability_cooldowns = {'7': 0, '8': 0, '9': 0}
        self.particles = []

    def activate_hypercharge(self, target=None):
        if self.hypercharge_ready:
            self.hypercharge_active = True
            self.hypercharge_duration = 180  # 3 seconds
            self.hypercharge_cooldown = 900  # 15 seconds
            self.hypercharge_ready = False

            # Visual explosion particles
            for _ in range(100):
                self.particles.append(Particle(
                    self.x + self.width // 2,
                    self.y + 40,
                    random.choice([RED, ORANGE, YELLOW, WHITE]),
                    vel_x=random.uniform(-8, 8),
                    vel_y=random.uniform(-8, 8),
                    life=60
                ))

            # Area explosion damage when activating
            if target is not None:
                explosion_radius = 120
                explosion_damage = 35
                rocket_center = pygame.Vector2(self.x + self.width // 2, self.y + self.height // 2)
                target_center = pygame.Vector2(target.x + target.width // 2, target.y + target.height // 2)
                distance = rocket_center.distance_to(target_center)
                if distance < explosion_radius:
                    target.take_damage(explosion_damage)

            # Extra flash particles for style
            for _ in range(30):
                self.particles.append(Particle(
                    self.x + self.width // 2,
                    self.y + 40,
                    random.choice([YELLOW, ORANGE, RED, WHITE]),
                    vel_x=random.uniform(-10, 10),
                    vel_y=random.uniform(-10, 10),
                    life=30
                ))

    def use_ability(self, keys, target):
        # Hypercharge (0)
        if keys[pygame.K_0]:
            self.activate_hypercharge(target)

        damage_mult = 1.5 if self.hypercharge_active else 1.0

        # Single Rocket (7)
        if keys[pygame.K_7] and self.ability_cooldowns['7'] == 0:
            rocket = Rocket(self.x + self.width // 2, self.y, self.direction, target.y + target.height // 2)
            rocket.damage *= damage_mult
            self.rockets.append(rocket)
            self.ability_cooldowns['7'] = 40

        # Rocket Barrage (8)
        if keys[pygame.K_8] and self.ability_cooldowns['8'] == 0:
            count = 3 if not self.hypercharge_active else 6
            for i in range(count):
                rocket = Rocket(self.x + self.width // 2, self.y - i * 20, self.direction, target.y + target.height // 2)
                rocket.speed_x = 8 + random.uniform(-1, 1)
                rocket.damage *= damage_mult
                self.rockets.append(rocket)
            self.ability_cooldowns['8'] = 80

        # Homing Missile (9)
        if keys[pygame.K_9] and self.ability_cooldowns['9'] == 0:
            rocket = Rocket(self.x + self.width // 2, self.y, self.direction, target.y + target.height // 2)
            rocket.speed_x = 12
            rocket.damage = 25 * damage_mult
            self.rockets.append(rocket)
            self.ability_cooldowns['9'] = 100

        # Update cooldowns
        for key in self.ability_cooldowns:
            if self.ability_cooldowns[key] > 0:
                self.ability_cooldowns[key] -= 1

    def update_projectiles(self, target):
        for rocket in self.rockets:
            rocket.target_y = target.y + target.height // 2
            rocket.update()
        self.rockets = [r for r in self.rockets if r.active]

        # Update particles
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # Flame aura during hypercharge
        if self.hypercharge_active and random.random() < 0.3:
            self.particles.append(Particle(
                self.x + random.randint(0, self.width),
                self.y + random.randint(0, self.height),
                random.choice([RED, ORANGE, YELLOW]),
                vel_x=random.uniform(-2, 2),
                vel_y=random.uniform(-3, -1),
                life=30
            ))

    def draw(self, screen):
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

        # Visual glow variations
        if self.hit_cooldown > 0 and self.hit_cooldown % 4 < 2:
            color_offset = (50, 50, 50)
        elif self.hypercharge_active:
            color_offset = (random.randint(50, 100), random.randint(0, 30), 0)
        else:
            color_offset = (0, 0, 0)

        # Body
        body_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate(BLUE))
        pygame.draw.rect(screen, body_color, (self.x + 10, self.y + 30, 30, 40))

        # Hypercharge aura
        if self.hypercharge_active:
            pygame.draw.rect(screen, ORANGE, (self.x + 5, self.y + 25, 40, 50), 2)

        # Arms
        pygame.draw.rect(screen, body_color, (self.x, self.y + 35, 10, 25))
        pygame.draw.rect(screen, body_color, (self.x + 40, self.y + 35, 10, 25))

        # Legs
        leg_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate(GRAY))
        pygame.draw.rect(screen, leg_color, (self.x + 15, self.y + 70, 8, 15))
        pygame.draw.rect(screen, leg_color, (self.x + 27, self.y + 70, 8, 15))

        # Head base
        head_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate((255, 220, 180)))
        pygame.draw.circle(screen, head_color, (int(self.x + self.width // 2), int(self.y + 20)), 15)

        # Rocket head
        rocket_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate(RED))
        pygame.draw.polygon(screen, rocket_color, [
            (self.x + self.width // 2 - 10, self.y + 5),
            (self.x + self.width // 2 + 10, self.y + 5),
            (self.x + self.width // 2 + 10, self.y - 15),
            (self.x + self.width // 2 - 10, self.y - 15)
        ])
        pygame.draw.polygon(screen, DARK_RED, [
            (self.x + self.width // 2 - 10, self.y - 15),
            (self.x + self.width // 2 + 10, self.y - 15),
            (self.x + self.width // 2, self.y - 25)
        ])

        # Rocket fins
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + self.width // 2 - 10, self.y + 5),
            (self.x + self.width // 2 - 15, self.y + 5),
            (self.x + self.width // 2 - 10, self.y - 5)
        ])
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + self.width // 2 + 10, self.y + 5),
            (self.x + self.width // 2 + 15, self.y + 5),
            (self.x + self.width // 2 + 10, self.y - 5)
        ])

        # Face
        eye_offset = 3 if self.direction > 0 else -3
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width // 2 - 5 + eye_offset), int(self.y + 18)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width // 2 + 5 + eye_offset), int(self.y + 18)), 2)

        # Draw projectiles
        for rocket in self.rockets:
            rocket.draw(screen)
    def __init__(self, x, y, controls):
        super().__init__(x, y, controls, "Rocket Hair")
        self.rockets = []
        self.ability_cooldowns = {'7': 0, '8': 0, '9': 0}
        self.particles = []
        
    def activate_hypercharge(self):
        if self.hypercharge_ready:
            self.hypercharge_active = True
            self.hypercharge_duration = 180  # 3 seconds
            self.hypercharge_cooldown = 900  # 15 seconds
            self.hypercharge_ready = False
            
            # Spawn explosion particles
            for _ in range(100):
                self.particles.append(Particle(
                    self.x + self.width // 2,
                    self.y + 40,
                    random.choice([RED, ORANGE, YELLOW, WHITE]),
                    vel_x=random.uniform(-8, 8),
                    vel_y=random.uniform(-8, 8),
                    life=60
                ))
        
    def use_ability(self, keys, target):
        # Hypercharge (0)
        if keys[pygame.K_0]:
            self.activate_hypercharge()
        
        damage_mult = 1.5 if self.hypercharge_active else 1.0
        
        # Single Rocket (7)
        if keys[pygame.K_7] and self.ability_cooldowns['7'] == 0:
            rocket = Rocket(self.x + self.width // 2, self.y, self.direction, target.y + target.height // 2)
            rocket.damage *= damage_mult
            self.rockets.append(rocket)
            self.ability_cooldowns['7'] = 40
            
        # Rocket Barrage (8)
        if keys[pygame.K_8] and self.ability_cooldowns['8'] == 0:
            count = 3 if not self.hypercharge_active else 6
            for i in range(count):
                rocket = Rocket(self.x + self.width // 2, self.y - i * 20, self.direction, target.y + target.height // 2)
                rocket.speed_x = 8 + random.uniform(-1, 1)
                rocket.damage *= damage_mult
                self.rockets.append(rocket)
            self.ability_cooldowns['8'] = 80
            
        # Homing Missile (9)
        if keys[pygame.K_9] and self.ability_cooldowns['9'] == 0:
            rocket = Rocket(self.x + self.width // 2, self.y, self.direction, target.y + target.height // 2)
            rocket.speed_x = 12
            rocket.damage = 25 * damage_mult
            self.rockets.append(rocket)
            self.ability_cooldowns['9'] = 100
            
        # Update cooldowns
        for key in self.ability_cooldowns:
            if self.ability_cooldowns[key] > 0:
                self.ability_cooldowns[key] -= 1
                
    def update_projectiles(self, target):
        for rocket in self.rockets:
            rocket.target_y = target.y + target.height // 2
            rocket.update()
        self.rockets = [r for r in self.rockets if r.active]
        
        # Update particles
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        # Generate flame particles during hypercharge
        if self.hypercharge_active and random.random() < 0.3:
            self.particles.append(Particle(
                self.x + random.randint(0, self.width),
                self.y + random.randint(0, self.height),
                random.choice([RED, ORANGE, YELLOW]),
                vel_x=random.uniform(-2, 2),
                vel_y=random.uniform(-3, -1),
                life=30
            ))
        
    def draw(self, screen):
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw character with hit flash
        if self.hit_cooldown > 0 and self.hit_cooldown % 4 < 2:
            color_offset = (50, 50, 50)
        elif self.hypercharge_active:
            # Flame glow during hypercharge
            color_offset = (random.randint(50, 100), random.randint(0, 30), 0)
        else:
            color_offset = (0, 0, 0)
            
        # Body
        body_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate(BLUE))
        pygame.draw.rect(screen, body_color, (self.x + 10, self.y + 30, 30, 40))
        
        # Hypercharge aura
        if self.hypercharge_active:
            pygame.draw.rect(screen, ORANGE, (self.x + 5, self.y + 25, 40, 50), 2)
        
        # Arms
        pygame.draw.rect(screen, body_color, (self.x, self.y + 35, 10, 25))
        pygame.draw.rect(screen, body_color, (self.x + 40, self.y + 35, 10, 25))
        
        # Legs
        leg_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate(GRAY))
        pygame.draw.rect(screen, leg_color, (self.x + 15, self.y + 70, 8, 15))
        pygame.draw.rect(screen, leg_color, (self.x + 27, self.y + 70, 8, 15))
        
        # Regular head base
        head_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate((255, 220, 180)))
        pygame.draw.circle(screen, head_color, (int(self.x + self.width // 2), int(self.y + 20)), 15)
        
        # Rocket head
        rocket_color = tuple(max(0, min(255, c + color_offset[i])) for i, c in enumerate(RED))
        pygame.draw.polygon(screen, rocket_color, [
            (self.x + self.width // 2 - 10, self.y + 5),
            (self.x + self.width // 2 + 10, self.y + 5),
            (self.x + self.width // 2 + 10, self.y - 15),
            (self.x + self.width // 2 - 10, self.y - 15)
        ])
        pygame.draw.polygon(screen, DARK_RED, [
            (self.x + self.width // 2 - 10, self.y - 15),
            (self.x + self.width // 2 + 10, self.y - 15),
            (self.x + self.width // 2, self.y - 25)
        ])
        
        # Rocket fins
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + self.width // 2 - 10, self.y + 5),
            (self.x + self.width // 2 - 15, self.y + 5),
            (self.x + self.width // 2 - 10, self.y - 5)
        ])
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + self.width // 2 + 10, self.y + 5),
            (self.x + self.width // 2 + 15, self.y + 5),
            (self.x + self.width // 2 + 10, self.y - 5)
        ])
        
        # Face
        eye_offset = 3 if self.direction > 0 else -3
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width // 2 - 5 + eye_offset), int(self.y + 18)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + self.width // 2 + 5 + eye_offset), int(self.y + 18)), 2)
        
        # Draw projectiles
        for rocket in self.rockets:
            rocket.draw(screen)


class Cloud:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        
    def update(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH + 100:
            self.x = -100
            
    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), 30)
        pygame.draw.circle(screen, WHITE, (int(self.x + 25), int(self.y)), 35)
        pygame.draw.circle(screen, WHITE, (int(self.x + 50), int(self.y)), 30)


class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.brightness = random.randint(100, 255)
        self.twinkle_speed = random.uniform(0.02, 0.05)
        self.phase = random.uniform(0, math.pi * 2)
        
    def update(self):
        self.phase += self.twinkle_speed
        self.brightness = int(150 + 105 * math.sin(self.phase))
        
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 2)

class PixelChicken:
    """Cute animated chicken walking around the background."""
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = 1 if random.random() < 0.5 else -1
        self.frame = random.randint(0, 60)

    def update(self):
        self.x += self.speed * self.direction
        self.frame += 1

        # Randomly turn around
        if random.random() < 0.003:
            self.direction *= -1

        # Wrap around screen
        if self.x < -40:
            self.x = SCREEN_WIDTH + 40
        elif self.x > SCREEN_WIDTH + 40:
            self.x = -40

    def draw(self, screen):
        walk_bob = math.sin(self.frame * 0.2) * 2

        body_x = int(self.x)
        body_y = int(self.y + walk_bob)

        # Body (rounded oval)
        pygame.draw.ellipse(screen, (250, 240, 200), (body_x, body_y, 20, 12))
        # Wing (animation flap)
        wing_offset = math.sin(self.frame * 0.4) * 2
        pygame.draw.ellipse(screen, (240, 220, 180), (body_x + 5, body_y + 3 + wing_offset, 10, 6))

        # Head
        head_x = body_x + (18 if self.direction > 0 else -8)
        pygame.draw.circle(screen, (255, 255, 230), (int(head_x), int(body_y + 2)), 6)

        # Beak
        beak_dir = 1 if self.direction > 0 else -1
        pygame.draw.polygon(screen, (255, 165, 0), [
            (head_x + 5 * beak_dir, body_y + 2),
            (head_x + 9 * beak_dir, body_y + 1),
            (head_x + 5 * beak_dir, body_y + 3)
        ])

        # Eye
        pygame.draw.circle(screen, BLACK, (int(head_x + 2 * beak_dir), int(body_y + 1)), 1)

        # Legs (motion alternating)
        leg_y = body_y + 12
        step_cycle = (self.frame // 10) % 2
        leg_offset = 1 if step_cycle == 0 else -1
        pygame.draw.line(screen, (180, 120, 0), (body_x + 6, leg_y), (body_x + 6, leg_y + 5 + leg_offset), 2)
        pygame.draw.line(screen, (180, 120, 0), (body_x + 14, leg_y), (body_x + 14, leg_y + 5 - leg_offset), 2)


class Candy:
    """Bright wrapped candies floating gently in background."""
    def __init__(self, x, y, drift):
        self.x = x
        self.y = y
        self.drift = drift
        self.color = random.choice([
            (255, 100, 150),
            (255, 160, 100),
            (230, 100, 255),
            (150, 200, 255),
            (120, 255, 150)
        ])
        self.spin = random.uniform(0, 2 * math.pi)
        self.spin_speed = random.uniform(0.01, 0.03)
        self.float_phase = random.uniform(0, 2 * math.pi)

    def update(self):
        self.spin += self.spin_speed
        self.y += math.sin(pygame.time.get_ticks() * 0.002 + self.float_phase) * 0.2
        self.x += self.drift
        if self.x > SCREEN_WIDTH + 30: self.x = -30
        if self.x < -30: self.x = SCREEN_WIDTH + 30

    def draw(self, screen):
        cx, cy = int(self.x), int(self.y)
        angle = self.spin
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        # Candy body (rotating ellipse)
        for i in range(2):  # create subtle 3D shade
            width = 10 - i
            height = 6 - i
            pygame.draw.ellipse(screen, self.color, (cx - width, cy - height, width * 2, height * 2))

        # Wrappers (triangle-like wings)
        wrapper_length = 6
        left_tip = (cx - cos_a * wrapper_length * 2, cy - sin_a * wrapper_length * 2)
        right_tip = (cx + cos_a * wrapper_length * 2, cy + sin_a * wrapper_length * 2)
        pygame.draw.polygon(screen, (255, 255, 255, 180), [
            (cx, cy - 3), left_tip, (cx, cy + 3)
        ])
        pygame.draw.polygon(screen, (255, 255, 255, 180), [
            (cx, cy - 3), right_tip, (cx, cy + 3)
        ])

        # Wrapper shine
        if int(pygame.time.get_ticks() / 200) % 2 == 0:
            pygame.draw.line(screen, WHITE, (cx - 3, cy - 1), (cx + 3, cy - 1), 1)

def draw_health_bar(screen, x, y, health, max_health, name):
    pygame.draw.rect(screen, BLACK, (x - 2, y - 2, 204, 24))
    pygame.draw.rect(screen, DARK_RED, (x, y, 200, 20))
    
    health_width = int((health / max_health) * 200)
    if health > 60:
        color = GREEN
    elif health > 30:
        color = YELLOW
    else:
        color = RED
    pygame.draw.rect(screen, color, (x, y, health_width, 20))
    pygame.draw.rect(screen, BLACK, (x, y, 200, 20), 2)
    
    font = pygame.font.Font(None, 24)
    text = font.render(f"{name}: {int(health)}/{max_health}", True, WHITE)
    screen.blit(text, (x + 5, y + 2))


def draw_cooldown_indicators(screen, character, x, y):
    font = pygame.font.Font(None, 20)
    
    if isinstance(character, Telesheepy):
        abilities = [
            ('1: Lightning', character.ability_cooldowns['1'], 40),
            ('2: Storm', character.ability_cooldowns['2'], 80),
            ('3: Wave', character.ability_cooldowns['3'], 60),
            ('4: HYPERCHARGE', character.hypercharge_cooldown, 900)
        ]
    else:
        abilities = [
            ('7: Rocket', character.ability_cooldowns['7'], 40),
            ('8: Barrage', character.ability_cooldowns['8'], 80),
            ('9: Homing', character.ability_cooldowns['9'], 100),
            ('0: HYPERCHARGE', character.hypercharge_cooldown, 900)
        ]
    
    for i, (name, cooldown, max_cooldown) in enumerate(abilities):
        y_pos = y + i * 25
        bar_width = 100
        
        pygame.draw.rect(screen, BLACK, (x - 1, y_pos - 1, bar_width + 2, 12))
        
        is_hypercharge = 'HYPERCHARGE' in name
        
        if cooldown > 0:
            remaining_width = int((cooldown / max_cooldown) * bar_width)
            pygame.draw.rect(screen, RED, (x, y_pos, bar_width, 10))
            pygame.draw.rect(screen, GRAY, (x, y_pos, remaining_width, 10))
        else:
            color = GOLD if is_hypercharge else GREEN
            pygame.draw.rect(screen, color, (x, y_pos, bar_width, 10))
            
            # Pulsing effect for ready hypercharge
            if is_hypercharge and int(pygame.time.get_ticks() / 200) % 2:
                pygame.draw.rect(screen, WHITE, (x, y_pos, bar_width, 10), 2)
        
        pygame.draw.rect(screen, BLACK, (x, y_pos, bar_width, 10), 1)
        
        text_color = GOLD if is_hypercharge else WHITE
        text = font.render(name, True, text_color)
        screen.blit(text, (x + bar_width + 5, y_pos - 2))


def draw_background(screen, clouds, stars, chickens, candies):
    # Sky gradient
    for i in range(GROUND):
        progress = i / GROUND
        r = int(135 - 100 * progress)
        g = int(206 - 50 * progress)
        b = int(235 - 20 * progress)
        pygame.draw.line(screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

    # Stars
    for star in stars:
        star.update()
        star.draw(screen)

    # Mountains
    mountain_points = [
        (0, GROUND),
        (200, GROUND - 150),
        (400, GROUND - 100),
        (600, GROUND - 180),
        (800, GROUND - 120),
        (SCREEN_WIDTH, GROUND - 80),
        (SCREEN_WIDTH, GROUND)
    ]
    pygame.draw.polygon(screen, (60, 80, 100), mountain_points)
    pygame.draw.polygon(screen, (40, 60, 80), mountain_points, 3)

    # 🎨 Candies and Chickens before clouds
    for candy in candies:
        candy.update()
        candy.draw(screen)

    for chicken in chickens:
        chicken.update()
        chicken.draw(screen)

    # Clouds
    for cloud in clouds:
        cloud.update()
        cloud.draw(screen)

    # Ground
    pygame.draw.rect(screen, (34, 139, 34), (0, GROUND, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND))
    for i in range(0, SCREEN_WIDTH, 20):
        grass_height = random.randint(3, 8)
        pygame.draw.line(screen, (20, 120, 20), (i, GROUND), (i, GROUND - grass_height), 2)
    pygame.draw.rect(screen, (20, 100, 20), (0, GROUND, SCREEN_WIDTH, 5))

def main():
    # Initialize background elements HERE inside main()
    clouds = [Cloud(random.randint(0, SCREEN_WIDTH), random.randint(50, 150), random.uniform(0.2, 0.5)) for _ in range(5)]
    stars = [Star(random.randint(0, SCREEN_WIDTH), random.randint(0, GROUND - 100)) for _ in range(50)]
    # Add pixel chickens and candies
    # Add pixel chickens and candies
    chickens = [
        PixelChicken(random.randint(0, SCREEN_WIDTH), GROUND - random.randint(20, 90), random.uniform(0.3, 0.7))
        for _ in range(3)
    ]
    candies = [
        Candy(random.randint(0, SCREEN_WIDTH), random.randint(80, GROUND - 200), random.uniform(-0.15, 0.15))
        for _ in range(8)
    ]


    player1 = Telesheepy(100, GROUND - 80, {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'up': pygame.K_w,
        'down': pygame.K_s
    })
    
    player2 = RocketHair(SCREEN_WIDTH - 150, GROUND - 80, {
        'left': pygame.K_j,
        'right': pygame.K_l,
        'up': pygame.K_i,
        'down': pygame.K_k
    })
    
    running = True
    game_over = False
    winner = None
    frame_count = 0
    screen_shake = 0
    
    while running:
        clock.tick(FPS)
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_r:
                    player1.health = 100
                    player2.health = 100
                    player1.x = 100
                    player2.x = SCREEN_WIDTH - 150
                    player1.y = GROUND - 80
                    player2.y = GROUND - 80
                    player1.lightnings = []
                    player2.rockets = []
                    player1.particles = []
                    player2.particles = []
                    player1.ability_cooldowns = {'1': 0, '2': 0, '3': 0}
                    player2.ability_cooldowns = {'7': 0, '8': 0, '9': 0}
                    player1.hypercharge_ready = True
                    player2.hypercharge_ready = True
                    player1.hypercharge_cooldown = 0
                    player2.hypercharge_cooldown = 0
                    player1.hypercharge_active = False
                    player2.hypercharge_active = False
                    game_over = False
                    winner = None
        
        if not game_over:
            keys = pygame.key.get_pressed()
            
            player1.move(keys)
            player2.move(keys)
            
            player1.use_ability(keys)
            player2.use_ability(keys, player1)
            
            player1.update_projectiles()
            player2.update_projectiles(player1)
            
            # Screen shake during hypercharge
            if player1.hypercharge_active or player2.hypercharge_active:
                screen_shake = random.randint(-3, 3)
            else:
                screen_shake = 0
            
            for lightning in player1.lightnings:
                if lightning.get_rect().colliderect(player2.get_rect()):
                    player2.take_damage(lightning.damage)
                    lightning.active = False
            
            for rocket in player2.rockets:
                if rocket.get_rect().colliderect(player1.get_rect()):
                    player1.take_damage(rocket.damage)
                    rocket.active = False
            
            if player1.health <= 0:
                game_over = True
                winner = "Rocket Hair"
            elif player2.health <= 0:
                game_over = True
                winner = "Telesheepy"
        
        # Apply screen shake
        shake_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        shake_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        
        # Clear screen
        screen.fill(BLACK)
        
        # Create a surface to draw everything on, then blit it with shake offset
        game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Drawing to game surface
        draw_background(game_surface, clouds, stars, chickens, candies)
        
        player1.draw(game_surface)
        player2.draw(game_surface)
        
        draw_health_bar(game_surface, 20, 20, player1.health, player1.max_health, "Telesheepy")
        draw_health_bar(game_surface, SCREEN_WIDTH - 220, 20, player2.health, player2.max_health, "Rocket Hair")
        
        draw_cooldown_indicators(game_surface, player1, 20, 60)
        draw_cooldown_indicators(game_surface, player2, SCREEN_WIDTH - 220, 60)
        
        font_small = pygame.font.Font(None, 18)
        help_text1 = font_small.render("P1: WASD=Move, 1/2/3=Skills, 4=HYPERCHARGE", True, WHITE)
        help_text2 = font_small.render("P2: IJKL=Move, 7/8/9=Skills, 0=HYPERCHARGE", True, WHITE)
        
        pygame.draw.rect(game_surface, BLACK, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 50, 360, 45))
        game_surface.blit(help_text1, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT - 45))
        game_surface.blit(help_text2, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT - 25))
        
        if game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            game_surface.blit(overlay, (0, 0))
            
            font_large = pygame.font.Font(None, 72)
            winner_text = font_large.render(f"{winner} WINS!", True, GOLD)
            text_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            game_surface.blit(winner_text, text_rect)
            
            font_medium = pygame.font.Font(None, 36)
            restart_text = font_medium.render("Press R to Restart or ESC to Quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            game_surface.blit(restart_text, restart_rect)
        
        # Blit the entire game surface to screen with shake offset
        screen.blit(game_surface, (shake_x, shake_y))
        pygame.display.flip()
    
    pygame.quit()


if __name__ == "__main__":
    main()