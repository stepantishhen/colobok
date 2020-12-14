import pygame

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 864, 672
TILE_SIZE = 32
FPS = 15
MYEVENTTYPE = pygame.USEREVENT + 1


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

    def render(self, screen):
        colors = {'.': pygame.Color('#BAE6FC'), '#': pygame.Color('#FCCE08')}
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size,
                                   self.tile_size, self.tile_size)
                screen.fill(colors[self.get_tile_id((x, y))], rect)

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tile

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


class Game:
    def __init__(self, map, colobok, enemy):
        self.map = map
        self.colobok = colobok
        self.enemy = enemy

    def render(self, screen):
        self.map.render(screen)
        self.colobok.render(screen)
        self.enemy.render(screen)

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

    def move_enemy(self):
        next_position = self.map.find_path_step(self.enemy.get_position(),
                                                self.colobok.get_position())
        self.enemy.set_position(next_position)

    def check_lose(self):
        return self.colobok.get_position() == self.enemy.get_position()


class Enemy:
    def __init__(self, pic, position):
        self.x, self.y = position
        self.delay = 100
        pygame.time.set_timer(MYEVENTTYPE, self.delay)
        self.image = pygame.image.load(f"images/{pic}")

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image,
                    (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))


class Colobok:
    def __init__(self, pic, position):
        self.x, self.y = position
        self.image = pygame.image.load(f"images/{pic}")

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image,
                    (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))


def show_message(screen, message):
    font = pygame.font.Font('font/elizabeta-modern.ttf', 60)
    text = font.render(message, 1, (255, 255, 255))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (255, 0, 0), (text_x - 10, text_y - 10,
                                           text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


def main_window():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Колобок')
    icon = pygame.image.load('images/colobok.png')
    pygame.display.set_icon(icon)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False
                game_window()
        screen.fill(pygame.Color('#BAE6FC'))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


def game_window():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption('Колобок')
    icon = pygame.image.load('images/colobok.png')
    pygame.display.set_icon(icon)

    labyrint = Labyrint("map.txt", '.', '#')
    colobok = Colobok("colobok.png", (13, 15))
    enemy = Enemy("enemy.png", (13, 9))
    game = Game(labyrint, colobok, enemy)

    clock = pygame.time.Clock()
    running = True
    game_over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == MYEVENTTYPE and not game_over:
                game.move_enemy()
        if not game_over:
            game.update_colobok()
        screen.fill(pygame.Color('#BAE6FC'))
        game.render(screen)
        if game.check_lose():
            game_over = True
            show_message(screen, 'Ты проиграл!')
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    main_window()
