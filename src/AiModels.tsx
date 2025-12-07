import './App.css'

export default function AiModels() {
  return (
    <div className="app">
      <h1>AI Models</h1>
      <div className="setup" style={{ maxWidth: 720 }}>
        <h2>Overview</h2>
        <p>
          This page summarizes the AI models used in the visualization tab. Each model provides
          a distribution over next moves for any given tic-tac-toe board state.
        </p>

        <div className="field">
          <h3>AI-1: Q-Learning Agent</h3>
          <p>
            AI-1 is a Q-learning agent ...
          </p>
        </div>

        <div className="field">
          <h3>AI-2: Value-Iteration Agent</h3>
          <p>
            AI-2 is a dynamic-programming based value-iteration agent...
          </p>
        </div>

        <div className="field">
          <h3>Human Strategy</h3>
          <p>
            The human strategy uses aggregated move frequencies from collected human games. For a
            given board position, the orange suggestion indicates the most frequent human move based on the collected human dataset.
          </p>
        </div>

        <p style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#777' }}>
          To <strong>see these models in action</strong>, switch to the Visualization tab and interact
          with the game board and AI toggles.
        </p>
      </div>
    </div>
  )
}


