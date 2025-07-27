# Docs

### Getting started

Clone:

```
git clone https://github.com/nli33/rl-agent-racecar.git
cd rl-agent-racecar
```

Create a virtual environment and install dependencies:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Scripts:** `check_env.py, editor.py, play.py, test.py, train.py`
**Other files:** `callback.py, config.py, game.py, racecar_env.py, renderer.py`

| File | class(es) / purpose |
| --- | --- |
| `game.py` | `Game` - class which stores information about the track, car, game state, etc |
| `racecar_env.py` | `RacecarEnv` - environment class for the reinforcement learning agent; basically a thin wrapper around `Game` |
| `renderer.py` | `Renderer` - initializes a pygame GUI for rendering agent's training/testing process. Also allows human to play the game. This should be instantiated alongside a `Game` object if the game needs to displayed onscreen |
| `callback.py` | `Callback` - executes custom code at points in training process; helps monitor and modify training behaviour. | 
| `play.py` | script for human to play the game |
| `test.py` | tests a RL model |
| `train.py` | trains a RL model, either pre-existing or new |
| `editor.py`| GUI track editor that edits config file |
| `check_env.py` | checks that the environment is compliant with Gymnasium. should run with no errors |

### Training a model

If an existing model is passed, it will continue training that model. Otherwise defaults to creating a new model (default name `model.zip`)

```
python3 train.py
python3 train.py fast_model.zip 
python3 train.py --timesteps 200000
python3 train.py --legend
python3 train.py --plot training_plot.png
```

### Testing a model

```
python3 test.py
python3 test.py fast_model.zip
```

### Playing a track

```
python3 play.py
python3 play.py --agent fast_model.zip
python3 play.py --center
```

Press R to reset.

### Config

By default, config is located at `./config.json` and specifies the race car's **relative raycast angles** (for NN input) in addition to track information. Raycast angles must be edited manually, you can't edit them in the editor

### Track editor

Use keybinds to switch between different modes of the editor, which allows you to place different things:

- T: place tiles
- G: change goal location
- B: change beginning of track / spawnpoint
- S: save
- D: delete
- W: place waypoints
  - to delete a waypoint, enter "delete" mode and click near its endpoints
  - to clear any lone endpoints, press ESC

### Changing reward function

Modify `RacecarEnv._compute_reward()` in `racecar_env.py`