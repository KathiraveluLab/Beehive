import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ClerkProvider } from '@clerk/clerk-react'
import './index.css'
import App from './App.tsx'

const PUBLISHABLE_KEY = "pk_test_cmljaC1ibHVlZ2lsbC02MC5jbGVyay5hY2NvdW50cy5kZXYk"

createRoot(document.getElementById('root')!).render(
  
  <StrictMode>
    {/* <ClerkProvider publishableKey={PUBLISHABLE_KEY}> */}
      <App />
    {/* </ClerkProvider> */}
  </StrictMode>,
)
