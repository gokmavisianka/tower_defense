import pygame
from threading import Thread
from time import sleep
from math import atan2, pi, sin, cos
from random import randint, choice


rad_to_deg = 180 / pi

def random_color():
    return tuple(randint(100, 255) for code in "rgb")


class Window:
    def __init__(self, width, height, color):
        self.resolution.width = width
        self.resolution.height = height
        self.center.x = width // 2
        self.center.y = height // 2
        self.color = color
        self.screen = pygame.display.set_mode((width, height))
        self.fill()

    def fill(self):
        self.screen.fill(self.color)

    class center:
        x = y = 0

    class resolution:
        width = height = 0

class Game:
    def __init__(self):
        self.window = Window(1000, 1000, color=(0, 0, 0))
        self.enemies = []
        self.bullets = []
        self.keep_running = True
        self.fps = 120
        self.planet = self.Planet(self)
        Thread(target=self.draw_and_update).start()
        Thread(target=self.spawn).start()

    def spawn(self, count=1):
        while self.keep_running is True:
            for number in range(count):
                self.Enemy(self)
            sleep(2)

    def draw_and_update(self):
        delay = 1 / self.fps
        while self.keep_running is True:
            self.window.fill()
            pygame.draw.rect(self.window.screen, self.planet.color, (self.planet.x, self.planet.y, self.planet.size, self.planet.size))
            for bullet in self.bullets:
                pygame.draw.rect(self.window.screen, bullet.color, (bullet.x, bullet.y, bullet.size, bullet.size))
            for enemy in self.enemies:
                pygame.draw.rect(self.window.screen, enemy.color, (enemy.x, enemy.y, enemy.size, enemy.size))
            pygame.display.flip()
            sleep(delay)

    class Enemy:
        def __init__(self, game):
            self.color = random_color()
            self.game = game
            self.planet = game.planet
            self.size = 10 * randint(3, 6)
            x1 = choice((0 - self.size, game.window.resolution.width + self.size))
            y1 = randint(-200, game.window.resolution.height + 200)
            x2 = randint(-200, game.window.resolution.width + 200)
            y2 = choice((0 - self.size, game.window.resolution.height + self.size))
            if randint(1, 2) == 1:
                self.x, self.y = x1, y1
            else:
                self.x, self.y = x2, y2
            self.health = self.size // 10
            self.speed = 50
            self.game.enemies.append(self)
            Thread(target=self.move).start()

        def move(self):
            delay = (1 / self.game.fps)
            angle = atan2((self.planet.y - self.y), (self.planet.x - self.x))
            velocity_x = (cos(angle) * self.speed) / self.game.fps
            velocity_y = (sin(angle) * self.speed) / self.game.fps
            while self.health > 0:
                self.x += velocity_x
                self.y += velocity_y
                self.check_collision()
                sleep(delay)
            self.game.enemies.remove(self)

        def take_damage(self, damage):
            self.health -= damage

        def check_collision(self):
            for corner_x in (self.x, (self.x + self.size)):
                for corner_y in (self.y, (self.y + self.size)):
                    condition = ((self.planet.x <= corner_x <= self.planet.x + self.planet.size) and (self.planet.y <= corner_y <= self.planet.y + self.planet.size))
                    if condition is True:
                        self.health = 0
                        print("BOOM!!!")

    class Planet:
        def __init__(self, game):
            self.size = 100
            self.x = (game.window.center.x) - (self.size // 2)
            self.y = (game.window.center.y) - (self.size // 2)
            self.bullet_count = 1
            self.attack_rate = 0.1
            self.attack_damage = 1
            self.accuracy = 50
            self.game = game
            self.color = (0, 0, 255)
            self.angle = self.target_angle = 0
            Thread(target=self.shoot).start()
            Thread(target=self.rotate).start()

        def choose_target(self):
            enemies = self.game.enemies[::]
            if len(enemies) > 0:
                # return choice(enemies)
                distances = []
                for enemy in enemies:
                    _x_ = ((enemy.x + enemy.size // 2) - (self.x + self.size // 2))
                    _y_ = ((enemy.y + enemy.size // 2) - (self.y + self.size // 2))
                    distance = (_x_ * _x_ + _y_ * _y_) ** (0.5)
                    distances.append(distance)
                minimum_distance = min(distances)
                closest_target = enemies[distances.index(minimum_distance)]
                return closest_target
            else:
                return None

        def shoot(self):
            while self.game.keep_running is True:
                target = self.choose_target()
                if target is not None:
                    _x_ = (target.x + target.size // 2)
                    _y_ = (target.y + target.size // 2)
                    self.target_angle = atan2((_y_ - self.y), (_x_ - self.x))
                    for bullet in range(self.bullet_count):
                        self.Bullet(self.game, target)
                sleep(self.attack_rate)

        def rotate(self):
            delay = (1 / self.game.fps)
            while self.game.keep_running is True:
                self.target_angle = round(self.target_angle, 1)
                angle = round(self.angle, 1)
                if angle < self.target_angle:
                    self.angle += 0.05
                elif angle > self.target_angle:
                    self.angle -= 0.05
                sleep(0.02)

        class Bullet:
            def __init__(self, game, target):
                self.game = game
                self.planet = game.planet
                self.target = target
                self.color = (255, 255, 0)  # yellow
                self.x = (self.planet.x + (self.planet.size // 2))
                self.y = (self.planet.y + (self.planet.size // 2))
                self.size = 10
                self.speed = 300
                self.hit = False
                self.game.bullets.append(self)
                Thread(target=self.move).start()

            def move(self):
                delay = (1 / self.game.fps)
                lim = 110 - self.planet.accuracy
                _x_ = (self.target.x + self.target.size // 2) + (randint(-lim, lim))
                _y_ = (self.target.y + self.target.size // 2) + (randint(-lim, lim))
                angle = (atan2((_y_ - self.y), (_x_ - self.x)) - self.planet.target_angle) + self.planet.angle
                velocity_x = (cos(angle) * self.speed) / self.game.fps
                velocity_y = (sin(angle) * self.speed) / self.game.fps
                while self.hit is False:
                    self.x += velocity_x
                    self.y += velocity_y
                    self.check_collision()
                    sleep(delay)
                self.game.bullets.remove(self)

            def check_collision(self):
                if (0 <= self.x <= self.game.window.resolution.width) and (0 <= self.y <= self.game.window.resolution.height):
                    for enemy in self.game.enemies:
                        for corner_x in (self.x, (self.x + self.size)):
                            for corner_y in (self.y, (self.y + self.size)):
                                condition = ((enemy.x <= corner_x <= enemy.x + enemy.size) and (enemy.y <= corner_y <= enemy.y + enemy.size))
                                if condition is True:
                                    enemy.take_damage(self.planet.attack_damage)
                                    self.hit = True
                                    return None
                else:
                    self.hit = True


game = Game()
clicked = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.keep_running = False
            sleep(1)
            pygame.quit()
            quit()
            
        buttons = pygame.mouse.get_pressed()
        if buttons[0] == True:
            if clicked == False:
                position = pygame.mouse.get_pos()
                clicked = True
        else:
            clicked = False

    sleep(1 / game.fps)            
      
