import { useEffect, useMemo, useState } from 'react'
import './App.css'
import newGamesRaw from '../new_games.json?raw' // this is our games (human data)
//import ai1Raw from '../q_table_all.json?raw' // old local file
import ai1Raw from '../ai_agent_1/q_table.json?raw' // new import from ai_agent_1 folder
import ai2Raw from '../ai_agent_2/value_iteration_table.json?raw' // AI-2 value-iteration table

type Player = 'X' | 'O'
type BoardCell = Player | null

// if three cells in a row, column, or diagonal are the same -> winner
const WIN_LINES: number[][] = [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8],
  [2, 4, 6],
]

// if winning line is found, return the winner
function calculateWinner(board: BoardCell[]): Player | null {
  for (const [a, b, c] of WIN_LINES) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return board[a]
    }
  }
  return null
}

// the main component that renders the visualization
export default function Visualization() {
  const [board, setBoard] = useState<BoardCell[]>(Array(9).fill(null))
  const [nextPlayer, setNextPlayer] = useState<Player>('X')
  const winner = useMemo(() => calculateWinner(board), [board])
  const isDraw = useMemo(() => board.every((c) => c !== null) && !winner, [board, winner])
  // states that store checkboxes for showing AI1, AI2, and human player strategies
  // default will show everything
  const [showAI1, setShowAI1] = useState<boolean>(true)
  const [showAI2, setShowAI2] = useState<boolean>(true)
  const [showHuman, setShowHuman] = useState<boolean>(true)

  type GameSummary = {
    id: string
  }
  type MoveJson = {
    id: string
    game_id: string
    S_str: string
    move: number
    move_index: number
    player: 1 | -1
  }
  type GamesFile = { games: GameSummary[]; moves: MoveJson[] }

  const { statePlayerToMoveCounts } = useMemo(() => {
    let parsedNew: GamesFile = { games: [], moves: [] }
    try {
      parsedNew = JSON.parse(newGamesRaw) as GamesFile
    } catch {
      // fall back to empty dataset if parsing fails
      parsedNew = { games: [], moves: [] }
    }

    // Valid IDs are those present in new_games.json's games array
    // (some human games data is filtered out, because of testing/AI moves)
    const validIds = new Set<string>((parsedNew.games || []).map(g => g.id))

    const statePlayerToMoveCounts = new Map<string, Map<number, number>>()
    for (const m of parsedNew.moves || []) {
      if (!validIds.has(m.game_id)) continue
      const key = `${m.S_str}|${m.player}`
      let inner = statePlayerToMoveCounts.get(key)
      if (!inner) {
        inner = new Map<number, number>()
        statePlayerToMoveCounts.set(key, inner)
      }
      inner.set(m.move, (inner.get(m.move) || 0) + 1)
    }
    return { statePlayerToMoveCounts }
  }, [])

  // this is a helper function that converts the board to a string
  // X: 'X', O: 'O', empty cell: '.' -> a board string
  function boardToKey(b: BoardCell[]): string {
    return b.map((c) => (c === 'X' ? 'X' : c === 'O' ? 'O' : '.')).join('')
  }

  // Parse AI-1 Q-table once and build lookup by `${S_str}|player`
  type QState = { player: 1 | -1; probs: number[]; best?: number }
  const ai1ByStateAndPlayer = useMemo(() => {
    const map = new Map<string, QState>()
    try {
      const parsed = JSON.parse(ai1Raw) as { states: Record<string, QState> }
      const entries = parsed?.states ? Object.entries(parsed.states) : []
      for (const [s, v] of entries) {
        if (!v || !Array.isArray(v.probs)) continue
        const p = (v.player === 1 ? 1 : -1) as 1 | -1
        map.set(`${s}|${p}`, { player: p, probs: v.probs, best: v.best })
      }
    } catch {
      // ignore parse errors; leave empty
      console.log('Error parsing the Q-table')
    }
    return map
  }, [])

  // Parse AI-2 table once and build lookup
  const ai2ByStateAndPlayer = useMemo(() => {
    const map = new Map<string, QState>()
    try {
      const parsed = JSON.parse(ai2Raw) as { states: Record<string, QState> }
      const entries = parsed?.states ? Object.entries(parsed.states) : []
      for (const [s, v] of entries) {
        if (!v || !Array.isArray(v.probs)) continue
        const p = (v.player === 1 ? 1 : -1) as 1 | -1
        map.set(`${s}|${p}`, { player: p, probs: v.probs, best: v.best })
      }
    } catch {
      console.log('Error parsing AI-2 table')
    }
    return map
  }, [])

  const ai1SuggestedMove = useMemo(() => {
    if (!showAI1) return { move: null as number | null, hasData: false }
    if (winner || isDraw) return { move: null as number | null, hasData: false }
    const key = boardToKey(board)
    const playerNum = nextPlayer === 'X' ? 1 : -1
    const entry = ai1ByStateAndPlayer.get(`${key}|${playerNum}`)
    if (!entry) return { move: null as number | null, hasData: false }

    const legalIndices: number[] = []
    for (let i = 0; i < 9; i++) {
      if (!board[i]) {
        legalIndices.push(i);
      }
    }
    if (legalIndices.length === 0) return { move: null as number | null, hasData: true }
    let candidate: number | null = null
    if (typeof entry.best === 'number' && legalIndices.includes(entry.best)) {
      candidate = entry.best
    } else {
      let bestIdx: number | null = null
      let bestVal = -Infinity
      for (const i of legalIndices) {
        const v = entry.probs[i] ?? -Infinity
        if (v > bestVal) {
          bestVal = v
          bestIdx = i
        }
      }
      candidate = bestIdx
    }
    return { move: candidate, hasData: true }
  }, [ai1ByStateAndPlayer, board, nextPlayer, winner, isDraw, showAI1])

  const ai2SuggestedMove = useMemo(() => {
    if (!showAI2) return { move: null as number | null, hasData: false }
    if (winner || isDraw) return { move: null as number | null, hasData: false }
    const key = boardToKey(board)
    const playerNum = nextPlayer === 'X' ? 1 : -1
    const entry = ai2ByStateAndPlayer.get(`${key}|${playerNum}`)
    if (!entry) return { move: null as number | null, hasData: false }
    const legalIndices: number[] = []
    for (let i = 0; i < 9; i++) if (!board[i]) legalIndices.push(i)
    if (legalIndices.length === 0) return { move: null as number | null, hasData: true }
    let candidate: number | null = null
    if (typeof entry.best === 'number' && legalIndices.includes(entry.best)) {
      candidate = entry.best
    } else {
      let bestIdx: number | null = null
      let bestVal = -Infinity
      for (const i of legalIndices) {
        const v = entry.probs[i] ?? -Infinity
        if (v > bestVal) {
          bestVal = v
          bestIdx = i
        }
      }
      candidate = bestIdx
    }
    return { move: candidate, hasData: true }
  }, [ai2ByStateAndPlayer, board, nextPlayer, winner, isDraw, showAI2])

  // Entry for current state to drive heatmap (if present)
  const ai1EntryForState = useMemo(() => {
    const key = boardToKey(board)
    const playerNum = nextPlayer === 'X' ? 1 : -1
    return ai1ByStateAndPlayer.get(`${key}|${playerNum}`) || null
  }, [ai1ByStateAndPlayer, board, nextPlayer])

  const [ai1HeatmapOpen, setAi1HeatmapOpen] = useState<boolean>(false)

  function probsToMatrix3x3(arr: number[] | undefined) {
    const a = Array.isArray(arr) && arr.length === 9 ? arr : Array(9).fill(0)
    return [a.slice(0, 3), a.slice(3, 6), a.slice(6, 9)]
  }

  useEffect(() => {
    if (!ai1HeatmapOpen) return
    const entry = ai1EntryForState
    const z = probsToMatrix3x3(entry?.probs)
    // Build customdata carrying canonical row/col labels (row 0 at top, col 0 at left)
    const customdata = [
      [ [0,0], [0,1], [0,2] ],
      [ [1,0], [1,1], [1,2] ],
      [ [2,0], [2,1], [2,2] ],
    ]
    const probs = Array.isArray(entry?.probs) ? (entry!.probs as number[]) : []
    const maxVal = Math.max(0, ...(probs.length === 9 ? probs : [0]))
    const el = document.getElementById('ai1-heatmap')
    const P = (window as unknown as { Plotly?: { react: (el: HTMLElement, data: unknown, layout?: unknown, config?: unknown) => void } }).Plotly
    if (el && P) {
      // Custom colorscale: edit the heatmap colors here
      const colorscale: Array<[number, string]> = [
        [0.0, '#bdbdbd'],   // grey for zero/lowest
        [0.00001, '#edf5ff'],
        [0.2, '#d0e2ff'],
        [0.5, '#a6c8ff'],
        [0.8, '#78a9ff'],
        [1.0, '#0043ce']    // darkest blue for highest
      ]
      // using plotly to render heatmap: https://plotly.com/javascript/heatmaps/
      const data = [{
        type: 'heatmap',
        z,
        x: [0, 1, 2],
        y: [0, 1, 2],
        customdata,
        colorscale,
        reversescale: false,
        // xgap / ygap create visible grid lines between cells
        xgap: 2,
        ygap: 2,
        showscale: true,
        colorbar: { title: { text: 'Probability' } },
        zmin: 0,
        zmax: maxVal > 0 ? maxVal : 1,
        // Use canonical row/col from customdata so top row is row 0 regardless of axis direction
        hovertemplate: 'row %{customdata[0]}, col %{customdata[1]}<br>p=%{z:.2f}<extra></extra>',
      }]
      const layout = {
        width: 400,
        height: 300, 
        margin: { l: 20, r: 20, t: 20, b: 20 },
        // Reverse y so the first row in z is rendered at the top (row 0)
        yaxis: { autorange: 'reversed' as const, visible: false },
        xaxis: { visible: false },
      }
      P.react(el, data as unknown, layout as unknown, { displayModeBar: false } as unknown)
    }
  }, [ai1HeatmapOpen, ai1EntryForState])

  // AI-2 heatmap state and effect
  const ai2EntryForState = useMemo(() => {
    const key = boardToKey(board)
    const playerNum = nextPlayer === 'X' ? 1 : -1
    return ai2ByStateAndPlayer.get(`${key}|${playerNum}`) || null
  }, [ai2ByStateAndPlayer, board, nextPlayer])

  const [ai2HeatmapOpen, setAi2HeatmapOpen] = useState<boolean>(false)

  useEffect(() => {
    if (!ai2HeatmapOpen) return
    const entry = ai2EntryForState
    const z = probsToMatrix3x3(entry?.probs)
    const customdata = [
      [ [0,0], [0,1], [0,2] ],
      [ [1,0], [1,1], [1,2] ],
      [ [2,0], [2,1], [2,2] ],
    ]
    const probs = Array.isArray(entry?.probs) ? (entry!.probs as number[]) : []
    const maxVal = Math.max(0, ...(probs.length === 9 ? probs : [0]))
    const el = document.getElementById('ai2-heatmap')
    const P = (window as unknown as { Plotly?: { react: (el: HTMLElement, data: unknown, layout?: unknown, config?: unknown) => void } }).Plotly
    if (el && P) {
      // Light green for low probability, darkest green for highest
      const colorscale: Array<[number, string]> = [
        [0.0, '#bdbdbd'],   // grey for zero
        [0.00001, '#e8f5e9'],
        [0.25, '#c8e6c9'],
        [0.5, '#81c784'],
        [0.75, '#43a047'],
        [1.0, '#1b5e20'],   // darkest green for max
      ]
      const data = [{
        type: 'heatmap',
        z,
        x: [0, 1, 2],
        y: [0, 1, 2],
        customdata,
        colorscale,
        reversescale: false,
        xgap: 2,
        ygap: 2,
        showscale: true,
        colorbar: { title: { text: 'Probability' } },
        zmin: 0,
        zmax: maxVal > 0 ? maxVal : 1,
        hovertemplate: 'row %{customdata[0]}, col %{customdata[1]}<br>p=%{z:.2f}<extra></extra>',
      }]
      const layout = {
        width: 400,
        height: 300,
        margin: { l: 20, r: 20, t: 20, b: 20 },
        yaxis: { autorange: 'reversed' as const, visible: false },
        xaxis: { visible: false },
      }
      P.react(el, data as unknown, layout as unknown, { displayModeBar: false } as unknown)
    }
  }, [ai2HeatmapOpen, ai2EntryForState])
  
  const suggestedMove = useMemo(() => {
    if (winner || isDraw) return null
    const key = boardToKey(board)
    const playerNum = nextPlayer === 'X' ? 1 : -1
    const counts = statePlayerToMoveCounts.get(`${key}|${playerNum}`)
    if (!counts) return null
    let bestMove: number | null = null
    let bestCount = -Infinity
    for (const [mv, cnt] of counts.entries()) {
      if (board[mv]) continue
      if (cnt > bestCount) {
        bestCount = cnt
        bestMove = mv
      }
    }
    return bestMove
  }, [board, nextPlayer, winner, isDraw, statePlayerToMoveCounts])

  function onLeftClick(index: number) {
    if (board[index] || winner) return
    const updated = board.slice()
    updated[index] = nextPlayer
    setBoard(updated)
    setNextPlayer((p) => (p === 'X' ? 'O' : 'X'))
  }

  function reset() {
    setBoard(Array(9).fill(null))
    setNextPlayer('X')
  }

  return (
    <div className="app">
      <h1>Tic-Tac-Toe Visualization</h1>
      <div className="top-bar">
        {!winner && !isDraw && (
          <div className="status">Next player: <strong>{nextPlayer}</strong></div>
        )}
        {winner && <div className="status winner">Winner: <strong>{winner}</strong></div>}
        {isDraw && <div className="status">This is a draw.</div>}
        <div className="actions">
          <button onClick={reset}>Reset</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start', flexWrap: 'nowrap' }}>
        <div>
          <h2 style={{ marginBottom: 8 }}>Game Board</h2>
          <div className="board" role="grid" aria-label="Interactive board">
            {board.map((cell, idx) => (
              <button
                key={`L-${idx}`}
                className="square"
                role="gridcell"
                aria-label={`left-cell-${idx}`}
                onClick={() => onLeftClick(idx)}
                disabled={!!cell || !!winner}
              >
                {cell}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h2 style={{ marginBottom: 8 }}>Recommendation Visualization</h2>
          <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>
            <div className="board" role="grid" aria-label="Synced board">
              {board.map((cell, idx) => {
                const isHumanSuggestion = suggestedMove === idx && !cell && !winner && !isDraw && showHuman
                const isAI1Suggestion = ai1SuggestedMove.move === idx && !cell && !winner && !isDraw && showAI1
                const isAI2Suggestion = ai2SuggestedMove.move === idx && !cell && !winner && !isDraw && showAI2
                const display = cell || (isHumanSuggestion || isAI1Suggestion || isAI2Suggestion ? nextPlayer : null)
                // Prefer a single dashed border (no solid), then add inset rings for overlaps
                let style: React.CSSProperties | undefined
                if (isHumanSuggestion || isAI1Suggestion || isAI2Suggestion) {
                  style = { borderStyle: 'dashed', borderWidth: 2, outline: 'none' }
                  if (isHumanSuggestion) style.borderColor = '#e74c3c'
                  else if (isAI1Suggestion) style.borderColor = '#3498db'
                  else if (isAI2Suggestion) style.borderColor = '#2ecc71'
                  // Add inner rings only when there is overlap
                  if (isAI1Suggestion && isHumanSuggestion) {
                    style = { ...(style || {}), boxShadow: 'inset 0 0 0 2px #3498db' }
                  }
                  if (isAI2Suggestion && (isHumanSuggestion || isAI1Suggestion)) {
                    const existing = style && style.boxShadow ? `${style.boxShadow}, ` : ''
                    style = { ...(style || {}), boxShadow: `${existing}inset 0 0 0 2px #2ecc71` }
                  }
                }
                // Cursor: pointer only on clickable AI suggestion cells
                style = {
                  ...(style || {}),
                  cursor: (isAI1Suggestion || isAI2Suggestion) ? 'pointer' : 'default',
                }
                return (
                  <button
                    key={`R-${idx}`}
                    className="square"
                    role="gridcell"
                    aria-label={`right-cell-${idx}`}
                    disabled={!(isAI1Suggestion || isAI2Suggestion)}
                    onClick={
                      (isAI1Suggestion || isAI2Suggestion)
                        ? () => {
                            if (isAI1Suggestion && !isAI2Suggestion) {
                              setAi1HeatmapOpen(true)
                              setAi2HeatmapOpen(false)
                            } else if (isAI2Suggestion && !isAI1Suggestion) {
                              setAi2HeatmapOpen(true)
                              setAi1HeatmapOpen(false)
                            } else {
                              // if both suggest same cell, show both
                              setAi1HeatmapOpen(true)
                              setAi2HeatmapOpen(true)
                            }
                          }
                        : undefined
                    }
                    style={style}
                  >
                    {display && (
                      isHumanSuggestion ? (
                        <span style={{ opacity: 0.6, color: '#e74c3c' }}>{display}</span>
                      ) : isAI1Suggestion && !isAI2Suggestion ? (
                        <span style={{ opacity: 0.6, color: '#3498db' }}>{display}</span>
                      ) : isAI2Suggestion && !isAI1Suggestion ? (
                        <span style={{ opacity: 0.6, color: '#2ecc71' }}>{display}</span>
                      ) : (
                        <span>{display}</span>
                      )
                    )}
                  </button>
                )
              })}
            </div>
            {showAI1 && ai1HeatmapOpen && ai1EntryForState && (
              <div className="setup" style={{ marginTop: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ margin: 0 }}>AI-1 Probability Heatmap</h3>
                  <button onClick={() => setAi1HeatmapOpen(false)}>Close</button>
                </div>
                <div id="ai1-heatmap" aria-label="AI-1 heatmap" />
              </div>
            )}
            {showAI2 && ai2HeatmapOpen && ai2EntryForState && (
              <div className="setup" style={{ marginTop: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ margin: 0 }}>AI-2 Probability Heatmap</h3>
                  <button onClick={() => setAi2HeatmapOpen(false)}>Close</button>
                </div>
                <div id="ai2-heatmap" aria-label="AI-2 heatmap" />
              </div>
            )}
          </div>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#3498db', fontSize: '1.2rem' }}>
              <input
                type="checkbox"
                checked={showAI1}
                onChange={(e) => setShowAI1(e.target.checked)}
                style={{ accentColor: '#3498db', transform: 'scale(1.25)', transformOrigin: 'left center' }}
              />
              AI-1
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#2ecc71', fontSize: '1.2rem' }}>
              <input
                type="checkbox"
                checked={showAI2}
                onChange={(e) => setShowAI2(e.target.checked)}
                style={{ accentColor: '#2ecc71', transform: 'scale(1.25)', transformOrigin: 'left center' }}
              />
              AI-2
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#e74c3c', fontSize: '1.2rem' }}>
              <input
                type="checkbox"
                checked={showHuman}
                onChange={(e) => setShowHuman(e.target.checked)}
                style={{ accentColor: '#e74c3c', transform: 'scale(1.25)', transformOrigin: 'left center' }}
              />
              Human
            </label>
          </div>
          <div style={{ textAlign: 'center', marginTop: 6, color: '#777', fontSize: '0.9rem' }}>
            Click the AI move to view probability heatmap
          </div>
          {showAI1 && !ai1SuggestedMove.hasData && !winner && !isDraw && (
            <div style={{ textAlign: 'center', marginTop: 8, color: '#888' }}>
              No AI-1 data for this state and player now. Check back later.
            </div>
          )}
          {showAI2 && !ai2SuggestedMove.hasData && !winner && !isDraw && (
            <div style={{ textAlign: 'center', marginTop: 8, color: '#888' }}>
              No AI-2 data for this state and player now. Check back later.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


