"""
Value Iteration Implementation for Tic-Tac-Toe
This implementation computes optimal policy for both X and O players using value iteration.
"""

import numpy as np
import random
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
    
    def copy(self):
        """Create a deep copy of the game state."""
        new_game = TicTacToe()
        new_game.board = self.board.copy()
        new_game.current_player = self.current_player
        new_game.game_over = self.game_over
        new_game.winner = self.winner
        new_game.move_count = self.move_count
        return new_game
    
    def display(self):
        """Display the current board."""
        symbol_map = {0: '.', 1: 'X', 2: 'O'}
        print("\n  0 1 2")
        for i in range(3):
            print(f"{i} {' '.join(symbol_map[self.board[i][j]] for j in range(3))}")
        print()


class ValueIterationAgent:
    """
    Value Iteration agent for Tic-Tac-Toe.
    Computes optimal policy for both X and O players.
    """
    
    def __init__(self, discount=0.9, convergence_threshold=1e-6):
        """
        Initialize Value Iteration agent.
        
        Args:
            discount: Discount factor (gamma)
            convergence_threshold: Threshold for value convergence
        """
        self.discount = discount
        self.convergence_threshold = convergence_threshold
        
        # Value function: (state, player) -> value
        self.values = defaultdict(float)
        
        # Policy: (state, player) -> action -> probability
        # Similar structure to Q-learning for compatibility
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Statistics
        self.training_stats = {
            'iterations': 0,
            'converged': False
        }
    
    def get_state_key(self, state, player):
        """Get state key for value table."""
        return (state, player)
    
    def get_all_states(self):
        """
        Generate all possible game states.
        Returns a set of (state, player) tuples.
        Generates all valid game states by exploring all possible move sequences.
        """
        states = set()
        visited_boards = set()  # Track visited board configurations
        
        def is_valid_state(state_tuple):
            """
            Check if a state is valid (follows game rules).
            - X and O must alternate (count_x == count_o or count_x == count_o + 1)
            - Can't have both players winning
            """
            count_x = sum(1 for row in state_tuple for cell in row if cell == 1)
            count_o = sum(1 for row in state_tuple for cell in row if cell == 2)
            
            # X goes first, so count_x should be count_o or count_o + 1
            if count_x < count_o or count_x > count_o + 1:
                return False
            
            # Check for wins
            game = TicTacToe()
            game.board = np.array(state_tuple)
            x_wins = game._check_win(1)
            o_wins = game._check_win(2)
            
            # Can't have both players winning
            if x_wins and o_wins:
                return False
            
            return True
        
        def get_player_for_state(state_tuple):
            """
            Determine which player's turn it is based on the board state.
            """
            count_x = sum(1 for row in state_tuple for cell in row if cell == 1)
            count_o = sum(1 for row in state_tuple for cell in row if cell == 2)
            
            if count_x == count_o:
                return 1  # X's turn
            else:
                return 2  # O's turn
        
        def generate_states_recursive(state_tuple, player, depth=0):
            """Recursively generate all reachable states."""
            if depth > 9:  # Max depth (9 moves)
                return
            
            # Check if state is valid
            if not is_valid_state(state_tuple):
                return
            
            # Add state with the player whose turn it is
            state_key = (state_tuple, player)
            if state_key in states:
                return  # Already visited
            
            states.add(state_key)
            
            # Also track board configuration separately for debugging
            if state_tuple not in visited_boards:
                visited_boards.add(state_tuple)
            
            # Create a fresh game object for this state
            game = TicTacToe()
            game.board = np.array(state_tuple)
            game.current_player = player
            game.move_count = sum(1 for row in state_tuple for cell in row if cell != 0)
            
            # Check if terminal
            game.game_over = False
            game.winner = 0
            
            # Check for win
            if game._check_win(1):
                game.game_over = True
                game.winner = 1
            elif game._check_win(2):
                game.game_over = True
                game.winner = 2
            elif game.move_count == 9:
                game.game_over = True
                game.winner = 0
            
            if game.game_over:
                return  # Terminal state, don't generate children
            
            # Generate next states by trying all valid moves
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                return  # No valid moves (shouldn't happen for non-terminal)
            
            for move in valid_moves:
                i, j = move
                # Create a new board state - make sure we copy properly
                new_board = np.array(state_tuple, dtype=int).copy()
                new_board[i][j] = player
                new_state = tuple(map(tuple, new_board))
                
                # Verify the new state is valid before recursing
                if is_valid_state(new_state):
                    next_player = 3 - player
                    generate_states_recursive(new_state, next_player, depth + 1)
        
        # Start from empty board with player 1
        empty_state = ((0, 0, 0), (0, 0, 0), (0, 0, 0))
        generate_states_recursive(empty_state, 1, 0)
        
        print(f"  Generated {len(visited_boards)} unique board configurations")
        print(f"  Generated {len(states)} state-player pairs")
        
        # Debug: Show some example states
        def state_to_str(state_tuple):
            """Helper to convert state to string for debugging."""
            symbol_map = {0: '.', 1: 'X', 2: 'O'}
            result = []
            for row in state_tuple:
                for cell in row:
                    result.append(symbol_map[cell])
            return ''.join(result)
        
        if len(states) < 100:
            print(f"\n  Sample states (first 10):")
            for i, (state, player) in enumerate(list(states)[:10]):
                state_str = state_to_str(state)
                print(f"    {i+1}. {state_str} (player {player})")
        
        return states
    
    def get_reward(self, state, player, next_state, done, winner):
        """
        Get reward for a state transition.
        
        Args:
            state: Current state
            player: Current player (1 for X, 2 for O)
            next_state: Next state
            done: Whether game is done
            winner: Winner (1, 2, or 0 for draw)
        """
        if not done:
            return 0
        
        if winner == player:
            return 1.0  # Win
        elif winner == 0:
            return 0.5  # Draw
        else:
            return -1.0  # Loss
    
    def get_next_state(self, state, action, player):
        """
        Get next state after taking an action.
        
        Args:
            state: Current state tuple
            action: Action (row, col)
            player: Current player
        
        Returns:
            (next_state, done, winner)
        """
        game = TicTacToe()
        game.board = np.array(state)
        game.current_player = player
        game.move_count = sum(1 for row in state for cell in row if cell != 0)
        
        i, j = action
        if game.board[i][j] != 0:
            return state, True, 0  # Invalid move
        
        game.board[i][j] = player
        game.move_count += 1
        
        # Check for win
        if game._check_win(player):
            return tuple(map(tuple, game.board)), True, player
        elif game.move_count == 9:
            return tuple(map(tuple, game.board)), True, 0
        else:
            return tuple(map(tuple, game.board)), False, 0
    
    def value_iteration(self):
        """
        Perform value iteration to compute optimal values.
        """
        print("Generating all possible states...")
        all_states = self.get_all_states()
        print(f"Found {len(all_states)} unique state-player pairs")
        
        # Debug: Show breakdown by player
        states_p1 = sum(1 for (s, p) in all_states if p == 1)
        states_p2 = sum(1 for (s, p) in all_states if p == 2)
        print(f"  Player 1 (X) states: {states_p1}")
        print(f"  Player 2 (O) states: {states_p2}")
        
        # Initialize values
        for state_key in all_states:
            state, player = state_key
            # Check if terminal
            game = TicTacToe()
            game.board = np.array(state)
            game.move_count = sum(1 for row in state for cell in row if cell != 0)
            
            if game._check_win(1):
                # Player 1 won
                self.values[state_key] = 1.0 if player == 1 else -1.0
            elif game._check_win(2):
                # Player 2 won
                self.values[state_key] = 1.0 if player == 2 else -1.0
            elif game.move_count == 9:
                # Draw
                self.values[state_key] = 0.5
            else:
                # Non-terminal, initialize to 0
                self.values[state_key] = 0.0
        
        # Value iteration
        print("\nStarting value iteration...")
        iteration = 0
        max_iterations = 1000
        
        while iteration < max_iterations:
            iteration += 1
            max_change = 0.0
            
            # Update values for all states
            new_values = self.values.copy()
            
            for state_key in all_states:
                state, player = state_key
                
                # Skip terminal states (values don't change)
                game = TicTacToe()
                game.board = np.array(state)
                game.move_count = sum(1 for row in state for cell in row if cell != 0)
                
                if game._check_win(1) or game._check_win(2) or game.move_count == 9:
                    continue  # Terminal state, skip
                
                # Get valid moves
                valid_moves = game.get_valid_moves()
                if not valid_moves:
                    continue
                
                # Compute value for each action
                action_values = {}
                for action in valid_moves:
                    next_state, done, winner = self.get_next_state(state, action, player)
                    next_player = 3 - player
                    next_state_key = (next_state, next_player)
                    
                    reward = self.get_reward(state, player, next_state, done, winner)
                    
                    if done:
                        # Terminal state
                        value = reward
                    else:
                        # Non-terminal: value = reward + discount * V(next_state)
                        next_value = self.values.get(next_state_key, 0.0)
                        value = reward + self.discount * next_value
                    
                    action_values[action] = value
                
                # Update value: V(s) = max_a [R(s,a) + γ * V(s')]
                if action_values:
                    new_value = max(action_values.values())
                    old_value = self.values[state_key]
                    new_values[state_key] = new_value
                    max_change = max(max_change, abs(new_value - old_value))
            
            # Update values
            self.values = new_values
            
            # Check convergence
            if max_change < self.convergence_threshold:
                print(f"Converged after {iteration} iterations (max change: {max_change:.2e})")
                self.training_stats['converged'] = True
                break
            
            if iteration % 10 == 0:
                print(f"Iteration {iteration}: max change = {max_change:.6f}")
        
        self.training_stats['iterations'] = iteration
        
        if not self.training_stats['converged']:
            print(f"Stopped after {max_iterations} iterations (max change: {max_change:.6f})")
        
        # Compute policy (Q-table) from values
        print("\nComputing policy from values...")
        self._compute_policy(all_states)
        
        # Count states by type
        terminal_count = 0
        non_terminal_count = 0
        for state_key in all_states:
            state, player = state_key
            game = TicTacToe()
            game.board = np.array(state)
            game.move_count = sum(1 for row in state for cell in row if cell != 0)
            if game._check_win(1) or game._check_win(2) or game.move_count == 9:
                terminal_count += 1
            else:
                non_terminal_count += 1
        
        print(f"Policy computed for {len(self.q_table)} states")
        print(f"  Total states: {len(all_states)}")
        print(f"  Terminal states: {terminal_count}")
        print(f"  Non-terminal states: {non_terminal_count}")
        print(f"  States in q_table: {len(self.q_table)}")
        
        if len(self.q_table) != len(all_states):
            print(f"  WARNING: {len(all_states) - len(self.q_table)} states missing from q_table!")
    
    def _compute_policy(self, all_states):
        """
        Compute policy (action probabilities) from value function.
        Stores in q_table format similar to Q-learning.
        Includes ALL states (both terminal and non-terminal).
        """
        # First, ensure ALL states are in q_table
        for state_key in all_states:
            if state_key not in self.q_table:
                self.q_table[state_key] = {}
        
        # Now compute Q-values for non-terminal states
        for state_key in all_states:
            state, player = state_key
            
            # Check if terminal state
            game = TicTacToe()
            game.board = np.array(state)
            game.move_count = sum(1 for row in state for cell in row if cell != 0)
            
            is_terminal = False
            if game._check_win(1) or game._check_win(2) or game.move_count == 9:
                is_terminal = True
                # Terminal states have no actions, but they're already in q_table
                # with empty action dictionary
                continue
            
            valid_moves = game.get_valid_moves()
            if not valid_moves:
                # No valid moves (shouldn't happen for non-terminal, but handle it)
                # State is already in q_table with empty dict
                continue
            
            # Compute Q-values for each action
            for action in valid_moves:
                next_state, done, winner = self.get_next_state(state, action, player)
                next_player = 3 - player
                next_state_key = (next_state, next_player)
                
                reward = self.get_reward(state, player, next_state, done, winner)
                
                if done:
                    q_value = reward
                else:
                    next_value = self.values.get(next_state_key, 0.0)
                    q_value = reward + self.discount * next_value
                
                self.q_table[state_key][action] = q_value
    
    def get_best_action(self, state, valid_moves, player):
        """
        Get the best action according to the computed policy.
        
        Args:
            state: Current board state
            valid_moves: List of valid moves
            player: Current player (1 for X, 2 for O)
        """
        state_key = self.get_state_key(state, player)
        
        if not valid_moves:
            return None
        
        if state_key not in self.q_table or not self.q_table[state_key]:
            return random.choice(valid_moves)
        
        # Get Q-values for all valid moves
        q_values = {}
        for move in valid_moves:
            if move in self.q_table[state_key]:
                q_values[move] = self.q_table[state_key][move]
            else:
                q_values[move] = 0.0
        
        # Return action with highest Q-value
        best_action = max(q_values, key=q_values.get)
        
        # If multiple actions have same Q-value, randomly choose one
        max_q_value = q_values[best_action]
        best_actions = [action for action, q_val in q_values.items() if q_val == max_q_value]
        
        return random.choice(best_actions)


def train_value_iteration(save_model=True):
    """
    Train Value Iteration agent for both X and O players.
    
    Args:
        save_model: Whether to save the trained model
    """
    print("=" * 60)
    print("Training Value Iteration Agent for Tic-Tac-Toe (X and O)")
    print("=" * 60)
    
    agent = ValueIterationAgent(discount=0.9, convergence_threshold=1e-6)
    
    # Run value iteration
    agent.value_iteration()
    
    # Count states by player
    states_player1 = sum(1 for (s, p) in agent.q_table.keys() if p == 1)
    states_player2 = sum(1 for (s, p) in agent.q_table.keys() if p == 2)
    
    print(f"\n  Q-table size: {len(agent.q_table)} states")
    print(f"    Player 1 (X): {states_player1} states")
    print(f"    Player 2 (O): {states_player2} states")
    
    # Save model
    if save_model:
        filename = 'value_iteration_tictactoe.pkl'
        with open(filename, 'wb') as f:
            pickle.dump(agent, f)
        print(f"\n  Model saved to: {filename}")
    
    return agent


def evaluate_agent(agent, num_games=100, opponent='random'):
    """
    Evaluate trained agent against a random opponent.
    """
    import random
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


def main():
    """
    Main function to run value iteration training.
    """
    # Train the agent (both X and O)
    agent = train_value_iteration(save_model=True)
    
    # Evaluate
    print("\n" + "=" * 60)
    print("Evaluation")
    print("=" * 60)
    wins, losses, draws = evaluate_agent(agent, num_games=1000)
    print(f"\nPerformance against random opponent:")
    print(f"  Wins: {wins} ({wins/10:.1f}%)")
    print(f"  Losses: {losses} ({losses/10:.1f}%)")
    print(f"  Draws: {draws} ({draws/10:.1f}%)")


if __name__ == "__main__":
    main()

