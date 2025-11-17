import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { useEffect, useState } from 'react'
import Visualization from './Visualization.tsx'

function Router() {
  const [path, setPath] = useState<string>(window.location.pathname)

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname)
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])

  function navigate(to: string) {
    if (to !== window.location.pathname) {
      window.history.pushState({}, '', to)
      setPath(to)
    }
  }

  return (
    <>
      <div style={{ padding: '10px', borderBottom: '1px solid #eee', marginBottom: 12 }}>
        <button onClick={() => navigate('/')} style={{ marginRight: 8 }}>
          Data Collection
        </button>
        <button onClick={() => navigate('/visualize')}>
          Visualization
        </button>
      </div>
      {path === '/visualize' ? <Visualization /> : <App />}
    </>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Router />
  </StrictMode>,
)
