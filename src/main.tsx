import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { useEffect, useState } from 'react'
import App from './App.tsx'
import Visualization from './Visualization.tsx'
import AiModels from './AiModels.tsx'
import ProjectPage from './ProjectPage.tsx'

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
      <div style={{ padding: '10px', borderBottom: '1px solid #eee', marginBottom: 12, display: 'flex', gap: 8 }}>
        <button onClick={() => navigate('/project')}>
          Project Page
        </button>
        <button onClick={() => navigate('/')}>Data Collection</button>
        <button onClick={() => navigate('/visualize')}>Visualization</button>
        <button onClick={() => navigate('/ai-models')}>About the AI Models</button>
      </div>
      {path === '/project' && <ProjectPage />}
      {path === '/visualize' && <Visualization />}
      {path === '/ai-models' && <AiModels />}
      {path !== '/project' && path !== '/visualize' && path !== '/ai-models' && <App />}
    </>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Router />
  </StrictMode>,
)
