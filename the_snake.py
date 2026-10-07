"""Игра «Изгиб Питона»: классическая змейка на Pygame."""
import sys
from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр игрового поля:
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
LIGHT_BLUE = (93, 216, 228)

BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = LIGHT_BLUE
APPLE_COLOR = RED
SNAKE_COLOR = GREEN

# Скорость движения змейки:
SPEED = 20

# Повороты: клавиша -> (новое направление, запрещённое направление):
TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT),
}

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=SCREEN_CENTER, body_color=None):
        """Задаёт позицию и цвет объекта.

        Args:
            position: позиция объекта (по умолчанию центр игрового поля).
            body_color: цвет объекта.
        """
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на игровом поле.

        Метод должен быть переопределён в дочерних классах.

        Raises:
            NotImplementedError: если метод не переопределён.
        """
        raise NotImplementedError(
            f'Метод draw не переопределён в классе {type(self).__name__}'
        )

    def draw_cell(
        self,
        position,
        body_color=None,
        border_color=BORDER_COLOR,
    ):
        """Отрисовывает одну ячейку игрового поля.

        Args:
            position: координаты левого верхнего угла ячейки.
            body_color: цвет заливки (по умолчанию цвет объекта).
            border_color: цвет границы ячейки, None - без границы.
        """
        if body_color is None:
            body_color = self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, body_color, rect)
        if border_color is not None:
            pg.draw.rect(screen, border_color, rect, 1)


class Apple(GameObject):
    """Яблоко, которое змейка должна съесть."""

    def __init__(self, occupied_positions=(), body_color=APPLE_COLOR):
        """Задаёт цвет яблока и выбирает для него случайную позицию.

        Args:
            occupied_positions: занятые клетки, где яблоко не появится.
            body_color: цвет яблока.
        """
        super().__init__(body_color=body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Устанавливает случайную позицию яблока на игровом поле.

        Args:
            occupied_positions: занятые клетки (например, тело змейки),
                в которых яблоко не должно появляться.
        """
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка, управляемая игроком."""

    def __init__(self, position=SCREEN_CENTER, body_color=SNAKE_COLOR):
        """Задаёт начальное состояние змейки.

        Args:
            position: начальная позиция головы.
            body_color: цвет змейки.
        """
        super().__init__(position, body_color)
        self.reset()

    def update_direction(self):
        """Обновляет направление движения после нажатия на клавишу."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает змейку на одну клетку в текущем направлении.

        Новая голова добавляется в начало списка positions. Последний
        сегмент удаляется, если змейка не выросла. При выходе за границу
        поля змейка появляется с противоположной стороны.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает голову змейки и затирает след от хвоста.

        Остальные сегменты не перерисовываются: они уже нарисованы
        на предыдущих шагах.
        """
        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, None)
        self.draw_cell(self.get_head_position())

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def quit_game():
    """Закрывает окно Pygame и завершает программу."""
    pg.quit()
    sys.exit()


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и закрытие окна.

    Стрелки меняют направление змейки (разворот на 180 градусов
    запрещён), клавиша Esc и закрытие окна завершают игру.

    Args:
        game_object: змейка, у которой меняется направление.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit_game()
        if event.type != pg.KEYDOWN:
            continue
        if event.key == pg.K_ESCAPE:
            quit_game()
        if event.key in TURNS:
            new_direction, opposite = TURNS[event.key]
            if game_object.direction != opposite:
                game_object.next_direction = new_direction


def main():
    """Запускает основной цикл игры."""
    # Инициализация PyGame:
    pg.init()

    snake = Snake()
    apple = Apple(snake.positions)

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()

        if head == apple.position:
            # Змейка съела яблоко: растём и переносим яблоко.
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif head in snake.positions[1:]:
            # Змейка столкнулась с собой: игра начинается заново.
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pg.display.update()


if __name__ == '__main__':
    main()