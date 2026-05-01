# ASCII Ascent

A terminal-based ASCII platformer game.

```
  m   .m,   mm  mmm  mmm        m   .m,   mm .mmm,.m .,.mmm,
 ]W[ .P'T  W''[ 'W'  'W'       ]W[ .P'T  W''[]P''`]W ][''W'`
 ]W[ ]b   ]P     W    W        ]W[ ]b   ]P   ][   ]P[][  W
 W W  TWb ][     W    W        W W  TWb ][   ]WWW ][W][  W
 WWW    T[]b     W    W        WWW    T[]b   ][   ][]d[  W
.W W,]mmd` Wmm[ mWm  mWm      .W W,]mmd` Wmm[]bmm,][ W[  W
'` '` ''`   ''  '''  '''      '` '` ''`   '' ''''`'` '`  '
```

Capybara Studios © 2026

## Requirements

- Python 3.12+ (uses `itertools.batched`)
- A terminal that supports ANSI clear-screen

No third-party dependencies — standard library only.

## Run

```
python main.py
```

## Modes

- **Play** — work through the main level progression, ending in the Tower.
- **Creator** — build, save, and play your own levels in a custom editor with configurable hotkeys.
- **Endless** — auto-generated levels for score chasing (spike trials and the Mountain of Asterisks).
- **Level Packs** — additional level collections, unlocked after beating the Tower.
- **Tutorial** — interactive walkthrough of the platformer controls.
- **Account** — view progress, achievements, and stats.

## Save / Load

The game has no on-disk save file. From the main menu, **Save** prints a save string you can copy; paste it back at startup to restore progress.

## Project Layout

| File | Role |
| --- | --- |
| [main.py](main.py) | Entry point |
| [mainmode.py](mainmode.py) | Main menu, account viewer, level player |
| [plat.py](plat.py) | Core platformer engine (`Platformer`, `Tower`, `Endless`) |
| [editormode.py](editormode.py) | Level editor and hotkey system |
| [othermodes.py](othermodes.py) | Custom, Endless, and Pack modes |
| [maps.py](maps.py) | Built-in level data |
| [anim.py](anim.py) | Cutscenes and tutorial animations |
| [utils.py](utils.py) | Shared UI / IO / pagination / achievements helpers |
| [clear.py](clear.py) | Cross-platform screen clear |
