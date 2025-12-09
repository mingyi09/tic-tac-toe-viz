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
          We trained an agent using the popular reinforcement learning
algorithm Q-learning. Q-learning is a model-free method, which makes it
especially useful for scaling to games more complex than Tic-Tac-Toe. For our
experiments, we set the learning rate to 0.1 and trained the agent for 10,000
episodes to ensure it had sufficient experience to learn effective strategies.
          </p>
        </div>

        <div className="field">
          <h3>AI-2: Value-Iteration Agent</h3>
          <p>
          We also trained an agent using a dynamic-programming–based
reinforcement learning method called Value Iteration. This approach is
simple and interpretable, making it easy to understand how the agent evaluates
states and updates its decisions. However, because Value Iteration requires
sweeping over the entire state space, it does not scale well to larger or more
complex games. In our setup, we used a convergence threshold of 1e-6 and
allowed up to 1,000 iterations to ensure the algorithm reached a stable solution
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


