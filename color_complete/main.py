import math
import os
import random
import sys
import time
import base64
import zlib
from array import array
from dataclasses import dataclass
from enum import Enum

import pygame

from network import DEFAULT_WS_URL, NetworkClient


SCREEN_WIDTH = 1120
SCREEN_HEIGHT = 760
FPS = 60

BG = (255, 248, 230)
INK = (25, 28, 33)
MUTED = (94, 101, 114)
PANEL = (255, 255, 255)
BORDER = (204, 210, 219)
ACCENT = (255, 91, 122)
ACCENT_DARK = (210, 50, 84)
BLUE = (65, 145, 255)
YELLOW = (255, 211, 77)
GREEN = (64, 196, 132)
PURPLE = (142, 95, 255)
CANVAS_BG = (255, 255, 255)

CANVAS_RECT = pygame.Rect(80, 120, 960, 560)
TOOLBAR_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, 88)
GHOST_SECONDS = 3.0
LOBBY_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

PALETTE = [
    (22, 24, 29),
    (255, 255, 255),
    (230, 57, 70),
    (244, 162, 97),
    (233, 196, 106),
    (42, 157, 143),
    (38, 70, 83),
    (69, 123, 157),
    (131, 56, 236),
    (255, 91, 122),
    (64, 196, 132),
    (255, 211, 77),
]

PROMPTS = [
    "Astronaut cat eating pizza",
    "Robot building a sandcastle",
    "Dragon learning to skateboard",
    "Penguin DJ at a birthday party",
    "Wizard opening a tiny bakery",
    "Dinosaur riding a rainbow bus",
    "Superhero brushing a giant tooth",
    "Moon picnic with flying snacks",
    "Pirate searching for lost socks",
    "Alien trying ice cream for the first time",
]


class Screen(Enum):
    MENU = "menu"
    DRAWING = "drawing"
    GALLERY = "gallery"


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    value: object = None

    def draw(self, surface, font, selected=False, enabled=True):
        fill = ACCENT if selected else PANEL
        border = ACCENT_DARK if selected else BORDER
        text_color = (255, 255, 255) if selected else INK
        if not enabled:
            fill = (231, 234, 239)
            text_color = (147, 154, 166)
        pygame.draw.rect(surface, fill, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=8)
        text = font.render(self.label, True, text_color)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


class ColorCompleteGame:
    def __init__(self):
        pygame.init()
        self.tick_sound = self.make_tick_sound()
        pygame.display.set_caption("Color Complete")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("arial", 42, bold=True)
        self.large_font = pygame.font.SysFont("arial", 30, bold=True)
        self.font = pygame.font.SysFont("arial", 22)
        self.small_font = pygame.font.SysFont("arial", 17)

        self.screen_state = Screen.MENU
        self.player_count = 4
        self.round_seconds = 30
        self.total_rounds = 4
        self.current_turn = 0
        self.current_round = 1
        self.turn_started_at = 0
        self.turn_started_wall = None
        self.last_tick_second = None

        self.paintings = []
        self.assignments = []
        self.contributions = []
        self.turn_undo_stack = []
        self.turn_start_snapshot = None
        self.brush_color = PALETTE[0]
        self.brush_size = 8
        self.is_drawing = False
        self.last_pos = None
        self.has_drawn_this_turn = False
        self.hint_held = False
        self.gallery_offset = 0.0
        self.gallery_target_offset = 0.0
        self.prompt = random.choice(PROMPTS)
        self.lobby_code = self.generate_lobby_code()
        self.join_code = ""
        self.host_name = "Player 1"
        self.active_input = None
        self.player_names = ["Player 1", "Player 2", "Player 3", "Player 4"]
        self.ws_url = os.environ.get("COLOR_COMPLETE_WS_URL", DEFAULT_WS_URL)
        self.client = None
        self.local_player_id = None
        self.network_status = f"WebSocket: {self.ws_url}"
        self.connecting = False
        self.current_stroke_id = None

        self.name_input_rect = pygame.Rect(250, 166, 220, 38)
        self.join_input_rect = pygame.Rect(490, 166, 130, 38)
        self.new_lobby_button = Button(pygame.Rect(638, 166, 98, 38), "Host")
        self.join_button = Button(pygame.Rect(748, 166, 98, 38), "Join")
        self.player_buttons = self.make_row_buttons(["1", "2", "3", "4"], 392)
        self.time_buttons = self.make_row_buttons(["15s", "30s", "45s", "60s"], 518, [15, 30, 45, 60])
        self.round_buttons = self.make_row_buttons(["1", "2", "3", "4"], 642)
        self.prompt_button = Button(pygame.Rect(392, 704, 160, 42), "New idea")
        self.start_button = Button(pygame.Rect(568, 700, 180, 48), "Start")
        self.undo_button_rect = pygame.Rect(535, 49, 42, 32)
        self.peek_button_rect = pygame.Rect(586, 49, 62, 32)

    def generate_lobby_code(self):
        return "".join(random.choice(LOBBY_CHARS) for _ in range(5))

    def settings_payload(self):
        return {
            "player_count": self.player_count,
            "round_seconds": self.round_seconds,
            "total_rounds": self.total_rounds,
        }

    def network_ready(self):
        return self.client is not None and self.client.connected

    def is_my_turn(self):
        return not self.network_ready() or self.local_player_id == self.current_turn

    def start_host_lobby(self):
        if self.connecting:
            return
        self.lobby_code = self.generate_lobby_code()
        self.connecting = True
        self.connect_to_server(create_room=True)
        self.network_status = f"Creating room {self.lobby_code}..."

    def join_lobby(self):
        code = self.join_code.strip().upper()
        if not code or self.connecting:
            return
        self.lobby_code = code
        self.connecting = True
        self.connect_to_server(create_room=False)
        self.network_status = f"Joining room {code}..."

    def connect_to_server(self, create_room=False):
        self.client = NetworkClient()
        self.client.connect(
            self.ws_url,
            self.lobby_code,
            self.host_name.strip() or "Player",
            create_room=create_room,
            settings=self.settings_payload(),
            prompt=self.prompt,
        )

    def make_tick_sound(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1)
            sample_rate = 22050
            duration = 0.055
            volume = 9000
            samples = array("h")
            for i in range(int(sample_rate * duration)):
                wave = math.sin(2 * math.pi * 1200 * i / sample_rate)
                fade = 1 - (i / (sample_rate * duration))
                samples.append(int(volume * wave * fade))
            return pygame.mixer.Sound(buffer=samples.tobytes())
        except pygame.error:
            return None

    def make_row_buttons(self, labels, y, values=None):
        values = values or [int(label) for label in labels]
        total_width = len(labels) * 72 + (len(labels) - 1) * 14
        x = (SCREEN_WIDTH - total_width) // 2
        return [
            Button(pygame.Rect(x + i * 86, y, 72, 46), label, values[i])
            for i, label in enumerate(labels)
        ]

    def new_canvas(self):
        surface = pygame.Surface(CANVAS_RECT.size).convert()
        surface.fill(CANVAS_BG)
        return surface

    def start_game(self):
        if self.network_ready():
            self.client.send({"type": "start_game"})
            return
        self.setup_game_state(self.player_names[: self.player_count], self.prompt, self.settings_payload())

    def setup_game_state(self, player_names, prompt, settings):
        self.player_count = int(settings.get("player_count", self.player_count))
        self.round_seconds = int(settings.get("round_seconds", self.round_seconds))
        self.total_rounds = int(settings.get("total_rounds", self.total_rounds))
        self.prompt = prompt
        self.player_names = list(player_names[: self.player_count])
        while len(self.player_names) < self.player_count:
            self.player_names.append(f"Player {len(self.player_names) + 1}")
        self.paintings = [self.new_canvas() for _ in range(self.player_count)]
        self.assignments = [0 for _ in range(self.player_count)]
        self.contributions = [[]]
        self.turn_undo_stack = []
        self.current_turn = 0
        self.current_round = 1
        self.turn_started_at = pygame.time.get_ticks()
        self.turn_started_wall = time.time()
        self.last_tick_second = None
        self.is_drawing = False
        self.last_pos = None
        self.has_drawn_this_turn = False
        self.hint_held = False
        self.turn_start_snapshot = self.paintings[self.active_canvas_index()].copy()
        self.gallery_offset = 0.0
        self.gallery_target_offset = 0.0
        self.screen_state = Screen.DRAWING

    def active_canvas_index(self):
        return 0

    def active_player_name(self):
        return self.player_names[self.current_turn]

    def active_original_name(self):
        return f"Drawing {self.active_canvas_index() + 1}"

    def time_left(self):
        if self.turn_started_wall is not None:
            elapsed = time.time() - self.turn_started_wall
        else:
            elapsed = (pygame.time.get_ticks() - self.turn_started_at) / 1000
        return max(0, math.ceil(self.round_seconds - elapsed))

    def turn_elapsed(self):
        if self.turn_started_wall is not None:
            return time.time() - self.turn_started_wall
        return (pygame.time.get_ticks() - self.turn_started_at) / 1000

    def ghost_is_active(self):
        return self.hint_held or (not self.has_drawn_this_turn and self.turn_elapsed() < GHOST_SECONDS)

    def finish_turn(self):
        if self.network_ready():
            self.client.send({"type": "end_turn"})
            return
        canvas_index = self.active_canvas_index()
        player_name = self.active_player_name()
        if player_name not in self.contributions[canvas_index]:
            self.contributions[canvas_index].append(player_name)
        self.is_drawing = False
        self.last_pos = None
        self.turn_undo_stack = []
        self.has_drawn_this_turn = False
        self.hint_held = False
        self.current_turn += 1
        if self.current_turn >= self.player_count:
            self.current_turn = 0
            self.current_round += 1
            if self.current_round > self.total_rounds:
                self.screen_state = Screen.GALLERY
                return
        self.turn_started_at = pygame.time.get_ticks()
        self.turn_started_wall = time.time()
        self.last_tick_second = None
        self.turn_start_snapshot = self.paintings[self.active_canvas_index()].copy()

    def draw_playful_background(self):
        self.screen.fill(BG)
        bands = [
            ((255, 223, 93), pygame.Rect(-120, 80, 360, 80), 18),
            ((95, 205, 255), pygame.Rect(880, 130, 330, 86), 18),
            ((255, 132, 168), pygame.Rect(820, 620, 360, 78), 18),
            ((105, 218, 151), pygame.Rect(-80, 620, 320, 78), 18),
        ]
        for color, rect, radius in bands:
            pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        for x, y, color in [
            (95, 210, PURPLE),
            (1010, 315, YELLOW),
            (140, 520, GREEN),
            (980, 535, BLUE),
        ]:
            pygame.draw.circle(self.screen, color, (x, y), 16)

    def draw_menu(self):
        self.draw_playful_background()
        title = self.title_font.render("Color Complete", True, INK)
        subtitle = self.font.render("Pass drawings, remix ideas, and make one wonderfully weird gallery.", True, MUTED)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 76)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 122)))

        lobby_panel = pygame.Rect(238, 144, 644, 78)
        pygame.draw.rect(self.screen, PANEL, lobby_panel, border_radius=8)
        pygame.draw.rect(self.screen, BLUE, lobby_panel, 3, border_radius=8)
        self.draw_input_box(self.name_input_rect, "Your name", self.host_name, self.active_input == "name")
        self.draw_input_box(self.join_input_rect, "Join code", self.join_code, self.active_input == "code")
        self.new_lobby_button.draw(self.screen, self.small_font)
        self.join_button.draw(self.screen, self.small_font, enabled=not self.connecting)
        code_surface = self.small_font.render(f"Lobby: {self.lobby_code}", True, INK)
        self.screen.blit(code_surface, (lobby_panel.x + 22, lobby_panel.y + 55))
        status_surface = self.fit_text(self.network_status, self.small_font, 310, MUTED)
        self.screen.blit(status_surface, (lobby_panel.x + 188, lobby_panel.y + 55))

        prompt_panel = pygame.Rect(250, 244, 620, 76)
        pygame.draw.rect(self.screen, PANEL, prompt_panel, border_radius=8)
        pygame.draw.rect(self.screen, YELLOW, prompt_panel, 4, border_radius=8)
        prompt_label = self.small_font.render("Today's prompt", True, MUTED)
        prompt_text = self.fit_text(self.prompt, self.large_font, prompt_panel.width - 44, INK)
        self.screen.blit(prompt_label, (prompt_panel.x + 22, prompt_panel.y + 12))
        self.screen.blit(prompt_text, prompt_text.get_rect(midleft=(prompt_panel.x + 22, prompt_panel.y + 50)))

        self.draw_menu_group("Players", self.player_buttons, self.player_count)
        self.draw_menu_group("Seconds per turn", self.time_buttons, self.round_seconds)
        self.draw_menu_group("Rounds", self.round_buttons, self.total_rounds)
        self.prompt_button.draw(self.screen, self.font)
        self.start_button.draw(self.screen, self.large_font)

    def draw_input_box(self, rect, label, value, active=False):
        border = ACCENT if active else BORDER
        pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=8)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=8)
        label_surface = self.small_font.render(label, True, MUTED)
        self.screen.blit(label_surface, (rect.x, rect.y - 18))
        text = value or ""
        if active and (pygame.time.get_ticks() // 450) % 2 == 0:
            text += "|"
        text_surface = self.fit_text(text, self.font, rect.width - 18, INK)
        self.screen.blit(text_surface, text_surface.get_rect(midleft=(rect.x + 10, rect.centery)))

    def draw_menu_group(self, label, buttons, selected_value):
        label_surface = self.large_font.render(label, True, INK)
        y = buttons[0].rect.y - 48
        self.screen.blit(label_surface, label_surface.get_rect(center=(SCREEN_WIDTH // 2, y)))
        for button in buttons:
            button.draw(self.screen, self.font, selected=button.value == selected_value)

    def fit_text(self, text, font, max_width, color):
        surface = font.render(text, True, color)
        if surface.get_width() <= max_width:
            return surface
        for size in range(font.get_height() - 2, 14, -1):
            candidate_font = pygame.font.SysFont("arial", size, bold=True)
            surface = candidate_font.render(text, True, color)
            if surface.get_width() <= max_width:
                return surface
        return surface

    def draw_toolbar(self):
        pygame.draw.rect(self.screen, PANEL, TOOLBAR_RECT)
        pygame.draw.rect(self.screen, (255, 240, 120), pygame.Rect(0, 0, SCREEN_WIDTH, 6))
        pygame.draw.line(self.screen, BORDER, (0, TOOLBAR_RECT.bottom), (SCREEN_WIDTH, TOOLBAR_RECT.bottom), 2)

        progress = f"Round {self.current_round}/{self.total_rounds}"
        turn = f"{self.active_player_name()}'s turn - finishing {self.active_original_name()}"
        if self.network_ready() and not self.is_my_turn():
            turn = f"Watching {self.active_player_name()} finish {self.active_original_name()}"
        prompt = f"Idea: {self.prompt}"
        seconds_left = self.time_left()
        timer = f"{seconds_left}s"
        self.screen.blit(self.large_font.render(progress, True, INK), (28, 18))
        self.screen.blit(self.small_font.render(turn, True, MUTED), (28, 48))
        prompt_rect = pygame.Rect(24, 64, 285, 22)
        pygame.draw.rect(self.screen, (255, 255, 255), prompt_rect, border_radius=8)
        pygame.draw.rect(self.screen, YELLOW, prompt_rect, 1, border_radius=8)
        prompt_surface = self.fit_text(prompt, self.small_font, prompt_rect.width - 18, (0, 0, 0))
        self.screen.blit(prompt_surface, prompt_surface.get_rect(midleft=(prompt_rect.x + 9, prompt_rect.centery)))
        danger_flash = seconds_left <= 5 and (pygame.time.get_ticks() // 220) % 2 == 0
        timer_color = (229, 32, 55) if seconds_left <= 5 else BLUE
        if danger_flash:
            pygame.draw.circle(self.screen, (255, 220, 225), (SCREEN_WIDTH - 64, 32), 37)
        timer_surface = self.large_font.render(timer, True, timer_color)
        self.screen.blit(timer_surface, timer_surface.get_rect(midright=(SCREEN_WIDTH - 28, 30)))
        self.screen.blit(self.small_font.render("N: next", True, MUTED), (SCREEN_WIDTH - 105, 54))

        x = 330
        for color in PALETTE:
            rect = pygame.Rect(x, 17, 28, 28)
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            pygame.draw.rect(self.screen, INK if color == self.brush_color else BORDER, rect, 3, border_radius=6)
            x += 34

        x = 330
        for size in [4, 8, 14, 22]:
            rect = pygame.Rect(x, 50, 40, 30)
            pygame.draw.rect(self.screen, PANEL, rect, border_radius=8)
            pygame.draw.rect(self.screen, ACCENT if size == self.brush_size else BORDER, rect, 2, border_radius=8)
            pygame.draw.circle(self.screen, INK, rect.center, max(2, size // 2))
            x += 47

        self.draw_icon_button(self.undo_button_rect, "undo", enabled=bool(self.turn_undo_stack))
        self.draw_text_button(self.peek_button_rect, "Hint", selected=self.ghost_is_active())

    def draw_icon_button(self, rect, icon, enabled=True):
        fill = PANEL if enabled else (232, 235, 241)
        line = INK if enabled else (155, 160, 170)
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT if enabled else BORDER, rect, 2, border_radius=8)
        if icon == "undo":
            pygame.draw.arc(self.screen, line, rect.inflate(-14, -12), math.radians(40), math.radians(310), 3)
            pygame.draw.polygon(
                self.screen,
                line,
                [(rect.x + 16, rect.y + 18), (rect.x + 12, rect.y + 29), (rect.x + 25, rect.y + 27)],
            )

    def draw_text_button(self, rect, label, selected=False):
        fill = (255, 236, 118) if selected else PANEL
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, YELLOW if selected else BORDER, rect, 2, border_radius=8)
        text = self.small_font.render(label, True, INK)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_canvas_screen(self):
        self.draw_playful_background()
        self.draw_toolbar()
        seconds_left = self.time_left()
        panic = seconds_left <= 5 and (pygame.time.get_ticks() // 180) % 2 == 0
        frame_color = (235, 39, 60) if panic else (255, 180, 78)
        pygame.draw.rect(self.screen, frame_color, CANVAS_RECT.inflate(16, 16), border_radius=14)
        canvas = self.paintings[self.active_canvas_index()]
        if self.ghost_is_active():
            preview = pygame.Surface(CANVAS_RECT.size).convert_alpha()
            preview.fill(CANVAS_BG)
            if self.turn_start_snapshot:
                ghost = self.turn_start_snapshot.copy().convert_alpha()
                ghost.set_alpha(48)
                preview.blit(ghost, (0, 0))
            self.screen.blit(preview, CANVAS_RECT)
        else:
            self.screen.blit(canvas, CANVAS_RECT)
        pygame.draw.rect(self.screen, INK, CANVAS_RECT, 2)

    def canvas_pos(self, pos):
        return pos[0] - CANVAS_RECT.x, pos[1] - CANVAS_RECT.y

    def paint_at(self, pos):
        if not CANVAS_RECT.collidepoint(pos):
            self.last_pos = None
            return
        if not self.is_my_turn():
            return
        self.has_drawn_this_turn = True
        local = self.canvas_pos(pos)
        canvas = self.paintings[self.active_canvas_index()]
        previous = self.last_pos
        if self.last_pos is None:
            pygame.draw.circle(canvas, self.brush_color, local, self.brush_size // 2)
        else:
            pygame.draw.line(canvas, self.brush_color, self.last_pos, local, self.brush_size)
            pygame.draw.circle(canvas, self.brush_color, self.last_pos, self.brush_size // 2)
            pygame.draw.circle(canvas, self.brush_color, local, self.brush_size // 2)
        self.last_pos = local
        if self.network_ready():
            self.client.send({
                "type": "stroke",
                "stroke_id": self.current_stroke_id,
                "previous": previous,
                "point": local,
                "color": list(self.brush_color),
                "size": self.brush_size,
            })

    def apply_stroke(self, canvas_index, previous, point, color, size):
        if canvas_index >= len(self.paintings):
            return
        canvas = self.paintings[canvas_index]
        color = tuple(color)
        point = tuple(point)
        if previous is None:
            pygame.draw.circle(canvas, color, point, size // 2)
        else:
            previous = tuple(previous)
            pygame.draw.line(canvas, color, previous, point, size)
            pygame.draw.circle(canvas, color, previous, size // 2)
            pygame.draw.circle(canvas, color, point, size // 2)

    def handle_palette_click(self, pos):
        if self.undo_button_rect.collidepoint(pos):
            self.undo_last_stroke()
            return True
        if self.peek_button_rect.collidepoint(pos):
            self.hint_held = True
            return True

        x = 330
        for color in PALETTE:
            if pygame.Rect(x, 17, 28, 28).collidepoint(pos):
                self.brush_color = color
                return True
            x += 34

        x = 330
        for size in [4, 8, 14, 22]:
            if pygame.Rect(x, 50, 40, 30).collidepoint(pos):
                self.brush_size = size
                return True
            x += 47
        return False

    def save_undo_snapshot(self):
        self.turn_undo_stack.append(self.paintings[self.active_canvas_index()].copy())
        if len(self.turn_undo_stack) > 12:
            self.turn_undo_stack.pop(0)

    def undo_last_stroke(self):
        if not self.turn_undo_stack:
            return
        self.paintings[self.active_canvas_index()] = self.turn_undo_stack.pop()
        self.is_drawing = False
        self.last_pos = None
        if self.network_ready() and self.is_my_turn():
            self.client.send({
                "type": "undo",
                "canvas": self.encode_canvas(self.paintings[self.active_canvas_index()]),
            })

    def encode_canvas(self, surface):
        raw = pygame.image.tostring(surface, "RGB")
        return base64.b64encode(zlib.compress(raw, 3)).decode("ascii")

    def decode_canvas(self, payload):
        raw = zlib.decompress(base64.b64decode(payload.encode("ascii")))
        return pygame.image.fromstring(raw, CANVAS_RECT.size, "RGB").convert()

    def draw_gallery(self):
        self.draw_playful_background()
        title = self.title_font.render("Final Gallery", True, INK)
        hint = self.font.render(f"Prompt: {self.prompt}   |   Lobby {self.lobby_code}   |   Use left and right arrows.", True, MUTED)
        self.screen.blit(title, (42, 26))
        self.screen.blit(hint, (46, 76))

        gap = 70
        card_w = 720
        card_h = 500
        start_x = 90 - self.gallery_offset
        y = 150
        self.gallery_offset += (self.gallery_target_offset - self.gallery_offset) * 0.18

        for i, canvas in enumerate(self.paintings):
            x = start_x + i * (card_w + gap)
            card = pygame.Rect(round(x), y, card_w, card_h)
            if card.right < -50 or card.left > SCREEN_WIDTH + 50:
                continue
            pygame.draw.rect(self.screen, PANEL, card, border_radius=8)
            pygame.draw.rect(self.screen, BORDER, card, 2, border_radius=8)
            label = self.large_font.render(f"Drawing {i + 1}", True, INK)
            self.screen.blit(label, (card.x + 24, card.y + 18))
            artists = "Created by: " + " -> ".join(self.contributions[i] or ["No strokes"])
            artists_surface = self.fit_text(artists, self.small_font, card_w - 48, MUTED)
            self.screen.blit(artists_surface, (card.x + 24, card.y + 52))
            preview_rect = pygame.Rect(card.x + 24, card.y + 82, card_w - 48, card_h - 108)
            scaled = pygame.transform.smoothscale(canvas, preview_rect.size)
            self.screen.blit(scaled, preview_rect)
            pygame.draw.rect(self.screen, BORDER, preview_rect, 1)

    def move_gallery(self, direction):
        gap = 70
        card_w = 720
        max_offset = max(0, (self.player_count - 1) * (card_w + gap))
        self.gallery_target_offset = min(max(self.gallery_target_offset + direction * (card_w + gap), 0), max_offset)

    def handle_menu_click(self, pos):
        self.active_input = None
        if self.name_input_rect.collidepoint(pos):
            self.active_input = "name"
            return
        if self.join_input_rect.collidepoint(pos):
            self.active_input = "code"
            return
        for button in self.player_buttons:
            if button.hit(pos):
                self.player_count = button.value
                if self.network_ready():
                    self.client.send({"type": "settings", "settings": self.settings_payload()})
        for button in self.time_buttons:
            if button.hit(pos):
                self.round_seconds = button.value
                if self.network_ready():
                    self.client.send({"type": "settings", "settings": self.settings_payload()})
        for button in self.round_buttons:
            if button.hit(pos):
                self.total_rounds = button.value
                if self.network_ready():
                    self.client.send({"type": "settings", "settings": self.settings_payload()})
        if self.new_lobby_button.hit(pos):
            self.start_host_lobby()
        if self.join_button.hit(pos):
            self.join_lobby()
        if self.prompt_button.hit(pos):
            self.prompt = random.choice([item for item in PROMPTS if item != self.prompt])
            if self.network_ready():
                self.client.send({"type": "prompt", "prompt": self.prompt})
        if self.start_button.hit(pos):
            if self.join_code.strip():
                self.lobby_code = self.join_code.strip().upper()[:5]
            self.start_game()

    def handle_text_input(self, event):
        if self.active_input is None:
            return
        if event.key == pygame.K_BACKSPACE:
            if self.active_input == "name":
                self.host_name = self.host_name[:-1]
            else:
                self.join_code = self.join_code[:-1]
            return
        if event.key == pygame.K_RETURN:
            self.active_input = None
            return
        if len(event.unicode) != 1:
            return
        if self.active_input == "name":
            if len(self.host_name) < 16 and event.unicode.isprintable():
                self.host_name += event.unicode
        elif self.active_input == "code":
            char = event.unicode.upper()
            if len(self.join_code) < 5 and char in LOBBY_CHARS:
                self.join_code += char

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.screen_state == Screen.MENU and self.active_input:
                    self.handle_text_input(event)
                    continue
                if self.screen_state == Screen.DRAWING and event.key == pygame.K_n:
                    self.finish_turn()
                if self.screen_state == Screen.DRAWING and (event.key == pygame.K_z or event.key == pygame.K_BACKSPACE):
                    self.undo_last_stroke()
                if self.screen_state == Screen.GALLERY:
                    if event.key == pygame.K_RIGHT:
                        self.move_gallery(1)
                    elif event.key == pygame.K_LEFT:
                        self.move_gallery(-1)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.screen_state == Screen.MENU:
                    self.handle_menu_click(event.pos)
                elif self.screen_state == Screen.DRAWING:
                    if not self.handle_palette_click(event.pos):
                        self.is_drawing = CANVAS_RECT.collidepoint(event.pos) and self.is_my_turn()
                        self.last_pos = None
                        if self.is_drawing:
                            self.current_stroke_id = f"{self.local_player_id or 0}-{time.time_ns()}"
                            self.save_undo_snapshot()
                            self.paint_at(event.pos)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.is_drawing = False
                self.last_pos = None
                self.hint_held = False
            if event.type == pygame.MOUSEMOTION and self.screen_state == Screen.DRAWING and self.is_drawing:
                self.paint_at(event.pos)

    def update(self):
        self.process_network()
        if self.screen_state == Screen.DRAWING:
            seconds_left = self.time_left()
            if seconds_left <= 5 and seconds_left != self.last_tick_second:
                self.last_tick_second = seconds_left
                if self.tick_sound:
                    self.tick_sound.play()
            if seconds_left <= 0 and not self.network_ready():
                self.finish_turn()

    def process_network(self):
        if not self.client:
            return
        while not self.client.inbox.empty():
            self.apply_network_message(self.client.inbox.get())

    def apply_network_message(self, message):
        message_type = message.get("type")
        if message_type == "welcome":
            self.connecting = False
            self.local_player_id = message.get("player_id")
            self.lobby_code = message.get("lobby_code", self.lobby_code)
            settings = message.get("settings", {})
            self.player_count = int(settings.get("player_count", self.player_count))
            self.round_seconds = int(settings.get("round_seconds", self.round_seconds))
            self.total_rounds = int(settings.get("total_rounds", self.total_rounds))
            self.prompt = message.get("prompt", self.prompt)
            self.network_status = f"Connected as Player {self.local_player_id + 1}"
        elif message_type == "lobby":
            settings = message.get("settings", {})
            self.player_count = int(settings.get("player_count", self.player_count))
            self.round_seconds = int(settings.get("round_seconds", self.round_seconds))
            self.total_rounds = int(settings.get("total_rounds", self.total_rounds))
            self.prompt = message.get("prompt", self.prompt)
            self.player_names = message.get("players", self.player_names)
            self.lobby_code = message.get("lobby_code", self.lobby_code)
            connected = message.get("connected_count", 0)
            self.network_status = f"{connected}/{self.player_count} connected"
        elif message_type == "start_game":
            self.setup_game_state(
                message.get("player_names", self.player_names),
                message.get("prompt", self.prompt),
                message.get("settings", self.settings_payload()),
            )
        elif message_type == "turn":
            self.current_turn = int(message.get("current_turn", self.current_turn))
            self.current_round = int(message.get("current_round", self.current_round))
            self.assignments = list(message.get("assignments", self.assignments))
            self.contributions = message.get("contributions", self.contributions)
            self.turn_started_wall = float(message.get("turn_started_at", time.time()))
            self.turn_started_at = pygame.time.get_ticks()
            self.last_tick_second = None
            self.is_drawing = False
            self.last_pos = None
            self.current_stroke_id = None
            self.has_drawn_this_turn = False
            self.hint_held = False
            if self.paintings:
                self.turn_start_snapshot = self.paintings[self.active_canvas_index()].copy()
        elif message_type == "stroke":
            if message.get("sender_id") == self.local_player_id:
                return
            self.apply_stroke(
                int(message.get("canvas_index", 0)),
                message.get("previous"),
                message.get("point"),
                message.get("color", PALETTE[0]),
                int(message.get("size", self.brush_size)),
            )
        elif message_type == "undo":
            if message.get("sender_id") == self.local_player_id:
                return
            canvas_index = int(message.get("canvas_index", 0))
            if canvas_index < len(self.paintings) and message.get("canvas"):
                self.paintings[canvas_index] = self.decode_canvas(message["canvas"])
        elif message_type == "gallery":
            self.contributions = message.get("contributions", self.contributions)
            self.screen_state = Screen.GALLERY
            self.is_drawing = False
        elif message_type == "disconnect":
            self.connecting = False
            self.network_status = "Disconnected"
        elif message_type == "error":
            self.connecting = False
            self.network_status = message.get("message", "Network error")

    def draw(self):
        if self.screen_state == Screen.MENU:
            self.draw_menu()
        elif self.screen_state == Screen.DRAWING:
            self.draw_canvas_screen()
        elif self.screen_state == Screen.GALLERY:
            self.draw_gallery()
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    ColorCompleteGame().run()
