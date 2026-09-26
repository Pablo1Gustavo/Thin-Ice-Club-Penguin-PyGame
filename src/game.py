from pathlib import Path

import pygame

from .level import Level
from .player import Player
from .tile import TileType


ROOT = Path(__file__).resolve().parent.parent

TILE_SIZE = 20
BOARD_WIDTH = 19
BOARD_HEIGHT = 15
WINDOW_SIZE = (BOARD_WIDTH * TILE_SIZE, BOARD_HEIGHT * TILE_SIZE + 30)
ICE_COLOR = (230, 253, 255)
SCORE_COLOR = (0, 0, 255)
TEXT_COLOR = (0, 0, 0)

DIRECTIONS = {
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
}


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Thin Ice")
        self.font = pygame.font.Font(ROOT / "Fonts/Pixeled.ttf", 9)
        self.end_font = pygame.font.Font(None, 28)

        textures = ROOT / "Textures"
        self.player_image = pygame.image.load(textures / "Player.png").convert_alpha()
        self.score_image = pygame.image.load(textures / "score_screen.png").convert()
        self.tile_images = {
            TileType.EMPTY: pygame.image.load(textures / "EmptySquare.png").convert(),
            TileType.WATER: pygame.image.load(textures / "Water.png").convert(),
            TileType.FINISH: pygame.image.load(textures / "FinishSquare.png").convert(),
            TileType.WALL: pygame.image.load(textures / "Wall.png").convert(),
            TileType.DOUBLE_ICE: pygame.image.load(textures / "DoubleIce.png").convert(),
        }
        ice = pygame.Surface((TILE_SIZE, TILE_SIZE))
        ice.fill(ICE_COLOR)
        self.tile_images[TileType.ICE] = ice

        pygame.mixer.music.load(ROOT / "Sounds/GameMusic.mp3")
        pygame.mixer.music.set_volume(0.65)
        pygame.mixer.music.play(-1)

        self.level_paths = sorted(
            (ROOT / "Levels").glob("level*.toml"),
            key=lambda path: int(path.stem.removeprefix("level")),
        )
        self.restart()

    def restart(self) -> None:
        self.score = 0
        self.level_score = 0
        self.level_index = 0
        self.won = False
        self.player = Player(0, 0)
        self.load_level()

    def load_level(self) -> None:
        self.level = Level(self.level_paths[self.level_index])
        self.player.reset_position(*self.level.start)

    def move_player(self, dx: int, dy: int) -> None:
        x, y = self.player.x + dx, self.player.y + dy
        destination = self.level.tile_at(x, y)
        if destination is None or not destination.walkable:
            return

        points = self.level.tile_at(self.player.x, self.player.y).leave()
        self.score += points
        self.level_score += points
        self.player.move(dx, dy)

        match destination.kind:
            case TileType.WATER:
                self.score -= self.level_score
                self.level_score = 0
                self.player.lose_life()
                if not self.player.is_alive():
                    self.restart()
                else:
                    self.load_level()
            case TileType.FINISH:
                self.level_score = 0
                self.level_index += 1
                if self.level_index == len(self.level_paths):
                    self.won = True
                else:
                    self.load_level()

    def draw(self) -> None:
        for y, row in enumerate(self.level.tiles):
            for x, tile in enumerate(row):
                self.screen.blit(self.tile_images[tile.kind], (x * TILE_SIZE, y * TILE_SIZE))

        hud_y = BOARD_HEIGHT * TILE_SIZE
        self.screen.blit(self.score_image, (0, hud_y))
        self.screen.blit(self.font.render(f"SCORE: {self.score}", True, SCORE_COLOR), (285, hud_y))
        self.screen.blit(self.font.render(f"x{self.player.lives}", True, TEXT_COLOR), (32, hud_y))
        self.screen.blit(self.player_image, (self.player.x * TILE_SIZE, self.player.y * TILE_SIZE))

        if self.won:
            message = self.end_font.render("You won! R: restart   Esc: quit", True, TEXT_COLOR)
            box = message.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            pygame.draw.rect(self.screen, ICE_COLOR, box.inflate(20, 16))
            self.screen.blit(message, box)

        pygame.display.flip()

    def run(self) -> None:
        running = True
        self.draw()
        while running:
            for event in (pygame.event.wait(), *pygame.event.get()):
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_ESCAPE:
                                running = False
                            case pygame.K_r if self.won:
                                self.restart()
                            case key if not self.won and key in DIRECTIONS:
                                self.move_player(*DIRECTIONS[key])
            if running:
                self.draw()

        pygame.quit()
