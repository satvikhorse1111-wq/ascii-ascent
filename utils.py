from clear import clear
from time import sleep
from random import random, choices, shuffle, sample
from textwrap import shorten
from typing import Iterator, TypeVar
from dataclasses import dataclass, field
from enum import Enum, auto

from math import floor, sin, cos, radians
from statistics import quantiles
from sys import stdout, stderr
from itertools import batched, chain
from textwrap import wrap

from maps import LevelData, IndexedDatabase

"""[utils.py] Contains some random functions that are used
in the main game loop (game.py)"""

type Progress = TypeVar("Progress")

class IOUtils:

    class Response(Enum):

        YES = 1
        NO = auto()
        UNKNOWN = auto()

    """Tools that make input / output easier from the player
    to the user."""

    __slots__ = ()

    @staticmethod
    def sanitized(string: str):
        return string.strip().lower()

    @staticmethod
    def input(prompt: str="", sanitize: bool=False):

        stdout.write(prompt)

        x = input()
        return IOUtils.sanitized(x) if sanitize else x

    @staticmethod
    def validate(user_input: str) -> bool:

        if user_input:
            char = IOUtils.sanitized(user_input)[0]
            if char == "y":
                return IOUtils.Response.YES
            elif char == "n":
                return IOUtils.Response.NO

        return IOUtils.Response.UNKNOWN

    @staticmethod
    def get_validation(prompt: str, /) -> bool:

        user_input = IOUtils.input(prompt)
        return IOUtils.validate(user_input)

class StringUtils:

    __slots__ = ()

    @staticmethod
    def format_columns(list_str: list[str], cols=3, width=63,
                       even=True) -> None:

        """Prints lists of strings in columns.
        Provides a way to format strings."""

        batches = batched(list_str, cols)
        output = []

        col_width = width // cols
        for i in batches:

            if even:
                joinlist = [f"{x:<{col_width}}" for x in i]
                output.append("".join(joinlist).ljust(width))
            else:
                joinlist = [x for x in i]
                output.append("".join(joinlist).ljust(width))

        return "\n".join(output)

    @staticmethod
    def fast_distribute(list_str: list[str], /, *, width=63):

        if not list_str:
            return " " * width

        n = len(list_str[0])

        if any(len(s) - n for s in list_str):
            raise ValueError(
                "Can only take in list of strings with all equal lengths"
            )

        num_elements = width // (n + 1)
        result = " ".join(list_str[:num_elements]).ljust(width)

        if len(result) > width:
            result = result[:width - 3] + "..."

        return result

    @staticmethod
    def distribute(list_str: list[str], /, *, width=63):

        if not list_str:
            return " " * width

        n = len(list_str)

        # Width without separating spaces is divided
        p_width = (width - (n - 1)) // n

        aux = [len(string) - p_width for string in list_str]

        debt, widths = 0, list()

        # Will only compensate starting at the second element
        # since there is no debt to compensate for yet

        for ind in range(n):

            a = aux[ind]
            if a > 0:
                debt += a
                widths.append(p_width + a)
            elif a == 0:
                widths.append(p_width)
            elif a < 0:
                b = min(abs(a), debt)
                debt -= b
                widths.append(p_width - b)

        result = " ".join(
            string.ljust(w) for string, w in zip(list_str, widths)
        )

        if len(result) > width:
            return result[:width - 3] + "..."

        return result.ljust(width)

    @staticmethod
    def list_box(list_str: list[str], subs: dict[int, str]=None):

        if subs is None:
            subs = {}

        new_list = []

        max_width = max(len(string) for string in list_str)
        side = "~"*(max_width + 4)

        new_list.append(side)
        new_list.extend([f"| {string:<{max_width}} |" for string in list_str])
        new_list.append(side)

        for index, sub in subs.items():

            new_list[index+1] += f" {sub}"

        return "\n".join(new_list)

    @staticmethod
    def text_box(string: str, width: int=63):

        y_len = len(string.splitlines())

        lines = wrap(
            string, width=width-2)

        lines = [f"| {line:<{width-2}} |" for line in lines]

        display = ["~"*(width+2)]
        display.extend(lines)

        remainder = y_len - len(display)
        display.extend([f"| {' '*(width-2)} |" for i in range(remainder)])

        display.append("~" * (width+2))

        return "\n".join(display) + "\n"

    @staticmethod
    def bullet_box(list_str: list[str], width=63, newline=True):

        new_list = [
            wrap(string.replace("\n", ""),
                 width=(width - 2),
                 initial_indent="- ",
                 subsequent_indent="  "
                 ) for string in list_str
        ]

        result = ["~" * (width + 2)]

        result.extend([
            f"| {line:<{width - 2}} |" for line in chain.from_iterable(
                new_list)
        ]
        )

        result.append("~" * (width + 2))

        return "\n".join(result) + ("\n" if newline else "")

    @staticmethod
    def divider(width: int=63):

        length, extra = divmod(width, 2)
        divider = "=~"*length + "="*extra

        return divider

    @staticmethod
    def bar(list_str: list[str], width: int=63):

        divider = StringUtils.divider(width)

        new_list = []

        new_list.append(divider)
        new_list.append("\n".join(list_str))
        new_list.append(divider)

        return "\n".join(new_list)

    @staticmethod
    def _enumerated(str_list):

        new_list = str_list.copy()
        for i, string in enumerate(new_list, 1):

            if string == "Exit":
                n = "[x]"
            elif string == "Info":
                n = "[i]"
            else:
                n = f"[{i}]"

            new_list[i-1] = f"{n} {new_list[i-1]}"

        return new_list.copy()

    @staticmethod
    def menu(header, str_list, subs: dict[int, str]=None):

        str_list = StringUtils._enumerated(str_list)

        menu_list = [
            header,
            StringUtils.list_box(str_list, subs),
            "Select an option: "
        ]

        return "\n".join(menu_list)

@dataclass(frozen=True, slots=True)
class InfoData:

    header: str = "Info:"
    bullets: list = field(default_factory=list)
    free_text: str = ""

class InfoUtils:

    __slots__ = ()

    """This class basically just collects a bunch
    of messages for 'help' or 'info' across different
    menus. This allows for easy access."""

    GENERAL = InfoData(
        header="About the Game:",
        bullets=[
            """'ASCII Ascent' is a text-based platformer that uses entirely ASCII 
    characters. I am fairly sure this game is the first of its kind.""",
            """This game took an eternity to build, so please like and comment 
    if you can.""",
            """Please give feedback on this game if you have any 
    so I can improve it. """,
            """If you liked this game, subscribe to my subpage to support me! 
    Thanks :)""",
        ],
        free_text="https://www.khanacademy.org/python-program/the-capybaras-subpage/6648125978689536"
    )

    GAME = InfoData(
        header="Help for 'Play' Mode:",
        bullets=[
            """This is the menu for climbing up the castle and 
    playing the main levels.""",
            """[1] Continue Game: Plays the next level.""",
            """[2] Select Level: Select among the levels you have unlocked.""",
            """Tip: You need to collect 10 coins to unlock the Tower. If you 
    cannot access the Tower, collect 10 coins and come back."""
        ]
    )

    CUSTOM = InfoData(
        header="Help for 'Custom' Mode:",
        bullets=[
            """The Custom Mode lets you view user levels as well as 
create your own!""",
            """[1] Create New Level: Sends you to the editor, where you can 
create levels. Go to 'Editor Tutorial' to learn more.""",
            """[2] Created Levels: Lets you search through your created 
levels. Once you have selected a level, you can edit that level, play it, 
delete it, or get the save string for the level.""",
            """[3] Load Save String: This feature allows you to save levels 
and share them with others. If you have a save string for a level, copy paste 
it to add it to your created levels!""",
            """[4] Public Levels: Play levels that others have created.""",
            """[5] Editor Tutorial: Teaches you how to use the editor.""",
        ]
    )

    ACCOUNT = InfoData(
        header="Help for 'View Account' Mode:",
        bullets=[
            "[1] View Stats: View your total attempts and jumps.",
            "[2] View Progress: See completion status for the main levels.",
            """[3] View Achievements: View achievements that are earned from 
    playing the game. There are 16 achievements you can earn. Each achievement 
    gives you 5 points, although some achievements are much harder than others.""",
            "[4]/[5]: Change Icon/Username: Username must be under 25 characters.",
            "[6] About Game: Learn more about the Platformer."
        ]
    )

    ENDLESS = InfoData(
        header="Help for 'Endless':",
        bullets=[
            """Endless Mode allows you to platform uninterrupted, 
    beating harder and harder randomly generated levels while gaining points!""",
            """[1] Play: You can choose to play two different modes: Spike Trials 
    and Mountain of Asterisks."""
            """Spike Trials generates terrain with spikes, whereas Mountain of 
    Asterisks throws asterisk blocks into the mix as well.""",
            """[2] View Endless Mode Progress: See how far you have gotten 
    in Endless Mode for both modes."""
        ]
    )

    PACKS = InfoData(
        header="Help for 'Experimental Level Packs':",
        bullets=[
            """30 new levels for you to beat, including 6 new features!""",
            """[1] Hidden Blocks: Makes the character invisible, 
so you really have to pay attention.""",
            """[2] Countdown Blocks: A block that momentarily disappears 
on a cycle.""",
            """[3] Gravity Blocks: Switches the player's gravity 
upside down or right side up.""",
            """[4] Teleporters: Teleports the icon from one location 
to another.""",
            """[5] Launchers: Launches the icon through the air: 
the player can choose the target.""",
            """[6] More Locks: New locks that are more complex than 
the existing locks 'l' and 'L'."""
        ]
    )

    HOTKEYS = InfoData(
        header="Help for 'Edit Hotkeys':",
        bullets=[
            """Hotkeys help you quickly place a character without 
having to use your toolbar.""",
            """To create a hotkey, move down to the [+ New] bar 
and press [ENTER]. There, you can specify a hotkey, and the character 
it places.""",
            """You can edit the character a hotkey places. Just 
move to the hotkey you want to edit and press [ENTER] to get to 
the Edit / Delete menu.""",
            """In this same menu, you can also delete hotkeys.""",
            """You can always view your current hotkeys while 
editing by pressing [h].""",
            """(Some hotkeys cannot be used as they already have 
a use in the editor, such as w, a, s, d. Some characters are not 
supported for hotkeys yet.)"""
        ]
    )

    @classmethod
    def display_info(cls, name: str="GENERAL"):

        clear()

        info_data = getattr(InfoUtils, name.strip().upper())

        string_list = [
            info_data.header,
            StringUtils.bullet_box(info_data.bullets, width=63, newline=False),
            info_data.free_text
        ]

        stdout.write("\n".join(string_list) + "\n")

        StringUtils.fixed_input("Press [ENTER] to continue. ")

class EnterExitUtils:

    __slots__ = ()

    LOGO = """                                 
                   &x&Xx&&   
                   :.&&...x. 
                 x.$;.....&&x
        ;&&&&&&$x:.;:.    .& 
      &&$;+X;:.+;.. . x;.;&. 
    x&x.:;:.:..:++..  ..:;   
   .&.  ;..$X;:  ..+.;.:.    
   &X+x;::.....:.:+x:+ ;+    
   &;.   .;..:.+&&x.  ::.    
   &X+:...::;:+.$;..   .     
   &X:x$;;;+.. ;&&$$ &&X     
   .&X$x:..Xx$$.   && &x     
    &&&&&&&&&&&&.. &;  &&.   
    ...............&&&. .$...
         .......... .........
Brought to you by: Capybara Studios [(C) 2026]"""[1:]

    CAPYBARA = """                                 
                   &x&Xx&&   
                   :.&&...x. 
                 x.$;.....&&x
        ;&&&&&&$x:.;:.    .& 
      &&$;+X;:.+;.. . x;.;&. 
    x&x.:;:.:..:++..  ..:;   
   .&.  ;..$X;:  ..+.;.:.    
   &X+x;::.....:.:+x:+ ;+    
   &;.   .;..:.+&&x.  ::.    
   &X+:...::;:+.$;..   .     
   &X:x$;;;+.. ;&&$$ &&X     
   .&X$x:..Xx$$.   && &x     
    &&&&&&&&&&&&.. &;  &&.   
    ...............&&&. .$...
         .......... ........."""[1:]

    TITLE = r"""
  m   .m,   mm  mmm  mmm        m   .m,   mm .mmm,.m .,.mmm,
 ]W[ .P'T  W''[ 'W'  'W'       ]W[ .P'T  W''[]P''`]W ][''W'`
 ]W[ ]b   ]P     W    W        ]W[ ]b   ]P   ][   ]P[][  W  
 W W  TWb ][     W    W        W W  TWb ][   ]WWW ][W][  W  
 WWW    T[]b     W    W        WWW    T[]b   ][   ][]d[  W  
.W W,]mmd` Wmm[ mWm  mWm      .W W,]mmd` Wmm[]bmm,][ W[  W  
'` '` ''`   ''  '''  '''      '` '` ''`   '' ''''`'` '`  '
ASCII Ascent: A Platformer Game [Capybara Studios (C) 2026]"""[1:]

    @classmethod
    def starting_scene(cls):

        clear()
        sleep(1)

        for line in EnterExitUtils.LOGO.splitlines():
            stdout.write(line + "\n")
            sleep(0.05)

        sleep(3)
        clear()

        for line in EnterExitUtils.TITLE.splitlines():
            stdout.write(line + "\n")
            sleep(0.05)

        sleep(3)
        clear()

        sleep(2)

    @classmethod
    def exit_scene(cls, string: str):
        clear()
        stderr.write(
            "\n".join([EnterExitUtils.CAPYBARA, "Thanks for playing!", string]
                      ))

class LoadUtils:

    __slots__ = ()

    MSGS = [
        "Loading...",
        "Getting Characters...",
        "Placing Obstacles...",
        "Parsing Code...",
        "Flipping Bits...",
        "Getting Data...",
        "Doing Stuff...",
        "Running Algorithms...",
        "Creating the Fake Progress Bar... umm... wait nevermind",
        "If you see this, you are incredibly lucky"
    ]

    WEIGHTS = [1_000] * (len(MSGS) - 1) + [1]

    @staticmethod
    def progress_bar_iter(speed: float=1.0) -> Iterator:

        percent: float = 0.0
        bar_length: int = 65

        while True:

            bar = "%" * int(percent * bar_length)

            yield f"{bar:-<{bar_length}}"

            if percent >= 1.0:
                break

            percent = min(percent + (random() / speed), 1.0)

    @classmethod
    def get_loading_msg(cls):

        return choices(cls.MSGS, weights=cls.WEIGHTS)[0]

    @staticmethod
    def _format_time(time: int | float):

        if isinstance(time, (int, float)) and time != float("inf"):
            return f"Time Goal: [{time:.2f} seconds]"
        else:
            return ""

    @staticmethod
    def load(level: LevelData) -> None:

        if level == LevelData.NULL:
            return

        bars = LoadUtils.progress_bar_iter()

        while True: # Print progress bar
            try:
                clear()

                points_str = (f" [Points: {level.points}]"
                              if level.points > 0 else "")

                stdout.write(
                    LoadUtils._format_time(level.time) + points_str + "\n"
                )
                stdout.write(str(level.map))
                stdout.write(
                    LoadUtils.get_loading_msg() + "\n" + next(bars) + "\n"
                )

                sleep(random())

            except StopIteration:
                clear()
                break

    @staticmethod
    def load_scrolling(level: LevelData) -> None:

        if level == LevelData.NULL:
            return

        y_len = len(level.map)

        bars = LoadUtils.progress_bar_iter(12.0)

        bottom, top = 0, 12

        c = 1
        up = True

        while True:
            try:

                display = level.map[bottom:top]

                clear()

                stdout.write(LoadUtils._format_time(level.time) + "\n")
                stdout.write(str(display))
                stdout.flush()

                if up is False and bottom <= 0:
                    up = True
                elif up and top >= y_len:
                    up = False

                c = 1 if up else -1
                top += c
                bottom += c

                stdout.write(LoadUtils.get_loading_msg() + "\n")
                stdout.write(next(bars) + "\n")
                stdout.flush()

                sleep(random())

            except StopIteration:
                clear()
                break

class Achievements:

    __slots__ = ()

    ACHIEVEMENTS = dict(
        [
            # Progress / coin related achievements
            ("Getting Started", "Beat one level"),
            ("Above Average", "Beat a level with a coin"),
            ("ASCII Rookie", "Beat 5 levels"),
            ("ASCII Novice", "Beat 10 levels"),
            ("ASCII Master", "Beat the Tower"),
            ("ASCII King?", "Beat all levels"),
            ("The Richest", "Beat 10 levels with all coins"),
            ("Maxxed Out", "Beat all levels with coins and in time"),

            # Point related achievements
            ("Ten Squared", "Earn 100 points"),
            ("Two Times Better", "Earn 200 points"),
            ("How on Earth?", "Earn 500 points"),

            # Jump related achievements
            ("Jumping Maniac", "Jump 100 times"),

            # Attempt related achievements
            ("Never Give Up", "Get 20 attempts"),

            # Time related achievements
            ("Speedrunner", "Beat a level under the time limit"),
            ("Master Speedrunner", "Beat 10 levels under the time limit"),
            ("Need for Speed", "Beat a level in under 3 seconds"),
        ]
    )

class PaginateUtils:

    __slots__ = ()

    @staticmethod
    def paginate_maps(database: IndexedDatabase, *,
                      showcase=False, meta=True, ind=0
                      ) -> tuple[int, LevelData]:

        if not database:
            raise ValueError

        max_ind = len(database) - 1

        while True:
            clear()

            if showcase:
                stdout.write("Play user-created maps!\n")
            elif showcase is None:
                stdout.write("Results:\n")

            level = database[ind] # LevelData

            game_map, msg, time, title, _1, points, author, _2 = level

            # From textwrap.
            msg_str = shorten(msg, width=50, placeholder="...")

            if msg_str:
                msg_str = f"[{msg_str}]"

            title_str = f"[{title}]".upper()

            points_str = f"[Points: {points}]" if points > 0 else ""

            author_str = f"[Created by: {author}]" if meta else ""

            time_str = LoadUtils._format_time(time)

            # Always 3 lines long. Prevents shifting between maps
            stdout.write(
                f"""{title_str} {author_str}
{time_str} {points_str}
{msg_str}
""")
            stdout.write(str(game_map))

            stdout.write("Page:".center(65) + "\n")
            if ind == 0:
                arrow = "|1 >|" if len(database) != 1 else "|1|"
            elif ind == max_ind:
                arrow = f"|< {ind + 1}|"
            else:
                arrow = f"|< {ind + 1} >|"

            stdout.write(arrow.center(65) + "\n")

            a = IOUtils.input(
                "[a]/[d] to scroll, [x] to exit, [ENTER] to continue. "
            )

            if a == "d" and ind != max_ind:
                ind += 1
            elif a == "a" and ind != 0:
                ind -= 1
            elif a in {"exit", "x"}:
                return float("nan"), LevelData.NULL
            elif not a:
                break

        return ind, database[ind]

# Type aliases
num = int | float
vector = tuple[num, num]

class PerlinNoise:

    __slots__ = ("gradients",)

    """A class which contains the .noise() method, which returns
    a value based on x and y coordinates. It also contains .display(),
    which can be used to create a visualization with a certain length
    and height."""

    permutations = [i for i in range(256)]
    shuffle(permutations)

    def __init__(self):

        self.gradients = self._create_gradients()

    def _create_gradients(self):

        """Generates a list of 256 random unit vectors using basic
        trigonometry."""

        gradients = []
        degrees = sample(range(360), k=256)

        # Create a list of random unit vectors.
        gradients = [(cos(radians(x)), sin(radians(x))) for x in degrees]

        return gradients

    def _get_gradient(self, ix: int, iy: int):

        """Finds the gradient vector from self.gradients
        at a certain coordinate."""

        i = (ix % 256 + PerlinNoise.permutations[iy % 256]) % 256
        index = PerlinNoise.permutations[i]

        return self.gradients[index % 256]

    @staticmethod
    def _dot_product(v1: vector, v2: vector) -> num:

        """Helper function to return the dot product of two vectors in R^2."""

        return v1[0] * v2[0] + v1[1] * v2[1]

    @staticmethod
    def _easing(a: num) -> num:

        """Smoothstep function 3a^2 - 2a^3."""

        return 3 * pow(a, 2) - 2 * pow(a, 3)

    @staticmethod
    def linear(h1: num, h2: num, frac: num) -> float:

        """Linear interpolation formula using smoothstep, A.K.A lerp()."""

        return h1 + PerlinNoise._easing(frac) * (h2 - h1)

    @staticmethod
    def bilinear(n00: num, n10: num, n01: num, n11: num, xf: num, yf: num):

        """Bilinear interpolation formula using linear interpolation.
        The first four arguments in this case are the dot products."""

        v0 = PerlinNoise.linear(n00, n10, xf)
        v1 = PerlinNoise.linear(n01, n11, xf)

        v = PerlinNoise.linear(v0, v1, yf)

        return v

    def noise(self, x: num, y: num) -> float:

        """Generates the Perlin Noise value based on a coordinate
        x and y.

        Key for variable names:

        01    11


        00    10

        """

        ix, iy = floor(x), floor(y)

        # Decimal parts of x and y.

        xf: num
        yf: num

        xf, yf = x - ix, y - iy

        # Gradient vectors.

        g00: vector
        g10: vector
        g01: vector
        g11: vector

        g00 = self._get_gradient(ix, iy)
        g10 = self._get_gradient(ix + 1, iy)
        g01 = self._get_gradient(ix, iy + 1)
        g11 = self._get_gradient(ix + 1, iy + 1)

        # The dot products of the offset vectors and gradient vectors.

        n00: num
        n10: num
        n01: num
        n11: num

        n00 = PerlinNoise._dot_product((xf, yf), g00)
        n10 = PerlinNoise._dot_product((xf - 1, yf), g10)
        n01 = PerlinNoise._dot_product((xf, yf - 1), g01)
        n11 = PerlinNoise._dot_product((xf - 1, yf - 1), g11)

        return self.bilinear(n00, n10, n01, n11, xf, yf)
