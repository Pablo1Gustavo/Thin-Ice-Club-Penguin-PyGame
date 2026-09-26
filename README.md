# Thin Ice — Club Penguin 🐧🧊

Recreation of **Thin Ice**, a Club Penguin minigame. It was made in 2018 for an Object-Oriented Programming course in an integrated technical program in Computer Science.

![Game preview](game_preview.jpg)

## 🚀 How to play

The project uses **Python 3.6.15** and **pygame 1.9.4**. `mise.toml` specifies the Python version, and `requirements.txt` lists the game's dependency.

From the project root, install the dependencies and run the game:

```bash
python -m pip install -r requirements.txt
python "Thin Ice.py"
```

If you use [mise](https://mise.jdx.dev/), first install the configured Python version with `mise install`. Then prefix each `python` command above with `mise exec --`.

### 🎮 Controls

```text
       [^]
   [<] [v] [>]

   [Esc] Quit
```

> Run the game from the project root: the code uses relative paths to load levels, images, the font, and music.

## 📁 Project structure

| Path | Contents |
| --- | --- |
| `Thin Ice.py` | Main game code and entry point. |
| `Levels/` | Text files containing the level maps. |
| `Textures/` | Images for the player, scenery, and scoreboard. |
| `Sounds/` | Game music. |
| `Fonts/` | Font used in the interface. |
| `game_preview.jpg` | Preview image shown in this README. |
| `requirements.txt` | Python dependency (`pygame==1.9.4`). |
| `mise.toml` | Python version (`3.6.15`) for mise users. |
