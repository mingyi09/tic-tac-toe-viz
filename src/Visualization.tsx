import { useMemo, useState } from 'react'
import './App.css'
import newGamesRaw from '../new_games.json?raw'

type Player = 'X' | 'O'
type BoardCell = Player | null

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

function calculateWinner(board: BoardCell[]): Player | null {
  for (const [a, b, c] of WIN_LINES) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return board[a]
    }
  }
  return null
}

export default function Visualization() {
  const [board, setBoard] = useState<BoardCell[]>(Array(9).fill(null))
  const [nextPlayer, setNextPlayer] = useState<Player>('X')
  const winner = useMemo(() => calculateWinner(board), [board])
  const isDraw = useMemo(() => board.every((c) => c !== null) && !winner, [board, winner])
  const [showAI1, setShowAI1] = useState<boolean>(false)
  const [showAI2, setShowAI2] = useState<boolean>(false)
  const [showHuman, setShowHuman] = useState<boolean>(true)

  // Load games and moves; build state->move counts using only IDs present in new_games.json.games
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

  function boardToKey(b: BoardCell[]): string {
    return b.map((c) => (c === 'X' ? 'X' : c === 'O' ? 'O' : '.')).join('')
  }

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
        {isDraw && <div className="status">It's a draw.</div>}
        <div className="actions">
          <button onClick={reset}>Reset</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <div>
          <h2 style={{ marginBottom: 8 }}>Left: Interactive</h2>
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
          <h2 style={{ marginBottom: 8 }}>Right: Synced</h2>
          <div className="board" role="grid" aria-label="Synced board">
            {board.map((cell, idx) => {
              const isSuggestion = suggestedMove === idx && !cell && !winner && !isDraw && showHuman
              const display = cell || (isSuggestion ? nextPlayer : null)
              return (
                <button
                  key={`R-${idx}`}
                  className="square"
                  role="gridcell"
                  aria-label={`right-cell-${idx}`}
                  disabled
                  style={isSuggestion ? { borderStyle: 'dashed', borderColor: '#e74c3c' } : undefined}
                >
                  {display && (
                    <span style={isSuggestion ? { opacity: 0.6, color: '#e74c3c' } : undefined}>
                      {display}
                    </span>
                  )}
                </button>
              )
            })}
          </div>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#3498db' }}>
              <input
                type="checkbox"
                checked={showAI1}
                onChange={(e) => setShowAI1(e.target.checked)}
                style={{ accentColor: '#3498db' }}
              />
              AI-1
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#2ecc71' }}>
              <input
                type="checkbox"
                checked={showAI2}
                onChange={(e) => setShowAI2(e.target.checked)}
                style={{ accentColor: '#2ecc71' }}
              />
              AI-2
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#e74c3c' }}>
              <input
                type="checkbox"
                checked={showHuman}
                onChange={(e) => setShowHuman(e.target.checked)}
                style={{ accentColor: '#e74c3c' }}
              />
              Human
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}


