import pygame
import random

# Настройка
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 864, 672
TILE_SIZE = 32
FPS = 15
MYEVENTTYPE = pygame.USEREVENT + 1


# Лабиринт
class Labyrint:
    def __init__(self, filename, free_tile, wall_tile):
        self.map = []
        with open(f'{filename}') as input_file:
            for line in input_file:
                self.map.append(list(map(str, line.rstrip('\n'))))
        self.height = len(self.map)
        self.width = len(self.map[0])
        self.tile_size = TILE_SIZE
        self.free_tile = free_tile
        self.wall_tile = wall_tile

    # Отрисовка лабиринта
    def render(self, screen):
        colors = {'.': pygame.Color('#BAE6FC'), '#': pygame.Color('#FCCE08')}
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size,
                                   self.tile_size, self.tile_size)
                screen.fill(colors[self.get_tile_id((x, y))], rect)

    # Вернуть айди элемента карты
    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    # Проверка на свободность участка
    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tile

    # Построение короткого маршрута
    def find_path_step(self, start, target):
        INF = 1000
        x, y = start
        distance = [[INF] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 < next_y < self.height and \
                        self.is_free((next_x, next_y)) and \
                        distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y


# Класс игры
class Game:
    def __init__(self, map, colobok, enemy):
        self.map = map
        self.colobok = colobok
        self.enemy = enemy

    # Отрисовка всей игры
    def render(self, screen):
        self.map.render(screen)
        self.colobok.render(screen)
        self.enemy.render(screen)

    # Обновление игрока
    def update_colobok(self):
        next_x, next_y = self.colobok.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.map.is_free((next_x, next_y)):
            self.colobok.set_position((next_x, next_y))

    # Перемещение врага
    def move_enemy(self):
        next_position = self.map.find_path_step(self.enemy.get_position(),
                                                self.colobok.get_position())
        self.enemy.set_position(next_position)

    # Проверка проигрыша
    def check_lose(self):
        return self.colobok.get_position() == self.enemy.get_position()


# Враг
class Enemy:
    def __init__(self, pic, position):
        self.x, self.y = position
        self.delay = 120
        pygame.time.set_timer(MYEVENTTYPE, self.delay)
        self.image = pygame.image.load(f"images/{pic}")

    # Вернуть позицию врага
    def get_position(self):
        return self.x, self.y

    # Переместить врага
    def set_position(self, position):
        self.x, self.y = position

    # Отрисовка врага
    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image,
                    (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))


# Игрок
class Colobok:
    def __init__(self, pic, position):
        self.x, self.y = position
        self.image = pygame.image.load(f"images/{pic}")

    # Вернуть позицию игрока
    def get_position(self):
        return self.x, self.y

    # Переместить врага
    def set_position(self, position):
        self.x, self.y = position

    # Отрисовка игрока
    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image,
                    (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))


# Показать сообщение
def show_message(screen, message, position, size):
    font = pygame.font.Font('font/elizabeta-modern.ttf', size)
    text = font.render(message, 1, (251, 2, 3))
    screen.blit(text, position)


# Гланое окно игры
def main_window():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Колобок')
    icon = pygame.image.load('images/colobok.png')
    pygame.display.set_icon(icon)

    background_img = pygame.image.load('images/background-img.png')
    keyboard_img = pygame.image.load('images/keyboard.png')
    pygame.mixer.music.load('sounds/main_music.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1)

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False
                game_window()
                pygame.mixer.music.stop()
        screen.blit(background_img, [0, 0])
        screen.blit(keyboard_img, [0, 550])
        show_message(screen, 'Нажмите пробел, чтобы начать играть', (50, 10),
                     30)
        show_message(screen, 'Управление с помощью клавиш', (180, 610),
                     30)
        pygame.display.flip()
        clock.tick(FPS)


# Окно игры
def game_window():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Колобок')
    icon = pygame.image.load('images/colobok.png')
    pygame.display.set_icon(icon)

    pygame.mixer.music.load('sounds/colobok.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=1)
    pygame.mixer.music.queue('sounds/main_music.mp3')

    labyrint = Labyrint("map.txt", '.', '#')
    colobok = Colobok("colobok.png", (13, 15))
    enemy = Enemy("enemy.png", (13, 9))
    game = Game(labyrint, colobok, enemy)

    score = 0
    clock = pygame.time.Clock()
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MYEVENTTYPE and not game_over:
                game.move_enemy()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r \
                    and game_over:
                game_window()
        if not game_over:
            game.update_colobok()
            score += 1
        screen.fill(pygame.Color('#BAE6FC'))
        game.render(screen)
        show_message(screen, f'Очков: {score}', (0, 0), 25)
        if game.check_lose():
            pygame.mixer.music.stop()
            game_over = True
            show_message(screen, 'Съеден', (320, 300), 50)
            show_message(screen, 'Для рестарта нажмите R', (220, 370), 25)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    main_window()
