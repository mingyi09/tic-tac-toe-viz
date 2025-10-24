## Tic-Tac-Toe (React + TypeScript)

A data collection site for visualizing Tic-Tac-Toe.

URL: https://tic-tac-toe-d1b97.web.app/.

### Scripts

- `npm run dev`: start dev server
- `npm run build`: build for production
- `npm run preview`: preview the production build

### How it works

- Board is a 3x3 grid stored as a 9-element array
- On each move, we compute the acting player's vector `[v0..v8]` from the board after the move

### Local Development

- Install dependencies: `npm install`
- Start dev server: `npm run dev`

### Deploy: Firebase Hosting
- Set up Firebase Project
- Build and deploy:

```
npm run build
firebase deploy --only hosting
```


