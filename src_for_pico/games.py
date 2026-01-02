from machine import I2C,Pin,PWM,Timer,UART
from menu import MenuController
from ssd1306 import SSD1306_I2C
from math import ceil
from servo import Servo
import time, utime, sys
import random

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
OLED_I2C_ADDR = 0x3C

# snake config
SNAKE_PIECE_SIZE = 3
MAX_SNAKE_LENGTH = 150
MAP_SIZE_X = 20
MAP_SIZE_Y = 20
START_SNAKE_SIZE = 10
SNAKE_MOVE_DELAY = 5
# game config
class State(object):
    START = 0
    RUNNING = 1
    GAMEOVER = 2
    @classmethod
    def setter(cls, state):
        if state == cls.START:
            return cls.START
        elif state == cls.RUNNING:
            return cls.RUNNING
        elif state == cls.GAMEOVER:
            return cls.GAMEOVER
class Direction(object):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3
    @classmethod
    def setter(cls, dirc):
        if dirc == cls.UP:
            return cls.UP
        elif dirc == cls.DOWN:
            return cls.DOWN
        elif dirc == cls.LEFT:
            return cls.LEFT
        elif dirc == cls.RIGHT:
            return cls.RIGHT
class Snake(object):
    def __init__(self, oled, UP_PIN,DOWN_PIN,LEFT_PIN,RIGHT_PIN):
        self.snake = []
        self.fruit = []
        self.snake_length = START_SNAKE_SIZE
        self.direction = Direction.RIGHT
        self.new_direction = Direction.RIGHT
        self.game_state = None
        self.oled = oled
        self.setup_game()
        self.UP_PIN = UP_PIN
        self.DOWN_PIN = DOWN_PIN
        self.LEFT_PIN = LEFT_PIN
        self.RIGHT_PIN = RIGHT_PIN
    def setup_game(self):
        self.game_state = State.START
        direction = Direction.RIGHT
        new_direction = Direction.RIGHT
        self.reset_snake()
        self.generate_fruit()
#         self.oled.fill(0)
        self.draw_map()
        self.show_score()
        self.show_press_to_start()
#         self.oled.show()
    def reset_snake(self):
        self.snake = []
        self.snake_length = START_SNAKE_SIZE
        for i in range(self.snake_length):
            self.snake.append((MAP_SIZE_X // 2 - i, MAP_SIZE_Y // 2))
    def check_fruit(self):
        if self.snake[0][0] == self.fruit[0] and self.snake[0][1] == self.fruit[1]:
            if self.snake_length + 1 < MAX_SNAKE_LENGTH:
                self.snake_length += 1
                self.snake.insert(0, (self.fruit[0], self.fruit[1]))
            self.generate_fruit()
    def generate_fruit(self):
        while True:
            self.fruit = [random.randint(1, MAP_SIZE_X - 1), random.randint(1, MAP_SIZE_Y - 1)]
            fruit = tuple(self.fruit)
            if fruit in self.snake:
                continue
            else:
                break
    @staticmethod
    def button_press():
        for pin in self.UP_PIN, self.DOWN_PIN, self.LEFT_PIN, self.RIGHT_PIN:
            if pin.value() == 0:
                return True
        return False
    def read_direction(self):
        for direction, pin in enumerate((self.UP_PIN, self.LEFT_PIN, self.DOWN_PIN, self.RIGHT_PIN)):
            if pin.value() == 0 and not (direction == (self.direction + 2) % 4):
                self.new_direction = Direction.setter(direction)
                return
    def collection_check(self, x, y):
        for i in self.snake:
            if x == i[0] and y == i[1]:
                return True
        if x < 0 or y < 0 or x >= MAP_SIZE_X or y >= MAP_SIZE_Y:
            return True
        return False
    def move_snake(self):
        x, y = self.snake[0]
        new_x, new_y = x, y
        if self.direction == Direction.UP:
            new_y -= 1
        elif self.direction == Direction.DOWN:
            new_y += 1
        elif self.direction == Direction.LEFT:
            new_x -= 1
        elif self.direction == Direction.RIGHT:
            new_x += 1
        if self.collection_check(new_x, new_y):
            return False
        self.snake.pop()
        self.snake.insert(0, (new_x, new_y))
        return True
    def draw_map(self):
        offset_map_x = SCREEN_WIDTH - SNAKE_PIECE_SIZE * MAP_SIZE_X - 2
        offset_map_y = 2
        self.oled.rect(self.fruit[0] * SNAKE_PIECE_SIZE + offset_map_x,
                          self.fruit[1] * SNAKE_PIECE_SIZE + offset_map_y,
                          SNAKE_PIECE_SIZE, SNAKE_PIECE_SIZE, 1)
        self.oled.rect(offset_map_x - 2,
                          0,
                          SNAKE_PIECE_SIZE * MAP_SIZE_X + 4,
                          SNAKE_PIECE_SIZE * MAP_SIZE_Y + 4, 1)
        for x, y in self.snake:
            self.oled.fill_rect(x * SNAKE_PIECE_SIZE + offset_map_x,
                                   y * SNAKE_PIECE_SIZE + offset_map_y,
                                   SNAKE_PIECE_SIZE,
                                   SNAKE_PIECE_SIZE, 1)
    def show_score(self):
        score = self.snake_length - START_SNAKE_SIZE
        self.oled.text('Score:%d' % score, 0, 2, 1)
    def show_press_to_start(self):
        self.oled.text('Press', 0, 16, 1)
        self.oled.text('button', 0, 26, 1)
        self.oled.text('start!', 0, 36, 1)
    def show_game_over(self):
        self.oled.text('Game', 0, 30, 1)
        self.oled.text('Over!', 0, 40, 1)