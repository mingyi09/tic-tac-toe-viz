"""
Q-Learning Implementation for Tic-Tac-Toe
This implementation trains an agent to play Tic-Tac-Toe using Q-learning.
"""

import numpy as np
import random
# import pickle
import dill as pickle
from collections import defaultdict
import matplotlib.pyplot as plt


class TicTacToe:
    """
    Tic-Tac-Toe game environment.
    - Player 1 (X): uses state as-is
    - Player 2 (O): uses flipped state (1->2, 2->1)
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the game to initial state."""
        self.board = np.zeros((3, 3), dtype=int)
        self.current_player = 1  # Player 1 starts
        self.game_over = False
        self.winner = 0
        self.move_count = 0
        return self.get_state()
    
    def get_state(self):
        """Get current state as a tuple of the board."""
        return tuple(map(tuple, self.board))
    
    def get_valid_moves(self):
        """Get list of valid move positions."""
        valid_moves = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 0:
                    valid_moves.append((i, j))
        return valid_moves
    
    def make_move(self, position):
        """
        Make a move on the board.
        Returns: (new_state, reward, done, info)
        """
        if self.game_over:
            return self.get_state(), 0, True, {}
        
        i, j = position
        if self.board[i][j] != 0:
            # Invalid move
            return self.get_state(), -10, True, {}
        
        self.board[i][j] = self.current_player
        self.move_count += 1
        
        # Check for win
        if self._check_win(self.current_player):
            self.game_over = True
            self.winner = self.current_player
            reward = 1  # Win
            done = True
        elif self.move_count == 9:
            # Draw
            self.game_over = True
            self.winner = 0
            reward = 0.5  # Draw
            done = True
        else:
            reward = 0
            done = False
            # Switch players
            self.current_player = 3 - self.current_player
        
        info = {'winner': self.winner}
        return self.get_state(), reward, done, info
    
    def _check_win(self, player):
        """Check if the given player has won."""
        # Check rows
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)):
                return True
        
        # Check columns
        for j in range(3):
            if all(self.board[i][j] == player for i in range(3)):
                return True
        
        # Check diagonals
        if all(self.board[i][i] == player for i in range(3)):
            return True
        if all(self.board[i][2-i] == player for i in range(3)):
            return True
        
        return False
    
    def display(self):
        """Display the current board."""
        symbol_map = {0: '.', 1: 'X', 2: 'O'}
        print("\n  0 1 2")
        for i in range(3):
            print(f"{i} {' '.join(symbol_map[self.board[i][j]] for j in range(3))}")
        print()


class QLearningAgent:
    """
    Q-Learning agent for Tic-Tac-Toe.
    Now supports training both X and O agents in a single Q-table.
    """
    
    def __init__(self, learning_rate=0.1, discount=0.9, epsilon=1.0, 
                 epsilon_min=0.01, epsilon_decay=0.995):
        """
        Initialize Q-learning agent.
        
        Args:
            learning_rate: Learning rate (alpha)
            discount: Discount factor (gamma)
            epsilon: Epsilon for epsilon-greedy exploration
            epsilon_min: Minimum epsilon value
            epsilon_decay: Epsilon decay rate
        """
        self.learning_rate = learning_rate
        self.discount = discount
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Q-table: (state, player) -> action -> Q-value
        # player is 1 for X, 2 for O
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Statistics
        self.training_stats = {
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'episode_wins': [],
            'episode_losses': [],
            'episode_draws': []
        }
    
    def get_state_key(self, state, player):
        """
        Get state key for Q-table.
        Key is (state, player) tuple.
        """
        return (state, player)
    
    def get_action(self, state, valid_moves, player):
        """
        Choose action using epsilon-greedy policy.
        
        Args:
            state: Current board state
            valid_moves: List of valid moves
            player: Current player (1 for X, 2 for O)
        """
        if random.random() < self.epsilon:
            # Explore: random action
            return random.choice(valid_moves)
        else:
            # Exploit: best known action
            return self.get_best_action(state, valid_moves, player)
    
    def get_best_action(self, state, valid_moves, player):
        """
        Get the best action according to current Q-values.
        
        Args:
            state: Current board state
            valid_moves: List of valid moves
            player: Current player (1 for X, 2 for O)
        """
        state_key = self.get_state_key(state, player)
        
        if not valid_moves:
            return None
        
        # If state not in Q-table, return random action
        if state_key not in self.q_table or not self.q_table[state_key]:
            return random.choice(valid_moves)
        
        # Get Q-values for all valid moves
        q_values = {}
        for move in valid_moves:
            q_values[move] = self.q_table[state_key][move]
        
        # Return action with highest Q-value
        best_action = max(q_values, key=q_values.get)
        
        # If multiple actions have same Q-value, randomly choose one
        max_q_value = q_values[best_action]
        best_actions = [action for action, q_val in q_values.items() if q_val == max_q_value]
        
        return random.choice(best_actions)
    
    def update_q_value(self, state, action, reward, next_state, next_valid_moves, done, player, next_player=None):
        """
        Update Q-value using Q-learning update rule.
        Q(s,a) = Q(s,a) + alpha * (reward + gamma * max(Q(s',a')) - Q(s,a))
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            next_valid_moves: Valid moves in next state
            done: Whether episode is done
            player: Current player (1 for X, 2 for O)
            next_player: Next player (1 for X, 2 for O), defaults to 3 - player
        """
        if next_player is None:
            next_player = 3 - player  # Switch player
        
        state_key = self.get_state_key(state, player)
        next_state_key = self.get_state_key(next_state, next_player)
        
        # Current Q-value
        current_q = self.q_table[state_key][action]
        
        if done:
            # Terminal state
            td_target = reward
        else:
            # Get max Q-value for next state
            if next_valid_moves and next_state_key in self.q_table:
                max_next_q = max([self.q_table[next_state_key][action] 
                                 for action in next_valid_moves], default=0)
            else:
                max_next_q = 0
            
            td_target = reward + self.discount * max_next_q
        
        # TD error
        td_error = td_target - current_q
        
        # Update Q-value
        self.q_table[state_key][action] = current_q + self.learning_rate * td_error
    
    def decay_epsilon(self):
        """Decay epsilon value."""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


def train_q_learning(num_episodes=10000, opponent_type='self', save_model=True):
    """
    Train Q-learning agents for both X and O players.
    
    Args:
        num_episodes: Number of training episodes
        opponent_type: Type of opponent ('random' or 'self')
        save_model: Whether to save the trained model
    """
    print("=" * 60)
    print("Training Q-Learning Agents for Tic-Tac-Toe (X and O)")
    print("=" * 60)
    
    # Initialize single agent that learns for both players
    agent = QLearningAgent(learning_rate=0.1, discount=0.9, 
                          epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.9995)
    game = TicTacToe()
    
    # Training statistics
    win_rate_history = []
    
    for episode in range(num_episodes):
        state = game.reset()
        done = False
        action_history = []  # Store (state, action, player) tuples
        
        while not done:
            valid_moves = game.get_valid_moves()
            current_player = game.current_player
            
            if opponent_type == 'self':
                # Self-play: both players use the same agent
                action = agent.get_action(state, valid_moves, current_player)
                action_history.append((state, action, current_player))
                
                next_state, reward, done, info = game.make_move(action)
                
                if done:
                    # Game ended - update Q-value with final reward
                    if info['winner'] == current_player:
                        # Current player won
                        final_reward = 1
                    elif info['winner'] == 0:
                        # Draw
                        final_reward = 0.5
                    else:
                        # Current player lost (shouldn't happen on their move)
                        final_reward = -1
                    
                    agent.update_q_value(state, action, final_reward, next_state, [], done, current_player)
                    
                    # Update opponent's last move if applicable
                    if len(action_history) > 1:
                        prev_state, prev_action, prev_player = action_history[-2]
                        opp_reward = -final_reward if info['winner'] != 0 else -0.5
                        agent.update_q_value(prev_state, prev_action, opp_reward, next_state, [], done, prev_player, current_player)
                    break
                else:
                    # Update Q-value for current move
                    next_valid_moves = game.get_valid_moves()
                    next_player = game.current_player
                    agent.update_q_value(state, action, 0, next_state, next_valid_moves, False, current_player, next_player)
                    state = next_state
                    
            else:
                # Random opponent mode
                if current_player == 1:
                    # Agent (X) plays
                    action = agent.get_action(state, valid_moves, current_player)
                    action_history.append((state, action, current_player))
                    
                    next_state, reward, done, info = game.make_move(action)
                    
                    if done:
                        if info['winner'] == 1:
                            final_reward = 1
                        elif info['winner'] == 0:
                            final_reward = 0.5
                        else:
                            final_reward = -1
                        agent.update_q_value(state, action, final_reward, next_state, [], done, current_player)
                        break
                    else:
                        # Random opponent's turn
                        next_valid_moves = game.get_valid_moves()
                        opponent_action = random.choice(next_valid_moves)
                        opponent_next_state, opponent_reward, opponent_done, opponent_info = game.make_move(opponent_action)
                        
                        if opponent_done:
                            # Opponent won or draw
                            final_reward = -1 if opponent_info['winner'] == 2 else -0.5
                            agent.update_q_value(state, action, final_reward, opponent_next_state, [], True, current_player)
                            done = True
                            break
                        else:
                            # Update Q-value for agent's move
                            agent.update_q_value(state, action, 0, opponent_next_state, game.get_valid_moves(), False, current_player, 2)
                            state = opponent_next_state
                else:
                    # Random opponent's turn (not learning)
                    action = random.choice(valid_moves)
                    state, reward, done, info = game.make_move(action)
        
        # Decay epsilon
        agent.decay_epsilon()
        
        # Track statistics
        if (episode + 1) % 1000 == 0:
            wins, losses, draws = evaluate_agent(agent, num_games=100)
            win_rate = wins / 100
            win_rate_history.append(win_rate)
            
            # Count unique states for each player
            states_player1 = sum(1 for (s, p) in agent.q_table.keys() if p == 1)
            states_player2 = sum(1 for (s, p) in agent.q_table.keys() if p == 2)
            
            print(f"Episode {episode + 1}/{num_episodes} | "
                  f"Epsilon: {agent.epsilon:.4f} | "
                  f"Win Rate: {win_rate:.2%} | "
                  f"Q-table size: {len(agent.q_table)} states "
                  f"(X: {states_player1}, O: {states_player2})")
    
    # Final evaluation
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    final_wins, final_losses, final_draws = evaluate_agent(agent, num_games=1000)
    print(f"\nFinal Performance:")
    print(f"  Wins: {final_wins} ({final_wins/10:.1f}%)")
    print(f"  Losses: {final_losses} ({final_losses/10:.1f}%)")
    print(f"  Draws: {final_draws} ({final_draws/10:.1f}%)")
    
    # Count states by player
    states_player1 = sum(1 for (s, p) in agent.q_table.keys() if p == 1)
    states_player2 = sum(1 for (s, p) in agent.q_table.keys() if p == 2)
    print(f"\n  Q-table size: {len(agent.q_table)} states")
    print(f"    Player 1 (X): {states_player1} states")
    print(f"    Player 2 (O): {states_player2} states")
    
    # Save model
    if save_model:
        filename = 'q_learning_tictactoe.pkl'
        with open(filename, 'wb') as f:
            pickle.dump(agent, f)
        print(f"\n  Model saved to: {filename}")
    
    # Plot training progress
    if win_rate_history:
        plt.figure(figsize=(10, 6))
        plt.plot(range(1000, num_episodes + 1, 1000), win_rate_history)
        plt.xlabel('Episode')
        plt.ylabel('Win Rate')
        plt.title('Q-Learning Training Progress')
        plt.grid(True)
        plt.savefig('training_progress.png')
        print(f"  Training plot saved to: training_progress.png")
    
    return agent


def evaluate_agent(agent, num_games=100, opponent='random'):
    """
    Evaluate trained agent against a random opponent.
    """
    agent.epsilon = 0  # No exploration during evaluation
    game = TicTacToe()
    
    wins = 0
    losses = 0
    draws = 0
    
    for _ in range(num_games):
        state = game.reset()
        done = False
        
        while not done:
            valid_moves = game.get_valid_moves()
            current_player = game.current_player
            
            if current_player == 1:  # Agent's turn (X)
                action = agent.get_best_action(state, valid_moves, current_player)
                state, reward, done, info = game.make_move(action)
                
                if done:
                    if info['winner'] == 1:
                        wins += 1
                    elif info['winner'] == 0:
                        draws += 1
                    break
            else:
                # Random opponent
                action = random.choice(valid_moves)
                state, reward, done, info = game.make_move(action)
                
                if done:
                    if info['winner'] == 2:
                        losses += 1
                    break
    
    return wins, losses, draws


def play_against_agent(model_file='q_learning_tictactoe.pkl'):
    """
    Play a game against the trained agent.
    """
    print("\n" + "=" * 60)
    print("Playing against Q-Learning Agent")
    print("=" * 60)
    
    # Load agent
    try:
        with open(model_file, 'rb') as f:
            agent = pickle.load(f)
        agent.epsilon = 0  # No exploration
    except FileNotFoundError:
        print(f"Model file {model_file} not found. Please train the agent first.")
        return
    
    game = TicTacToe()
    state = game.reset()
    done = False
    
    print("\nYou are Player 2 (O), AI is Player 1 (X)")
    print("Enter row and column (e.g., '0 1' for top-middle)")
    
    while not done:
        game.display()
        valid_moves = game.get_valid_moves()
        
        if game.current_player == 1:  # AI's turn
            print("\nAI's turn...")
            action = agent.get_best_action(state, valid_moves, 1)
            state, reward, done, info = game.make_move(action)
            game.display()
            
            if done:
                if info['winner'] == 1:
                    print("AI wins!")
                elif info['winner'] == 0:
                    print("It's a draw!")
                break
        else:  # Player's turn
            print(f"\nYour turn (O). Valid moves: {valid_moves}")
            try:
                row, col = map(int, input("Enter row and column: ").split())
                action = (row, col)
                
                if action not in valid_moves:
                    print("Invalid move! Try again.")
                    continue
                
                state, reward, done, info = game.make_move(action)
                
                if done:
                    if info['winner'] == 2:
                        print("You win!")
                    elif info['winner'] == 0:
                        print("It's a draw!")
                    break
            except (ValueError, IndexError):
                print("Invalid input! Enter two numbers separated by space.")
                continue


def main():
    """
    Main function to run Q-learning training and evaluation.
    """
    # Train the agent (both X and O)
    agent = train_q_learning(num_episodes=10000, opponent_type='self', save_model=True)

    # Optionally play against the agent
    print("\n" + "=" * 60)
    response = input("Would you like to play against the agent? (y/n): ")
    if response.lower() == 'y':
        play_against_agent()



if __name__ == "__main__":
    main()
