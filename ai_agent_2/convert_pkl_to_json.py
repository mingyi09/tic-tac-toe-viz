"""
Convert MCTS pickle file to JSON format.
Converts the MCTS root_cache to a JSON file with states, probabilities, and best actions.
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


def convert_mcts_to_json(pkl_file='mcts_tictactoe.pkl', output_file='mcts.json'):
    """
    Convert MCTS pickle file to JSON format.
    
    Args:
        pkl_file: Path to the pickle file
        output_file: Path to output JSON file
    """
    print(f"Loading MCTS agent from {pkl_file}...")
    
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
    
    # Debug: Check what's available
    has_state_probs = hasattr(agent, 'state_probabilities')
    state_probs_len = len(agent.state_probabilities) if has_state_probs else 0
    root_cache_len = len(agent.root_cache) if hasattr(agent, 'root_cache') else 0
    
    print(f"Debug info:")
    print(f"  Has state_probabilities: {has_state_probs}")
    print(f"  state_probabilities length: {state_probs_len}")
    print(f"  root_cache length: {root_cache_len}")
    
    # Check if state_probabilities exists (new format) or use root_cache (old format)
    use_precomputed = has_state_probs and state_probs_len > 0
    
    if use_precomputed:
        print(f"Using pre-computed probabilities from {state_probs_len} states...")
        source_data = agent.state_probabilities
    elif root_cache_len > 0:
        print(f"Computing probabilities from root_cache ({root_cache_len} states)...")
        # If state_probabilities doesn't exist or is empty, but root_cache has data,
        # we can try to compute probabilities on the fly
        if has_state_probs and hasattr(agent, 'compute_all_probabilities'):
            print("  Computing probabilities from root_cache (state_probabilities was empty)...")
            try:
                agent.compute_all_probabilities()
                if len(agent.state_probabilities) > 0:
                    print(f"  Successfully computed {len(agent.state_probabilities)} state probabilities!")
                    source_data = agent.state_probabilities
                    use_precomputed = True
                else:
                    print("  Warning: compute_all_probabilities returned empty, using root_cache directly...")
                    source_data = agent.root_cache
            except Exception as e:
                print(f"  Warning: Could not compute probabilities ({e}), using root_cache directly...")
                source_data = agent.root_cache
        else:
            source_data = agent.root_cache
    else:
        print("ERROR: Both state_probabilities and root_cache are empty!")
        print("The agent may not have been trained or the cache was cleared.")
        print("Please retrain the agent or ensure the pickle file contains trained data.")
        return
    
    # Convert to JSON format
    json_data = {"states": {}}
    
    print(f"Processing {len(source_data)} entries...")
    processed_count = 0
    
    for state_key, data in source_data.items():
        processed_count += 1
        if processed_count % 1000 == 0:
            print(f"  Processed {processed_count}/{len(source_data)} entries...")
        # Handle both formats: state_probabilities uses (state, player) as key
        # root_cache also uses (state, player) as key
        if isinstance(state_key, tuple) and len(state_key) == 2:
            state_tuple, player = state_key
        else:
            # Fallback: assume state_key is just the state tuple
            state_tuple = state_key
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
        
        if use_precomputed:
            # Use pre-computed probabilities from state_probabilities
            # data is a dict: {action: probability}
            action_probs = data
            best_action = None
            best_prob = -1.0
            
            for action, prob in action_probs.items():
                if action in valid_moves:
                    idx = action_to_index(action)
                    probs[idx] = prob
                    if prob > best_prob:
                        best_prob = prob
                        best_action = action
            
            # Find best action index
            if best_action is not None:
                best_idx = action_to_index(best_action)
            elif valid_moves:
                # If no probabilities found, use first valid move
                best_idx = action_to_index(valid_moves[0])
            else:
                best_idx = 0
        else:
            # Compute from root_cache (backward compatibility)
            root_node = data
            visits = [0] * 9
            total_visits = 0
            
            # Fill in visit counts for valid moves from children
            for action, child_node in root_node.children.items():
                if action in valid_moves:
                    idx = action_to_index(action)
                    visits[idx] = child_node.visits
                    total_visits += child_node.visits
            
            # Convert visit counts to probabilities
            valid_indices = [i for i in range(9) if visits[i] > 0]
            
            if valid_indices and total_visits > 0:
                # Normalize visits to probabilities
                for idx in valid_indices:
                    probs[idx] = visits[idx] / total_visits
                
                # Find best action (most visits)
                best_idx = valid_indices[np.argmax([visits[i] for i in valid_indices])]
            else:
                # No visits recorded, set uniform probabilities for valid moves
                if valid_moves:
                    uniform_prob = 1.0 / len(valid_moves)
                    for move in valid_moves:
                        idx = action_to_index(move)
                        probs[idx] = uniform_prob
                    # Best is first valid move
                    best_idx = action_to_index(valid_moves[0])
                else:
                    # Terminal state, no valid moves
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
    pkl_file = sys.argv[1] if len(sys.argv) > 1 else 'mcts_tictactoe.pkl'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'mcts.json'
    
    convert_mcts_to_json(pkl_file, output_file)
