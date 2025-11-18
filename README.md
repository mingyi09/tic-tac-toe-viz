## Tic-Tac-Toe

A data collection/visualization tool for Tic-Tac-Toe.

Visualization Tool: https://tic-tac-toe-d1b97.web.app/visualize.
Data Collection Site: https://tic-tac-toe-d1b97.web.app/
Short video demo: https://drive.google.com/file/d/1thM_GlFd9HmQzhMnShImB8lrYps_0jVm/view?usp=sharing

### Scripts

- `npm run dev`: start dev server
- `npm run build`: build for production
- `npm run preview`: preview the production build
- To run it locally, include your own firebase API key in a .env file: \
VITE_FIREBASE_API_KEY="" \
VITE_FIREBASE_AUTH_DOMAIN="" \
VITE_FIREBASE_PROJECT_ID="" \
VITE_FIREBASE_APP_ID=""

- Install dependencies: `npm install`
- Start dev server: `npm run dev`

### Deploy: Firebase Hosting
- Set up Firebase Project
- Build and deploy:

```
npm run build
firebase deploy --only hosting
```


