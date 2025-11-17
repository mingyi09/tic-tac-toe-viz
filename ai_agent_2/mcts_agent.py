"""
Monte Carlo Tree Search (MCTS) Implementation for Tic-Tac-Toe
This implementation trains an agent to play Tic-Tac-Toe using MCTS.
"""

import numpy as np
import random
import dill as pickle
import math
import matplotlib.pyplot as plt
from collections import defaultdict


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


class MCTSNode:
    """
    Node in the Monte Carlo Tree Search tree.
    """
    
    def __init__(self, state, player, parent=None, action=None):
        """
        Initialize MCTS node.
        
        Args:
            state: Current game state (board tuple)
            player: Player who will make the next move (1 for X, 2 for O)
            parent: Parent node
            action: Action that led to this state
        """
        self.state = state
        self.player = player
        self.parent = parent
        self.action = action
        
        # MCTS statistics
        self.visits = 0
        self.wins = 0.0  # Total wins (can be fractional for draws)
        self.children = {}  # action -> MCTSNode
        
        # Unexplored actions
        self.untried_actions = None
    
    def is_fully_expanded(self):
        """Check if all actions have been tried."""
        if self.untried_actions is None:
            return False  # Not initialized yet, so not fully expanded
        return len(self.untried_actions) == 0
    
    def is_terminal(self, game):
        """Check if this is a terminal state."""
        return game.game_over
    
    def get_ucb_value(self, exploration_constant=1.414):
        """
        Calculate UCB1 value for this node.
        UCB1 = (wins / visits) + c * sqrt(ln(parent_visits) / visits)
        
        Args:
            exploration_constant: Exploration constant (default sqrt(2))
        """
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.wins / self.visits
        
        if self.parent is None:
            parent_visits = self.visits
        else:
            parent_visits = self.parent.visits
        
        if parent_visits == 0:
            exploration = 0
        else:
            exploration = exploration_constant * math.sqrt(math.log(parent_visits) / self.visits)
        
        return exploitation + exploration
    
    def select_child(self, exploration_constant=1.414):
        """
        Select child node with highest UCB1 value.
        
        Args:
            exploration_constant: Exploration constant for UCB1
        """
        return max(self.children.values(), 
                  key=lambda node: node.get_ucb_value(exploration_constant))
    
    def add_child(self, action, state, player):
        """
        Add a child node.
        
        Args:
            action: Action taken
            state: Resulting state
            player: Player for the new state
        """
        child = MCTSNode(state, player, parent=self, action=action)
        self.children[action] = child
        return child
    
    def update(self, result):
        """
        Update node statistics after simulation.
        
        Args:
            result: Result from the perspective of the node's player
                   1.0 for win, 0.5 for draw, 0.0 for loss
        """
        self.visits += 1
        self.wins += result
    
    def get_best_action(self):
        """
        Get the action with the most visits (best move).
        """
        if not self.children:
            return None
        return max(self.children.items(), key=lambda x: x[1].visits)[0]


class MCTSAgent:
    """
    Monte Carlo Tree Search agent for Tic-Tac-Toe.
    """
    
    def __init__(self, num_simulations=1000, exploration_constant=1.414, 
                 use_temperature=False, temperature=1.0):
        """
        Initialize MCTS agent.
        
        Args:
            num_simulations: Number of MCTS simulations per move
            exploration_constant: UCB1 exploration constant (default sqrt(2))
            use_temperature: Whether to use temperature for move selection
            temperature: Temperature for move selection (higher = more random)
        """
        self.num_simulations = num_simulations
        self.exploration_constant = exploration_constant
        self.use_temperature = use_temperature
        self.temperature = temperature
        
        # Root node cache (state, player) -> root_node
        self.root_cache = {}
        
        # Statistics
        self.training_stats = {
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'episode_wins': [],
            'episode_losses': [],
            'episode_draws': []
        }
    
    def _simulate_random_game(self, game):
        """
        Simulate a random game from current state to terminal state.
        
        Args:
            game: TicTacToe game instance
            
        Returns:
            Result from perspective of the player at the start of simulation
            1.0 for win, 0.5 for draw, 0.0 for loss
        """
        game_copy = game.copy()
        starting_player = game_copy.current_player
        
        while not game_copy.game_over:
            valid_moves = game_copy.get_valid_moves()
            if not valid_moves:
                break
            action = random.choice(valid_moves)
            game_copy.make_move(action)
        
        # Determine result from starting player's perspective
        if game_copy.winner == starting_player:
            return 1.0
        elif game_copy.winner == 0:
            return 0.5
        else:
            return 0.0
    
    def _select(self, node, game):
        """
        Selection phase: traverse tree using UCB1 until leaf node.
        
        Args:
            node: Current node
            game: Game instance (will be modified during traversal)
        
        Returns:
            Selected node
        """
        while not node.is_terminal(game) and node.is_fully_expanded():
            node = node.select_child(self.exploration_constant)
            game.make_move(node.action)
        
        return node
    
    def _expand(self, node, game):
        """
        Expansion phase: add a new child node.
        
        Args:
            node: Node to expand
            game: Game instance in the node's state
        
        Returns:
            New child node
        """
        if node.untried_actions is None:
            node.untried_actions = game.get_valid_moves()
        
        if not node.untried_actions:
            return node  # Terminal node, cannot expand
        
        action = node.untried_actions.pop()
        game.make_move(action)
        new_state = game.get_state()
        new_player = game.current_player
        
        child = node.add_child(action, new_state, new_player)
        return child
    
    def _backpropagate(self, node, result):
        """
        Backpropagation phase: update statistics up the tree.
        
        Args:
            node: Node to start backpropagation from
            result: Result from the perspective of the node's player
        """
        current_node = node
        current_result = result
        
        while current_node is not None:
            current_node.update(current_result)
            # For parent, result is inverted (opponent's perspective)
            if current_node.parent is not None:
                if current_result == 1.0:
                    current_result = 0.0
                elif current_result == 0.0:
                    current_result = 1.0
                # Draw remains 0.5
            current_node = current_node.parent
    
    def _mcts_search(self, game):
        """
        Perform one MCTS iteration: selection, expansion, simulation, backpropagation.
        
        Args:
            game: TicTacToe game instance
        """
        # Get or create root node
        state = game.get_state()
        player = game.current_player
        root_key = (state, player)
        
        if root_key not in self.root_cache:
            root_node = MCTSNode(state, player)
            root_node.untried_actions = game.get_valid_moves()
            self.root_cache[root_key] = root_node
        else:
            root_node = self.root_cache[root_key]
        
        # Selection: traverse to leaf
        game_copy = game.copy()
        node = self._select(root_node, game_copy)
        
        # Expansion: add new child if not terminal
        if not node.is_terminal(game_copy):
            node = self._expand(node, game_copy)
        
        # Simulation: play random game to terminal
        result = self._simulate_random_game(game_copy)
        
        # Backpropagation: update statistics
        # Result from node's player perspective
        node_result = result
        self._backpropagate(node, node_result)
    
    def get_action(self, game, num_simulations=None):
        """
        Get best action using MCTS.
        
        Args:
            game: TicTacToe game instance
            num_simulations: Number of simulations (overrides default if provided)
        
        Returns:
            Best action (row, col)
        """
        if num_simulations is None:
            num_simulations = self.num_simulations
        
        state = game.get_state()
        player = game.current_player
        root_key = (state, player)
        
        # Create root node if it doesn't exist
        if root_key not in self.root_cache:
            root_node = MCTSNode(state, player)
            root_node.untried_actions = game.get_valid_moves()
            self.root_cache[root_key] = root_node
        else:
            root_node = self.root_cache[root_key]
        
        # Perform MCTS simulations
        for _ in range(num_simulations):
            self._mcts_search(game)
        
        # Select best action
        if self.use_temperature and self.temperature > 0:
            # Use temperature for move selection (probabilistic)
            actions = list(root_node.children.keys())
            visits = [root_node.children[action].visits for action in actions]
            
            # Apply temperature
            if self.temperature == 0:
                # Greedy selection
                best_idx = np.argmax(visits)
            else:
                # Softmax with temperature
                logits = np.array(visits) / self.temperature
                logits = logits - np.max(logits)  # Numerical stability
                probs = np.exp(logits) / np.sum(np.exp(logits))
                best_idx = np.random.choice(len(actions), p=probs)
            
            return actions[best_idx]
        else:
            # Greedy selection: most visits
            return root_node.get_best_action()
    
    def clear_cache(self):
        """Clear the root node cache."""
        self.root_cache.clear()


def train_mcts(num_episodes=1000, num_simulations=1000, opponent_type='self', 
               save_model=True, exploration_constant=1.414):
    """
    Train MCTS agent through self-play or against random opponent.
    
    Args:
        num_episodes: Number of training episodes
        num_simulations: Number of MCTS simulations per move
        opponent_type: Type of opponent ('random' or 'self')
        save_model: Whether to save the trained model
        exploration_constant: UCB1 exploration constant
    """
    print("=" * 60)
    print("Training MCTS Agent for Tic-Tac-Toe")
    print("=" * 60)
    
    agent = MCTSAgent(num_simulations=num_simulations, 
                     exploration_constant=exploration_constant)
    game = TicTacToe()
    
    # Training statistics
    win_rate_history = []
    
    for episode in range(num_episodes):
        state = game.reset()
        done = False
        
        while not done:
            valid_moves = game.get_valid_moves()
            current_player = game.current_player
            
            if opponent_type == 'self':
                # Self-play: both players use MCTS
                action = agent.get_action(game, num_simulations=num_simulations)
                state, reward, done, info = game.make_move(action)
                
                if done:
                    # Update statistics
                    if info['winner'] == 1:
                        agent.training_stats['wins'] += 1
                    elif info['winner'] == 2:
                        agent.training_stats['losses'] += 1
                    else:
                        agent.training_stats['draws'] += 1
                    break
                    
            else:
                # Random opponent mode
                if current_player == 1:
                    # Agent (X) plays
                    action = agent.get_action(game, num_simulations=num_simulations)
                    state, reward, done, info = game.make_move(action)
                    
                    if done:
                        if info['winner'] == 1:
                            agent.training_stats['wins'] += 1
                        elif info['winner'] == 0:
                            agent.training_stats['draws'] += 1
                        else:
                            agent.training_stats['losses'] += 1
                        break
                else:
                    # Random opponent's turn
                    action = random.choice(valid_moves)
                    state, reward, done, info = game.make_move(action)
                    
                    if done:
                        if info['winner'] == 2:
                            agent.training_stats['losses'] += 1
                        elif info['winner'] == 0:
                            agent.training_stats['draws'] += 1
                        break
        
        # Clear cache periodically to save memory
        if (episode + 1) % 100 == 0:
            agent.clear_cache()
        
        # Track statistics
        if (episode + 1) % 100 == 0:
            wins, losses, draws = evaluate_agent(agent, num_games=100, 
                                                num_simulations=num_simulations)
            win_rate = wins / 100
            win_rate_history.append(win_rate)
            
            print(f"Episode {episode + 1}/{num_episodes} | "
                  f"Win Rate: {win_rate:.2%} | "
                  f"Cache size: {len(agent.root_cache)} states")
    
    # Final evaluation
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    final_wins, final_losses, final_draws = evaluate_agent(agent, num_games=1000,
                                                          num_simulations=num_simulations)
    print(f"\nFinal Performance:")
    print(f"  Wins: {final_wins} ({final_wins/10:.1f}%)")
    print(f"  Losses: {final_losses} ({final_losses/10:.1f}%)")
    print(f"  Draws: {final_draws} ({final_draws/10:.1f}%)")
    print(f"\n  Cache size: {len(agent.root_cache)} states")
    
    # Save model
    if save_model:
        filename = 'mcts_tictactoe.pkl'
        with open(filename, 'wb') as f:
            pickle.dump(agent, f)
        print(f"\n  Model saved to: {filename}")
    
    # Plot training progress
    if win_rate_history:
        plt.figure(figsize=(10, 6))
        plt.plot(range(100, num_episodes + 1, 100), win_rate_history)
        plt.xlabel('Episode')
        plt.ylabel('Win Rate')
        plt.title('MCTS Training Progress')
        plt.grid(True)
        plt.savefig('/ai_agent_2/mcts_training_progress.png')
        print(f"  Training plot saved to: /ai_agent_2/mcts_training_progress.png")
    
    return agent


def evaluate_agent(agent, num_games=100, opponent='random', num_simulations=1000):
    """
    Evaluate trained agent against a random opponent.
    
    Args:
        agent: MCTS agent
        num_games: Number of games to play
        opponent: Type of opponent ('random')
        num_simulations: Number of MCTS simulations per move
    """
    agent.clear_cache()  # Start fresh for evaluation
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
                action = agent.get_action(game, num_simulations=num_simulations)
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
        
        agent.clear_cache()  # Clear cache after each game
    
    return wins, losses, draws


def play_against_agent(model_file='mcts_tictactoe.pkl', num_simulations=1000):
    """
    Play a game against the trained agent.
    
    Args:
        model_file: Path to saved model file
        num_simulations: Number of MCTS simulations per move
    """
    print("\n" + "=" * 60)
    print("Playing against MCTS Agent")
    print("=" * 60)
    
    # Load agent
    try:
        with open(model_file, 'rb') as f:
            agent = pickle.load(f)
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
            action = agent.get_action(game, num_simulations=num_simulations)
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
        
        agent.clear_cache()  # Clear cache after each move


def main():
    """
    Main function to run MCTS training and evaluation.
    """
    # Train the agent
    agent = train_mcts(num_episodes=1000, num_simulations=1000, 
                      opponent_type='self', save_model=True)
    
    # Optionally play against the agent
    print("\n" + "=" * 60)
    response = input("Would you like to play against the agent? (y/n): ")
    if response.lower() == 'y':
        play_against_agent()


if __name__ == "__main__":
    main()

