# Q-Learning for Tic-Tac-Toe

This implements a Q-learning algorithm to learn and play the game of Tic-Tac-Toe.

## Features

- **Complete Tic-Tac-Toe Environment**: Full game implementation with win/draw detection
- **Q-Learning Agent**: A Reinforcement Learning agent that learns optimal play through experience
- **Training & Evaluation**: Comprehensive training loop with performance tracking
- **Interactive Play**: Play against the trained agent
- **Visualization**: Training progress plots
- **Model Persistence**: Save and load trained models

## How It Works

### Q-Learning Algorithm

Q-learning is a model-free reinforcement learning algorithm that learns the value of state-action pairs through trial and error:

**Q-Update Formula:**
```
Q(s,a) = Q(s,a) + α * [reward + γ * max(Q(s',a')) - Q(s,a)]
```

Where:
- `α` (learning_rate) = 0.1
- `γ` (discount) = 0.9
- `ε` (epsilon) = 1.0 (exploration) → 0.01 (exploitation)

### State Representation

Each state is represented as a 3×3 tuple of the board:
- `0` = empty cell
- `1` = Player 1 (X)
- `2` = Player 2 (O)

### Rewards

- **Win**: +1
- **Draw**: +0.5
- **Loss**: -1


### Key Components

1. **TicTacToe Class**: Game environment with board management and win detection
2. **QLearningAgent Class**: Q-learning agent with epsilon-greedy exploration
3. **Training Function**: Trains agent against random opponent
4. **Evaluation Function**: Tests trained agent performance
5. **Interactive Play**: Human vs AI gameplay

## Usage

### Running the Training

```bash
python Q_learning.py
```

This will:
1. Train the Q-learning agent for 10,000 episodes
2. Save the trained model to `q_learning_tictactoe.pkl`
3. Display training progress every 1000 episodes
4. Generate training progress plot
5. Optionally let you play against the agent

### Key Functions

#### Train an Agent
```python
from Q_learning import train_q_learning

agent = train_q_learning(
    num_episodes=10000,
    opponent_type='random',  # or 'self'
    save_model=True
)
```

#### Evaluate Performance
```python
from Q_learning import evaluate_agent

wins, losses, draws = evaluate_agent(agent, num_games=100)
```

#### Play Against Agent
```python
from Q_learning import play_against_agent

play_against_agent(model_file='q_learning_tictactoe.pkl')
```

### Customizing Training

Edit the `main()` function to customize:

```python
# Training parameters
num_episodes = 10000          # Number of training episodes
learning_rate = 0.1           # Alpha - how fast to learn
discount = 0.9                # Gamma - future reward importance
epsilon = 1.0                 # Initial exploration rate
epsilon_min = 0.01           # Minimum exploration rate
epsilon_decay = 0.9995       # Exploration decay rate
```

## Expected Results

After training (~10,000 episodes), the agent should achieve:
- **Win rate**: ~70-90% against random opponent
- **Draw rate**: ~10-20%
- **Loss rate**: ~5-10%

Note: The agent may not achieve 100% win rate because Tic-Tac-Toe is a draw when both players play optimally.

## Files Generated

- `q_learning_tictactoe.pkl`: Trained Q-learning model
- `training_progress.png`: Training statistics visualization

## How to Play

1. Run the training script
2. When prompted, choose to play against the agent
3. Enter moves as row and column (e.g., "0 1" for top-middle)
4. Agent uses X, you play as O
5. Try to beat the AI!

## Algorithm Details


### State Normalization

For player 2, states are flipped to normalize the perspective, allowing the agent to learn more efficiently.

### Q-Table Structure

```python
Q_table: {
    state_hash: {
        action: Q_value
    }
}
```


## Requirements

```
numpy
matplotlib
```