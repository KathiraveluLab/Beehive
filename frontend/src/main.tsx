import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { GoogleOAuthProvider } from "@react-oauth/google";
import './index.css'
import App from './App.tsx'
import { logout } from './utils/auth'
import { API_BASE_URL } from './utils/api'
import { SIGN_IN_PATH } from './constants/routes'

// Validate that URL is from our backend API (prevents URL bypass attacks)
const isBackendRequest = (url: string): boolean => {
  try {
    const urlObj = new URL(url, window.location.origin);
    const apiObj = new URL(API_BASE_URL);
    // Strict check: same protocol, host, and port; path must start with API path
    return (
      urlObj.protocol === apiObj.protocol &&
      urlObj.host === apiObj.host &&
      urlObj.pathname.startsWith(apiObj.pathname)
    );
  } catch {
    return false;
  }
};

// Global 401 interceptor - redirects to sign-in on unauthorized responses from backend API only
const originalFetch = window.fetch;

window.fetch = async (...args) => {
  const res = await originalFetch(...args);

  const urlString = typeof args[0] === "string" ? args[0] : args[0]?.url;
  const isBackendApiRequest = urlString && isBackendRequest(urlString);

  // Only handle 401 from backend API (not from external requests)
  if (
    res.status === 401 &&
    isBackendApiRequest &&
    !window.location.pathname.startsWith(SIGN_IN_PATH)
  ) {
    try {
      logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
    // Redirect to sign-in (use setTimeout to allow pending requests to complete)
    setTimeout(() => {
      window.location.href = SIGN_IN_PATH;
    }, 0);
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
