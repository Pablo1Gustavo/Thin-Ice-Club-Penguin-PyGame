from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from .tile import TileType

if TYPE_CHECKING:
    from .game import Game
    from .player import Player


TILE_SIZE = 50
HUD_HEIGHT = 70
HEART_SIZE = 48
BOARD_WIDTH = 19
BOARD_HEIGHT = 15
WINDOW_SIZE = (BOARD_WIDTH * TILE_SIZE, BOARD_HEIGHT * TILE_SIZE + HUD_HEIGHT)

PLAYER_FRAME_DURATION_MS = 180
TILE_FRAME_DURATION_MS = 240
MOVEMENT_DURATION_MS = 150
ICE_MELT_DURATION_MS = 500
FALL_DURATION_MS = 1000
LEVEL_TRANSITION_DURATION_MS = 900

ICE_COLOR = (230, 253, 255)
SCORE_COLOR = (30, 60, 150)
HUD_COLOR = (215, 244, 255)
HUD_BORDER_COLOR = (77, 166, 224)


class Render:
    @staticmethod
    def smoothstep(progress: float) -> float:
        return progress * progress * (3 - 2 * progress)

    def __init__(self, screen: pygame.Surface, root: Path) -> None:
        self.screen = screen
        self.animation_elapsed_ms = 0
        self.font = pygame.font.Font(root / "Fonts/Pixeled.ttf", 24)
        self.end_font = pygame.font.Font(None, 48)
        self.fade_overlay = pygame.Surface(WINDOW_SIZE).convert()
        self.fade_overlay.fill((0, 0, 0))

        textures = root / "Textures"
        self.player_images = [
            pygame.transform.smoothscale(
                pygame.image.load(textures / "Player" / f"Player_{index:02d}.png").convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            )
            for index in range(1, 4)
        ]
        self.heart_image = pygame.transform.smoothscale(
            pygame.image.load(textures / "Heart.png").convert_alpha(),
            (HEART_SIZE, HEART_SIZE),
        )

        def load_tile_frames(name: str, count: int = 1) -> list[pygame.Surface]:
            paths = (
                [textures / name / f"{name}_{index:02d}.png" for index in range(1, count + 1)]
                if count > 1
                else [textures / f"{name}.png"]
            )
            return [
                pygame.transform.scale(
                    pygame.image.load(path).convert_alpha(),
                    (TILE_SIZE, TILE_SIZE),
                )
                for path in paths
            ]

        self.tile_images = {
            TileType.EMPTY: load_tile_frames("EmptySquare"),
            TileType.WATER: load_tile_frames("Water", 3),
            TileType.ICE: load_tile_frames("Ice"),
            TileType.FINISH: load_tile_frames("FinishSquare", 3),
            TileType.WALL: load_tile_frames("Wall"),
            TileType.DOUBLE_ICE: load_tile_frames("DoubleIce"),
        }
        self.hud_text_values = None

    def reset_level(self, player: Player) -> None:
        self.move_start = (player.x * TILE_SIZE, player.y * TILE_SIZE)
        self.move_elapsed_ms = MOVEMENT_DURATION_MS
        self.melting_tiles = {}

    def player_position(self, player: Player) -> tuple[int, int]:
        progress = min(self.move_elapsed_ms / MOVEMENT_DURATION_MS, 1)
        eased = self.smoothstep(progress)
        target_x, target_y = player.x * TILE_SIZE, player.y * TILE_SIZE
        start_x, start_y = self.move_start
        return (
            round(start_x + (target_x - start_x) * eased),
            round(start_y + (target_y - start_y) * eased),
        )

    def start_move(self, player: Player, melted: bool) -> None:
        if melted:
            self.melting_tiles[player.x, player.y] = self.animation_elapsed_ms
        self.move_start = self.player_position(player)
        self.move_elapsed_ms = 0

    def advance(self, elapsed_ms: int) -> None:
        self.animation_elapsed_ms += elapsed_ms
        self.move_elapsed_ms = min(self.move_elapsed_ms + elapsed_ms, MOVEMENT_DURATION_MS)

    def draw(self, game: Game) -> None:
        tile_frame_index = self.animation_elapsed_ms // TILE_FRAME_DURATION_MS
        tile_frames = {
            kind: frames[tile_frame_index % len(frames)]
            for kind, frames in self.tile_images.items()
        }
        for y, row in enumerate(game.level.tiles):
            for x, tile in enumerate(row):
                position = (x * TILE_SIZE, y * TILE_SIZE)
                self.screen.blit(tile_frames[tile.kind], position)
                if tile.kind is TileType.WATER and (x, y) in self.melting_tiles:
                    elapsed = self.animation_elapsed_ms - self.melting_tiles[x, y]
                    if elapsed >= ICE_MELT_DURATION_MS:
                        del self.melting_tiles[x, y]
                    else:
                        alpha = round(255 * (1 - self.smoothstep(elapsed / ICE_MELT_DURATION_MS)))
                        ice_overlay = tile_frames[TileType.ICE].copy()
                        ice_overlay.set_alpha(alpha)
                        self.screen.blit(ice_overlay, position)

        hud_y = BOARD_HEIGHT * TILE_SIZE
        pygame.draw.rect(self.screen, HUD_COLOR, (0, hud_y, WINDOW_SIZE[0], HUD_HEIGHT))
        pygame.draw.rect(self.screen, HUD_BORDER_COLOR, (0, hud_y, WINDOW_SIZE[0], 4))
        heart_rect = self.heart_image.get_rect(topleft=(24, hud_y + (HUD_HEIGHT - HEART_SIZE) // 2))
        self.screen.blit(self.heart_image, heart_rect)
        hud_text_values = (game.score, game.player.lives)
        if hud_text_values != self.hud_text_values:
            self.score_text = self.font.render(f"SCORE: {game.score}", True, SCORE_COLOR)
            self.lives_text = self.font.render(f"x{game.player.lives}", True, SCORE_COLOR)
            self.hud_text_values = hud_text_values
        self.screen.blit(self.score_text, self.score_text.get_rect(midright=(WINDOW_SIZE[0] - 32, hud_y + HUD_HEIGHT // 2)))
        self.screen.blit(self.lives_text, self.lives_text.get_rect(midleft=(heart_rect.right + 16, hud_y + HUD_HEIGHT // 2)))

        frame_index = (self.animation_elapsed_ms // PLAYER_FRAME_DURATION_MS) % len(self.player_images)
        player_image = self.player_images[frame_index]
        player_position = self.player_position(game.player)
        if game.fall_elapsed_ms is not None:
            shrink_progress = max(0, (game.fall_elapsed_ms - MOVEMENT_DURATION_MS) / (FALL_DURATION_MS - MOVEMENT_DURATION_MS))
            size = max(1, round(TILE_SIZE * (1 - shrink_progress**2)))
            player_image = pygame.transform.smoothscale(player_image, (size, size))
            player_position = player_image.get_rect(
                center=(player_position[0] + TILE_SIZE // 2, player_position[1] + TILE_SIZE // 2)
            )
        self.screen.blit(player_image, player_position)

        if game.won:
            message = self.end_font.render("You won! R: restart   Esc: quit", True, SCORE_COLOR)
            box = message.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            pygame.draw.rect(self.screen, ICE_COLOR, box.inflate(20, 16))
            self.screen.blit(message, box)

        if game.transition_elapsed_ms is not None:
            midpoint = LEVEL_TRANSITION_DURATION_MS // 2
            progress = min(game.transition_elapsed_ms, LEVEL_TRANSITION_DURATION_MS - game.transition_elapsed_ms) / midpoint
            self.fade_overlay.set_alpha(round(255 * self.smoothstep(progress)))
            self.screen.blit(self.fade_overlay, (0, 0))

        pygame.display.flip()
