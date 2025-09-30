## Tic-Tac-Toe (React + TypeScript)

Two human players play tic-tac-toe. Each move records a 9-length vector for the acting player (1 for the player's marks, 0 otherwise). You can export the move history as JSON or CSV.

### Scripts

- `npm run dev`: start dev server
- `npm run build`: build for production
- `npm run preview`: preview the production build

### How it works

- Board is a 3x3 grid stored as a 9-element array
- On each move, we compute the acting player's vector `[v0..v8]` from the board after the move
- Move history lists move number, player, position index (0–8), and the vector
- Export buttons download JSON or CSV of the recorded moves

### Development

1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Open the app and play; use Export to download data
