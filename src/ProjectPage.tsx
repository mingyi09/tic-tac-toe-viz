import './App.css'

export default function ProjectPage() {
  return (
    <div className="app">
      <h1>Project Page</h1>

      <div className="setup" style={{ maxWidth: 800 }}>
        <h2>Motivation</h2>
        <p>
          {/* TODO: Briefly describe the service learning partner, the context of the collaboration, and
              the motivating questions that led to this visualization project. */}
        </p>

        <h2>Data</h2>
        <p>
          {/* TODO: Summarize the datasets used (e.g., game logs, Q-tables, value-iteration tables),
              including data types, key fields, and any important preprocessing steps. */}
        </p>

        <h2>Task Analysis</h2>
        <p>
          {/* TODO: Summarize interview findings and the task table, focusing on users, goals, and
              concrete tasks the visualization supports. */}
        </p>

        <h2>Design Process</h2>
        <p>
          {/* TODO: Describe early sketches, iterations, and key design choices (layout, color, encoding)
              that led to the final visualization. Optionally link or embed sketches here. */}
        </p>

        <h2>Final Visualization</h2>
        <p>
          {/* TODO: Describe the final visualization, design justifications, libraries/packages used
              (e.g., React, Plotly), and provide a short UI walk-through. */}
        </p>

        <h2>Data Analysis</h2>
        <p>
          {/* TODO: Summarize the most interesting findings from analyzing human and AI moves, including
              any comparisons between strategies. */}
        </p>

        <h2>Conclusion</h2>
        <p>
          {/* TODO: Provide a short summary of the work completed, its impact, and areas for improvement
              or future work (e.g., additional models, richer datasets, or new interaction designs). */}
        </p>

        {/* Optional extra sections for more detail can be added below */}
      </div>
    </div>
  )
}


