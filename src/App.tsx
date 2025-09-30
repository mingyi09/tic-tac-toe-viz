import { useMemo, useState } from 'react'
import './App.css'

type Player = 'X' | 'O'

type BoardCell = Player | null

interface MoveRecord {
  moveNumber: number
  player: Player
  position: number
  moveVector: number[]
  boardAfter: BoardCell[]
}

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

function getMoveVector(board: BoardCell[]): number[] {
  return board.map((cell) => (cell === 'X' ? 1 : cell === 'O' ? -1 : 0))
}

function downloadFile(filename: string, contents: string, mime: string) {
  const blob = new Blob([contents], { type: mime })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function App() {
  const [board, setBoard] = useState<BoardCell[]>(Array(9).fill(null))
  const [nextPlayer, setNextPlayer] = useState<Player>('X')
  const [history, setHistory] = useState<MoveRecord[]>([])

  const winner = useMemo(() => calculateWinner(board), [board])
  const isDraw = useMemo(() => board.every((c) => c !== null) && !winner, [board, winner])

  function handleSquareClick(index: number) {
    if (board[index] || winner) return
    const newBoard = board.slice()
    newBoard[index] = nextPlayer
    const moveVector = getMoveVector(newBoard)
    const newMove: MoveRecord = {
      moveNumber: history.length + 1,
      player: nextPlayer,
      position: index,
      moveVector,
      boardAfter: newBoard,
    }
    setBoard(newBoard)
    setHistory((prev) => [...prev, newMove])
    setNextPlayer((p) => (p === 'X' ? 'O' : 'X'))
  }

  function resetGame() {
    setBoard(Array(9).fill(null))
    setNextPlayer('X')
    setHistory([])
  }

  function exportJSON() {
    const json = JSON.stringify(
      history.map((m) => ({
        moveNumber: m.moveNumber,
        player: m.player,
        position: m.position,
        moveVector: m.moveVector,
      })),
      null,
      2
    )
    downloadFile('tictactoe_moves.json', json, 'application/json')
  }

  function exportCSV() {
    const headers = [
      'moveNumber',
      'player',
      'position',
      ...Array.from({ length: 9 }, (_, i) => `v${i}`),
    ]
    const rows = history.map((m) => [
      m.moveNumber,
      m.player,
      m.position,
      ...m.moveVector,
    ])
    const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    downloadFile('tictactoe_moves.csv', csv, 'text/csv')
  }

  return (
    <div className="app">
      <h1>Tic-Tac-Toe (Human vs Human)</h1>
      <div className="top-bar">
        {!winner && !isDraw && (
          <div className="status">Next player: <strong>{nextPlayer}</strong></div>
        )}
        {winner && (
          <div className="status winner">Winner: <strong>{winner}</strong></div>
        )}
        {isDraw && <div className="status">It's a draw.</div>}
        <div className="actions">
          <button onClick={resetGame}>Reset</button>
          <button onClick={exportJSON} disabled={history.length === 0}>Export JSON</button>
          <button onClick={exportCSV} disabled={history.length === 0}>Export CSV</button>
        </div>
      </div>

      <div className="board" role="grid" aria-label="Tic tac toe board">
        {board.map((cell, idx) => (
          <button
            key={idx}
            className="square"
            role="gridcell"
            aria-label={`cell-${idx}`}
            onClick={() => handleSquareClick(idx)}
          >
            {cell}
          </button>
        ))}
      </div>

      <div className="history">
        <h2>Move History</h2>
        {history.length === 0 && <div className="empty">No moves yet.</div>}
        {history.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Move Number</th>
                <th>Player</th>
                <th>Position</th>
                <th>Board Representation (1=X, -1=O)</th>
              </tr>
            </thead>
            <tbody>
              {history.map((m) => (
                <tr key={m.moveNumber}>
                  <td>{m.moveNumber}</td>
                  <td>{m.player}</td>
                  <td>{m.position}</td>
                  <td>
                    [
                    {m.moveVector.map((v, i) => (
                      <span key={i} className="vec-item">{v}{i < 8 ? ', ' : ''}</span>
                    ))}
                    ]
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default App
