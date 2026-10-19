import asyncio
from pathlib import Path
import pygame

WIDTH, HEIGHT = 900, 600
BASE_DIR = Path(__file__).parent
ASSET_DIR = BASE_DIR / "assets"
TEXT_DIR = BASE_DIR / "text"

def story(filename):
    """Read writer-owned prose from a UTF-8 file packaged with the game."""
    return (TEXT_DIR / filename).read_text(encoding="utf-8").strip()

class Monster:
    def __init__(self, name, armor, description):
        self.name = name
        self.armor = armor
        self.description = description

class Treasure:
    def __init__(self, name, value, description):
        self.name = name
        self.value = value
        self.description = description

class Weapon:
    def __init__(self, name, damage, description):
        self.name = name
        self.damage = damage
        self.description = description

class Room:
    def __init__(self, name, description, enter_sound=None, music=None):
        self.name = name
        self.description = description
        self.enter_sound = enter_sound
        self.music = music
        self.neighbors = {}
        # Each room gets its own lists, initially empty.
        self.monsters = []
        self.treasures = []
        self.weapons = []

    def add_neighbor(self, direction, room):
        self.neighbors[direction] = room

    def get_neighbor(self, direction):
        return self.neighbors.get(direction)

    def list_exits(self):
        return ", ".join(self.neighbors.keys())

class TextAdventure:
    def __init__(self):
        self.current_music = None
        self.music_started = False
        self.music_muted = False
        self.default_music = "ambient.ogg"
        self.messages = []
        self.current_input = ""
        self.score = 0
        self.best_weapon_damage = 3
        self.game_over = False

        self.sounds = {
            "move": pygame.mixer.Sound(ASSET_DIR / "move.ogg"),
            "pickup": pygame.mixer.Sound(ASSET_DIR / "pickup.ogg"),
            "danger": pygame.mixer.Sound(ASSET_DIR / "danger.ogg"),
            "win": pygame.mixer.Sound(ASSET_DIR / "win.ogg"),
        }

        entrance = Room("entrance", story("entrance.txt"))
        hall = Room("hall", story("hall.txt"))
        armory = Room("armory", story("armory.txt"))
        lair = Room("lair", story("lair.txt"), "danger", music="lair_music.ogg")

        entrance.add_neighbor("north", hall)
        hall.add_neighbor("south", entrance)
        hall.add_neighbor("west", armory)
        hall.add_neighbor("east", lair)
        armory.add_neighbor("east", hall)
        lair.add_neighbor("west", hall)

        # append() adds one object; extend() adds several objects from a list.
        hall.monsters.extend([
            Monster("wolf", 2, story("wolf.txt")),
            Monster("goblin", 1, story("goblin.txt")),
        ])
        lair.monsters.append(Monster("dragon", 4, story("dragon.txt")))
        hall.treasures.extend([
            Treasure("diamond", 10, story("diamond.txt")),
            Treasure("coin", 5, story("coin.txt")),
        ])
        lair.treasures.append(Treasure("chalice", 85, story("chalice.txt")))
        armory.weapons.extend([
            Weapon("axe", 5, story("axe.txt")),
            Weapon("sword", 4, story("sword.txt")),
        ])
        # Calculate the goal from the actual treasures instead of assuming 100.
        self.winning_score = sum(
            treasure.value
            for room in [entrance, hall, armory, lair]
            for treasure in room.treasures
        )

        self.current_room = entrance
        self.say("Welcome to the dungeon!")
        self.say("Click here, then press Enter to start background audio.")
        self.say("Try: look, go north, take diamond, attack wolf; M toggles music.")
        self.announce_room()

    def say(self, message):
        self.messages.append(message)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def update_music(self):
        """Change tracks only when necessary, never once per frame."""
        filename = self.current_room.music or self.default_music
        if not self.music_started or filename == self.current_music:
            return
        pygame.mixer.music.load(str(ASSET_DIR / filename))
        pygame.mixer.music.set_volume(0.0 if self.music_muted else 0.25)
        pygame.mixer.music.play(-1)  # Repeat indefinitely; the game keeps running.
        self.current_music = filename

    def start_music(self):
        # Start from a player's key press, rather than during construction.
        self.music_started = True
        self.update_music()

    def toggle_music(self):
        self.music_muted = not self.music_muted
        pygame.mixer.music.set_volume(0.0 if self.music_muted else 0.25)

    def announce_room(self):
        self.say(f"You are in the {self.current_room.name}.")

    def look(self):
        self.say(f"You are in {self.current_room.description}.")
        for monster in self.current_room.monsters:
            self.say(f"There is {monster.description} here. (attack {monster.name})")
        for weapon in self.current_room.weapons:
            self.say(f"There is {weapon.description} here. (take {weapon.name})")
        for treasure in self.current_room.treasures:
            self.say(f"There is {treasure.description} here. (take {treasure.name})")
        self.say(f"Exits: {self.current_room.list_exits()}")

    def go(self, direction):
        destination = self.current_room.get_neighbor(direction)
        if destination is None:
            self.say("You can't go that way from here.")
            return
        self.current_room = destination
        self.update_music()
        self.play_sound("move")
        if self.current_room.enter_sound is not None:
            self.play_sound(self.current_room.enter_sound)
        self.announce_room()

    def attack(self, name):
        for monster in self.current_room.monsters:
            if monster.name == name:
                if self.best_weapon_damage > monster.armor:
                    self.say(f"You defeat the {monster.name}!")
                    self.current_room.monsters.remove(monster)
                else:
                    self.say("Your blow bounces off harmlessly.")
                    self.say(f"The {monster.name} eats your head!")
                    self.say("GAME OVER")
                    self.play_sound("danger")
                    pygame.mixer.music.stop()
                    self.game_over = True
                # Return immediately: do not continue iterating a changed list.
                return
        self.say(f"There is no {name} here.")

    def take(self, name):
        for treasure in self.current_room.treasures:
            if treasure.name == name:
                self.current_room.treasures.remove(treasure)
                self.score += treasure.value
                self.play_sound("pickup")
                self.say(f"You take the {treasure.name}.")
                self.say(f"Your score is now {self.score} out of {self.winning_score}.")
                if self.score == self.winning_score:
                    self.say("YOU WIN!")
                    self.play_sound("win")
                    pygame.mixer.music.stop()
                    self.game_over = True
                return
        for weapon in self.current_room.weapons:
            if weapon.name == name:
                self.current_room.weapons.remove(weapon)
                self.play_sound("pickup")
                self.say(f"You take the {weapon.name}.")
                if weapon.damage > self.best_weapon_damage:
                    self.best_weapon_damage = weapon.damage
                    self.say("You'll be a more effective fighter with this!")
                else:
                    self.say("You keep using your stronger weapon.")
                return
        self.say(f"There is no {name} here.")

    def handle_command(self, line):
        self.say(f"> {line}")
        words = line.lower().split()

        if not words:
            return

        command = words[0]

        if self.current_room.monsters and command not in ["attack", "look", "help"]:
            self.say("You can't do that with unfriendlies about.")
            return

        if command == "look":
            self.look()
        elif command == "go" and len(words) > 1:
            self.go(words[1])
        elif command == "attack" and len(words) > 1:
            self.attack(" ".join(words[1:]))
        elif command == "take" and len(words) > 1:
            self.take(" ".join(words[1:]))
        elif command == "help":
            self.say("Commands: look, go DIRECTION, take OBJECT, attack MONSTER")
        else:
            self.say("I don't understand that.")

def wrap_text(text, font, max_width):
    if not text:
        return [""]
    # Preserve paragraph breaks from the story files on screen.
    if "\n" in text:
        lines = []
        for paragraph in text.splitlines():
            lines.extend(wrap_text(paragraph, font, max_width))
        return lines
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = word if not current else current + " " + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_game(screen, font, small_font, game):
    screen.fill((24, 24, 28))
    screen.blit(font.render("Tiny Text Adventure", True, (235, 235, 240)), (30, 20))
    label = "Music: muted" if game.music_muted else "Music: on"
    screen.blit(small_font.render(label + " (M)", True, (180, 180, 190)), (650, 25))

    lines = []
    for message in game.messages:
        lines.extend(wrap_text(message, small_font, WIDTH - 60))
    lines = lines[-20:]

    y = 70
    for line in lines:
        screen.blit(small_font.render(line, True, (220, 220, 225)), (30, y))
        y += 23

    pygame.draw.line(screen, (100, 100, 110), (30, HEIGHT - 70), (WIDTH - 30, HEIGHT - 70), 2)
    screen.blit(small_font.render("> " + game.current_input, True, (255, 255, 255)), (30, HEIGHT - 50))

async def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tiny Text Adventure")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 22)

    game = TextAdventure()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif not game.music_started and event.key == pygame.K_RETURN:
                    game.start_music()
                    game.say("Background audio started. Type look to begin.")
                elif event.key == pygame.K_m and not game.current_input:
                    game.toggle_music()
                elif event.key == pygame.K_RETURN:
                    if not game.game_over:
                        command = game.current_input.strip()
                        game.current_input = ""
                        game.handle_command(command)
                elif event.key == pygame.K_BACKSPACE:
                    game.current_input = game.current_input[:-1]
                elif event.unicode and event.unicode.isprintable():
                    game.current_input += event.unicode

        draw_game(screen, font, small_font, game)
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
