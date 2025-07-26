# RL Agent Race Car
Playing a 2D Racecar Game with a Reinforcement Learning Agent

### About

This repo uses the `Stable-Baselines3` library along with `Gymnasium` to train an agent within a custom environment (`RacecarEnv`). The agent is trained using the Proximal Policy Optimization (PPO) algorithm, an on-policy method which effectively balances exploitation and exploration. 

For decision-making, the agent uses a multi-layer perceptron (MLP) neural network which takes the observation space (raycast distances and car speed) as input, and outputs binary decisions corresponding to the action space (acceleration, braking, and steering). 

The environment (`RacecarEnv`) wraps a `Game` instance and provides structured observations and rewards, while a callback periodically renders the agent's behavior using a Pygame-based GUI.

**Training**

In the early stages of training, the agent behaves erratically, often crashing and failing to reach the goal as it explores the environment and collects initial experiences. Its actions are largely random, and reward signals are sparse or highly variable. 

<p align="center">
  <img src="assets/training200k.png" alt="Training progress">
  <em>Early training process (0 - 200,000 timesteps).</em>
</p><br/>

Over time, as training progresses, the agent starts to complete the track consistently, and gradually improves its speed. In late-stage training the agent shows more stable behavior and slower incremental gains as it converges toward a more optimal policy.

<p align="center">
  <img src="assets/training1m_2.png" alt="Training progress">
  <em>Late-stage training (1,000,000 - 2,000,000 timesteps).</em>
</p><br/>

Overall throughout the training process, the agent converges closer and closer to a "theoretically perfect" policy. In late-stage training, the agent consistently completes episodes within a narrow range of step counts, showing that it has developed a reliable strategy.

There are still occasional failures, which displays the balance between exploitation (using the learned policy) and exploration (testing new actions) in training.

<p align="center">
  <img src="assets/training4m.png" alt="Training progress">
  <em>Overall training process (0 - 4,000,000 timesteps).</em>
</p><br/>

**The reward function**

The only direct feedback that the agent receives is through the reward function. A poorly designed reward function can cause unintended shortcuts and suboptimal actions.

The reward function I used was simple and worked decently well:
- If the car crashes, the agent receives a penalty of -100. 
- If the goal tile is reached, the agent is given a reward of 100. 
- Otherwise, during "normal" driving, the agent receives a reward of `4 * (car_speed / max_car_speed_allowed) ^ 2` every frame. 

Making the reward increase quadratically at higher speeds encourages the agent to more heavily prefer higher speeds. 

Using a higher magnitude penalty for crashing results in the agent driving more carefully, since there's a greater incentive for it to avoid crashing. 

Conversely, using a smaller penalty results in the agent driving more recklessly, since the agent will prioritize collecting speed rewards. 

So, tweaking the constants in the reward function during the training can help the agent prioritize different things.

**The neural network**

As mentioned before the NN's input is essentially the observation space. This consists of raycast distances at various angles relative to the car's heading (for most of this project I used -90˚, -45˚, -22.5˚, 0˚, 22.5˚, 45˚, and 90˚), and also the car's current speed. So for N raycasts there would be N+1 input nodes.

I also tried training another agent with more raycast angles: `[-90.0, -45.0, -33.75, -22.5, -11.25, 0.0, 11.25, 22.5, 33.75, 45.0, 90.0]`. With more raycasts, the agent has a finer perception of the surrounding environment. But since in my game the tracks were all strictly axis-aligned, this may not have been too helpful. 

Using more raycasts (i.e. more NN inputs) increases the time required for the agent’s policy to converge. For example, I couldn’t train an agent with 11 raycasts to match the speed of the original 7-raycast agent within a reasonable amount of training time (under 1 hour).

**A few things I was surprised by**

- The agent can get *really* fast on a track after training for a while. On one track (`configs/narrow.json`), the best score I could get was 371, while the agent got a run of 361 timesteps.
- Once being trained on one track, the agent is able to run well on an entirely new track (with similar track width) without re-training, showing that it doesn't memorize a specific track but is rather actually able to generalize. Of course any effective RL agent should be able to do this but it was impressive to see in action 

**Future improvements**

- The agent does poorly on long tracks (`configs/long_track.json`). 

This is because the agent's training always begins at the start of the track, and so with finite training time it has less opportunity to "discover" and learn about later parts of the track. A better way could be to have the agent begin training at random locations on the track. Having "waypoints" (which give a reward when crossed) could also improve training.

- The agent does poorly when the track requires a big turn immediately at the beginning. 

One example is when the correct path is behind the car when it spawns, so it has to make a U-turn (`configs/beginning_u_turn.json`). My guess is that the agent has a hard time "discovering" the turn via random exploration. At the very beginning of training the agent is just selecting random actions, so on average the agent will tend to favor moving forward. Waypoints might help with this problem, along with randomized training.

- The game itself is very simple. 

It has very rigid physics; the track's boundaries are always axis-aligned (rectangular); the car is a simple rectangle and the game simply ends when the car's center leaves the track. In a game like Trackmania there is much more complex physics which allows for the car being airborne, along with mechanics like drifting. With a more complex game, I'm guessing the agent's decision MLP will need to have more inputs (axes of rotation, angular velocity/accel, distance to waypoints, etc) and will need to be trained for longer.

**Training Demos**

<p align="center">
  <video src="assets/early_training.mp4" width="320" height="240" controls></video><br/>
  <em>Early-stage training</em>
</p><br/>
<p align="center">
  <video src="assets/mid_training.mp4" width="320" height="240" controls></video><br/>
  <em>Mid-stage training</em>
</p><br/>
<p align="center">
  <video src="assets/late_training.mp4" width="320" height="240" controls></video><br/>
  <em>Late-stage training</em>
</p><br/>