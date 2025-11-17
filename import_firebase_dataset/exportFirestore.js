// exportFirestore.js
import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import fs from 'fs';

const serviceAccount = JSON.parse(fs.readFileSync('appConfig.json', 'utf8'));
initializeApp({ credential: cert(serviceAccount) });

const db = getFirestore();

async function exportData() {
  const collections = ['games', 'moves'];
  const backup = {};

  for (const col of collections) {
    const snapshot = await db.collection(col).get();
    backup[col] = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
  }

  fs.writeFileSync('backup.json', JSON.stringify(backup, null, 2));
  console.log('✅ Export complete');
}

exportData();
