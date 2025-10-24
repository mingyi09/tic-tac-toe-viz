import { useEffect, useMemo, useState } from 'react'
import './App.css'
import { db } from './firebase'
import { doc, setDoc, writeBatch } from 'firebase/firestore'

type Player = 'X' | 'O'

type ExperienceLevel = 'novice' | 'intermediate' | 'expert'
type BackendLevel = 'beginner' | 'intermediate' | 'expert' | 'unknown'
type BackendOutcome = '1' | '-1' | '0' | 'unknown'

type BoardCell = Player | null

interface MoveRecord {
  moveNumber: number
  player: Player
  position: number
  moveVector: number[]
  boardAfter: BoardCell[]
  stateBefore: number[]
  outcome: '1 wins' | '-1 wins' | 'Draw' | 'Ongoing'
}

interface MoveUploadRecord {
  game_id: string
  player: 1 | -1
  move_index: number
  move: number
  S: number[]
  S_json: string
  S_prime: number[]
  S_prime_json: string
  outcome: '1' | '-1' | '0' | 'unknown'
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

function generateGameId(): string {
  const ts = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14)
  const rand = Math.random().toString(36).slice(2, 8)
  return `g_${ts}_${rand}`
}

function App() {
  const [board, setBoard] = useState<BoardCell[]>(Array(9).fill(null))
  const [nextPlayer, setNextPlayer] = useState<Player>('X')
  const [history, setHistory] = useState<MoveRecord[]>([])
  const [started, setStarted] = useState<boolean>(false)
  const [gameId, setGameId] = useState<string>(generateGameId())
  const [player1Exp, setPlayer1Exp] = useState<ExperienceLevel | ''>('')
  const [player2Exp, setPlayer2Exp] = useState<ExperienceLevel | ''>('')
  const [startedAt, setStartedAt] = useState<string | null>(null)
  const [endedAt, setEndedAt] = useState<string | null>(null)
  const [savedGameDoc, setSavedGameDoc] = useState<boolean>(false)
  const [showUploadPreview, setShowUploadPreview] = useState<boolean>(false)
  const [uploadSubmitting, setUploadSubmitting] = useState<boolean>(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  // track success implicitly via savedGameDoc

  const winner = useMemo(() => calculateWinner(board), [board])
  const isDraw = useMemo(() => board.every((c) => c !== null) && !winner, [board, winner])

  const movesForUpload = useMemo<MoveUploadRecord[]>(() => {
    const finalOutcome: BackendOutcome = winner === 'X' ? '1' : winner === 'O' ? '-1' : (isDraw ? '0' : 'unknown')
    return history.map((m) => {
      const playerNum: 1 | -1 = m.player === 'X' ? 1 : -1
      const S = m.stateBefore
      const SPrime = m.moveVector
      return {
        game_id: gameId,
        player: playerNum,
        move_index: m.moveNumber,
        move: m.position,
        S,
        S_json: JSON.stringify(S),
        S_prime: SPrime,
        S_prime_json: JSON.stringify(SPrime),
        outcome: finalOutcome === 'unknown' ? 'unknown' : finalOutcome,
      }
    })
  }, [history, gameId, winner, isDraw])

  function handleSquareClick(index: number) {
    if (!started || board[index] || winner) return
    const stateBefore = getMoveVector(board)
    const newBoard = board.slice()
    newBoard[index] = nextPlayer
    const moveVector = getMoveVector(newBoard)
    const winnerAfter = calculateWinner(newBoard)
    const outcome: '1 wins' | '-1 wins' | 'Draw' | 'Ongoing' =
      winnerAfter ? (winnerAfter === 'X' ? '1 wins' : '-1 wins') :
      (newBoard.every((c) => c !== null) ? 'Draw' : 'Ongoing')
    const newMove: MoveRecord = {
      moveNumber: history.length + 1,
      player: nextPlayer,
      position: index,
      moveVector,
      boardAfter: newBoard,
      stateBefore,
      outcome,
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

  function startGame() {
    setStarted(true)
    setStartedAt(new Date().toISOString())
  }

  function newGame() {
    setBoard(Array(9).fill(null))
    setNextPlayer('X')
    setHistory([])
    setStarted(false)
    setStartedAt(null)
    setEndedAt(null)
    setSavedGameDoc(false)
    setPlayer1Exp('')
    setPlayer2Exp('')
    setGameId(generateGameId())
  }

  function mapLevel(level: ExperienceLevel | ''): BackendLevel {
    if (!level) return 'unknown'
    if (level === 'novice') return 'beginner'
    return level
  }

  useEffect(() => {
    if (!started || savedGameDoc) return
    const gameEnded = !!winner || isDraw
    if (gameEnded) {
      const endedIso = new Date().toISOString()
      setEndedAt(endedIso)
      setShowUploadPreview(true)
    }
  }, [winner, isDraw, started, savedGameDoc])

  async function submitUpload() {
    if (uploadSubmitting || savedGameDoc) return
    setUploadSubmitting(true)
    setUploadError(null)
    try {
      if (!db) throw new Error('Firebase not configured')
      // Summary document under top-level /games/{gameId}
      const outcome: BackendOutcome = winner === 'X' ? '1' : winner === 'O' ? '-1' : '0'
      const startedMs = startedAt ? new Date(startedAt).getTime() : Date.now()
      const endedMs = endedAt ? new Date(endedAt).getTime() : Date.now()
      const outcomeNum = outcome === '1' ? 1 : outcome === '-1' ? -1 : 0
      const payload = {
        outcome_str: outcome,
        outcome_num: outcomeNum,
        player1_level: mapLevel(player1Exp),
        player2_level: mapLevel(player2Exp),
        started_at_ms: startedMs,
        ended_at_ms: endedMs,
      }
      await setDoc(doc(db, 'games', gameId), payload, { merge: true })

      // Per-move documents under top-level /moves collection
      const batch = writeBatch(db)
      for (const move of movesForUpload) {
        const moveId = `${move.game_id}_${move.move_index}`
        const ref = doc(db, 'moves', moveId)
        batch.set(ref, move, { merge: true })
      }
      await batch.commit()
      setSavedGameDoc(true)
      setShowUploadPreview(false)
    } catch {
      setUploadError('Failed to upload data. Please try again.')
    } finally {
      setUploadSubmitting(false)
    }
  }

  // no-op: upload is now manual via submitUpload()

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

      {!started && (
        <div className="setup">
          <h2>Game Setup</h2>
          <div className="field">
            <label htmlFor="game-id">Game ID</label>
            <input id="game-id" type="text" value={gameId} readOnly />
            <button onClick={() => setGameId(generateGameId())}>Regenerate</button>
          </div>
          <div className="field">
            <label htmlFor="p1-exp">Player X experience</label>
            <select
              id="p1-exp"
              value={player1Exp}
              onChange={(ev) => setPlayer1Exp(ev.target.value as ExperienceLevel)}
            >
              <option value="">Select...</option>
              <option value="novice">novice</option>
              <option value="intermediate">intermediate</option>
              <option value="expert">expert</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="p2-exp">Player O experience</label>
            <select
              id="p2-exp"
              value={player2Exp}
              onChange={(ev) => setPlayer2Exp(ev.target.value as ExperienceLevel)}
            >
              <option value="">Select...</option>
              <option value="novice">novice</option>
              <option value="intermediate">intermediate</option>
              <option value="expert">expert</option>
            </select>
          </div>
          <div className="actions">
            <button onClick={startGame} disabled={!player1Exp || !player2Exp}>Start Game</button>
          </div>
        </div>
      )}

      {started && (
        <>
          <div className="meta">
            <div><strong>Game:</strong> {gameId}</div>
            <div><strong>Started:</strong> {startedAt}</div>
            <div><strong>X:</strong> {player1Exp} <strong>O:</strong> {player2Exp}</div>
          </div>
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
              <button onClick={newGame}>New Game</button>
              <button onClick={exportJSON} disabled={history.length === 0}>Export JSON</button>
              <button onClick={exportCSV} disabled={history.length === 0}>Export CSV</button>
            </div>
          </div>
          {(endedAt || savedGameDoc) && (
            <div className="meta"><div><strong>Ended:</strong> {endedAt || 'saved'}</div></div>
          )}

          <div className="board" role="grid" aria-label="Tic tac toe board">
            {board.map((cell, idx) => (
              <button
                key={idx}
                className="square"
                role="gridcell"
                aria-label={`cell-${idx}`}
                onClick={() => handleSquareClick(idx)}
                disabled={!!cell || !!winner}
              >
                {cell}
              </button>
            ))}
          </div>

          {showUploadPreview && (
            <div className="setup" style={{ marginTop: '1rem' }}>
              <h2>Upload Preview</h2>
              <div className="field">
                <label>Game summary</label>
                <pre style={{ whiteSpace: 'pre-wrap', background: '#f8f8f8', padding: '0.75rem', borderRadius: 8 }}>
{JSON.stringify({
  game_id: gameId,
  outcome_str: winner ? (winner === 'X' ? '1' : '-1') : '0',
  player1_level: mapLevel(player1Exp),
  player2_level: mapLevel(player2Exp),
  started_at_ms: startedAt ? new Date(startedAt).getTime() : Date.now(),
  ended_at_ms: endedAt ? new Date(endedAt).getTime() : Date.now(),
}, null, 2)}
                </pre>
              </div>
              <div className="field">
                <label>Moves ({movesForUpload.length})</label>
                <pre style={{ whiteSpace: 'pre-wrap', background: '#f8f8f8', padding: '0.75rem', borderRadius: 8, maxHeight: 240, overflow: 'auto' }}>
{JSON.stringify(movesForUpload, null, 2)}
                </pre>
              </div>
              {uploadError && <div className="status" style={{ color: '#e74c3c' }}>{uploadError}</div>}
              <div className="actions">
                <button onClick={() => setShowUploadPreview(false)} disabled={uploadSubmitting}>Cancel</button>
                <button onClick={submitUpload} disabled={uploadSubmitting}>{uploadSubmitting ? 'Submitting...' : 'Submit Data'}</button>
              </div>
            </div>
          )}

          <div className="history">
            <h2>Move History</h2>
            {history.length === 0 && <div className="empty">No moves yet.</div>}
            {history.length > 0 && (
              <table>
                <thead>
                  <tr>
                    <th>S</th>
                    <th>move</th>
                    <th>player</th>
                    <th>S'</th>
                    <th>outcome</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((m) => (
                    <tr key={m.moveNumber}>
                      <td>
                        [
                        {m.stateBefore.map((v, i) => (
                          <span key={i} className="vec-item">{v}{i < 8 ? ', ' : ''}</span>
                        ))}
                        ]
                      </td>
                      <td>{m.position}</td>
                      <td>{m.player === 'X' ? 1 : -1}</td>
                      <td>
                        [
                        {m.moveVector.map((v, i) => (
                          <span key={i} className="vec-item">{v}{i < 8 ? ', ' : ''}</span>
                        ))}
                        ]
                      </td>
                      <td>{m.outcome}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default App
