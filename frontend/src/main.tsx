import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { GoogleOAuthProvider } from "@react-oauth/google";
import './index.css'
import App from './App.tsx'
import { logout } from './utils/auth'
import { API_BASE_URL } from './utils/api'

// Global 401 interceptor - redirects to sign-in on unauthorized responses from backend API
const originalFetch = window.fetch;

window.fetch = async (...args) => {
  const res = await originalFetch(...args);

  const url = args[0] instanceof Request ? args[0].url : String(args[0]);

  // Only handle 401 if it comes from the backend API endpoint
  const isBackendApiRequest = url.startsWith(API_BASE_URL);

  if (
    res.status === 401 &&
    isBackendApiRequest &&
    !window.location.pathname.startsWith('/sign-in')
  ) {
    logout();
    window.location.href = '/sign-in';
    // Prevent downstream code from processing the 401 response.
    return new Promise(() => {});
  }

  return res;
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
    <App />
    </GoogleOAuthProvider>
  </StrictMode>,
)
