"""
Convert Value Iteration pickle file to JSON format.
Converts the Q-table to a JSON file with states, probabilities, and best actions.
"""

import json
import numpy as np
import dill as pickle


def state_to_string(state):
    """
    Convert state tuple to string format.
    State is a tuple of tuples like ((0,0,0), (0,1,2), (0,0,0))
    Returns string like "X..O...X"
    """
    symbol_map = {0: '.', 1: 'X', 2: 'O'}
    result = []
    for row in state:
        for cell in row:
            result.append(symbol_map[cell])
    return ''.join(result)


def get_current_player(state_string):
    """
    Determine which player's turn it is based on the board state.
    Count X (player 1) and O (player 2). If equal, it's player 1's turn.
    """
    count_x = state_string.count('X')
    count_o = state_string.count('O')
    
    if count_x == count_o:
        return 1  # Player 1's turn
    else:
        return -1  # Player 2's turn


def action_to_index(action):
    """
    Convert (row, col) action to linear index (0-8).
    """
    if action is None:
        return None
    row, col = action
    return row * 3 + col


def index_to_action(idx):
    """
    Convert linear index (0-8) to (row, col) action.
    """
    row = idx // 3
    col = idx % 3
    return (row, col)


def get_valid_moves_from_state(state):
    """
    Get list of valid move positions from state tuple.
    """
    valid_moves = []
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                valid_moves.append((i, j))
    return valid_moves


def convert_value_iteration_to_json(pkl_file='value_iteration_tictactoe.pkl', output_file='value_iteration_table.json'):
    """
    Convert Value Iteration pickle file to JSON format.
    
    Args:
        pkl_file: Path to the pickle file
        output_file: Path to output JSON file
    """
    print(f"Loading Value Iteration agent from {pkl_file}...")
    
    # Load the agent
    try:
        with open(pkl_file, 'rb') as f:
            agent = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: File {pkl_file} not found!")
        return
    except Exception as e:
        print(f"Error loading pickle file: {e}")
        return
    
    print(f"Q-table loaded. Processing {len(agent.q_table)} state-player pairs...")
    
    # Convert Q-table to JSON format
    json_data = {"states": {}}
    
    for state_key, actions_dict in agent.q_table.items():
        # Handle Q-table structure: key is (state, player) tuple
        # Check if state_key is a tuple of (state_tuple, player)
        if isinstance(state_key, tuple) and len(state_key) == 2:
            first_elem, second_elem = state_key
            # Check if first element is a tuple (the state) and second is an int (the player)
            if isinstance(first_elem, tuple) and isinstance(second_elem, int):
                # Format: (state_tuple, player)
                state_tuple, player = state_key
            else:
                # Fallback: assume state_key is just the state tuple
                state_tuple = state_key
                # Try to determine player from state
                state_string_temp = state_to_string(state_tuple)
                player = get_current_player(state_string_temp)
                if player == -1:
                    player = 2  # Convert -1 to 2 for O
        else:
            # Fallback: assume state_key is just the state tuple
            state_tuple = state_key
            # Try to determine player from state
            state_string_temp = state_to_string(state_tuple)
            player = get_current_player(state_string_temp)
            if player == -1:
                player = 2  # Convert -1 to 2 for O
        
        # Convert state tuple to string
        state_string = state_to_string(state_tuple)
        
        # Get valid moves for this state
        valid_moves = get_valid_moves_from_state(state_tuple)
        
        # Initialize probability array for all 9 positions
        probs = [0.0] * 9
        q_values = [float('-inf')] * 9
        
        # Fill in Q-values for valid moves
        for action, q_value in actions_dict.items():
            if action in valid_moves:
                idx = action_to_index(action)
                q_values[idx] = q_value
        
        # Convert Q-values to probabilities using softmax
        # Only consider valid moves (non-negative infinity values)
        valid_indices = [i for i in range(9) if q_values[i] != float('-inf')]
        
        # Check if this is a terminal state (no valid moves or all positions filled)
        is_terminal = len(valid_moves) == 0
        
        if valid_indices:
            # Extract Q-values for valid moves
            valid_q_values = [q_values[i] for i in valid_indices]
            
            # Apply softmax to valid Q-values
            # Softmax: exp(x_i) / sum(exp(x_j))
            exp_q = np.exp(valid_q_values - np.max(valid_q_values))  # Subtract max for numerical stability
            valid_probs = exp_q / np.sum(exp_q)
            
            # Fill in probabilities
            for idx, prob in zip(valid_indices, valid_probs):
                probs[idx] = float(prob)
            
            # Find best action (argmax)
            best_idx = valid_indices[np.argmax(valid_q_values)]
        else:
            # No valid moves or Q-values
            if valid_moves:
                # Has valid moves but no Q-values (shouldn't happen, but handle it)
                uniform_prob = 1.0 / len(valid_moves)
                for move in valid_moves:
                    idx = action_to_index(move)
                    probs[idx] = uniform_prob
                # Best is first valid move
                best_idx = action_to_index(valid_moves[0])
            else:
                # Terminal state, no valid moves - all probabilities are 0, best is 0
                best_idx = 0
        
        # Convert player to format expected by JSON (1 for X, -1 for O)
        json_player = 1 if player == 1 else -1
        
        # Round probabilities to 2 decimal places
        probs = [round(p, 2) for p in probs]
        
        # Add to JSON data
        # Note: If the same state appears for both players, the last one will be kept
        # This is fine since for a given board state, only one player should be to move
        json_data["states"][state_string] = {
            "player": json_player,
            "probs": probs,
            "best": best_idx
        }
    
    # Save to JSON file
    print(f"Saving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"Conversion complete! {len(json_data['states'])} states converted.")
    print(f"Output saved to: {output_file}")
    
    return json_data


if __name__ == "__main__":
    import sys
    
    # Allow command line arguments
    pkl_file = sys.argv[1] if len(sys.argv) > 1 else 'value_iteration_tictactoe.pkl'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'value_iteration_table.json'
    
    convert_value_iteration_to_json(pkl_file, output_file)

