# Docs

| File | class(es) / purpose |
| --- | --- |
| `game.py` | `Game` - class which stores information about the track, car, game state, etc |
| `racecar_env.py` | `RacecarEnv` - environment class for the reinforcement learning agent; basically a thin wrapper around `Game` |
| `renderer.py` | `Renderer` - initializes a pygame GUI for rendering agent's training/testing process. Also allows human to play the game. This should be instantiated alongside a `Game` object if the game needs to rendered |
| `callback.py` | `RenderCallback` - executes custom code at points in training process; helps monitor and modify training behaviour. | 
| `play.py` | script for human to play the game. Set `center_car` to |
| `test.py` | tests an RL model |
| `train.py` | train an RL model using PPO (Proximal Policy Optimization) with a default MLP (fully connected) neural network policy |
| `editor.py`| GUI track editor that edits config file |

### Config

By default, config is located at `./config.json` and includes relative raycast angles and track information.