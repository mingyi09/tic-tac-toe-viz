import { getApp, getApps, initializeApp } from 'firebase/app'
import { getFirestore, serverTimestamp, Timestamp } from 'firebase/firestore'

const apiKey = import.meta.env.VITE_FIREBASE_API_KEY
const authDomain = import.meta.env.VITE_FIREBASE_AUTH_DOMAIN
const projectId = import.meta.env.VITE_FIREBASE_PROJECT_ID
const appId = import.meta.env.VITE_FIREBASE_APP_ID

let dbRef: ReturnType<typeof getFirestore> | null = null
if (apiKey && authDomain && projectId && appId) {
  const firebaseConfig = { apiKey, authDomain, projectId, appId }
  const app = getApps().length ? getApp() : initializeApp(firebaseConfig)
  dbRef = getFirestore(app)
}

export const db = dbRef
export { serverTimestamp, Timestamp }


