import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from '../src/context/ThemeContext';

// Layout
import MainLayout from '../src/layouts/MainLayout';
import AuthLayout from '../src/layouts/AuthLayout';

// Pages
import Home from './pages/Home';
import Gallery from '../src/pages/Gallery';
import Upload from '../src/pages/Upload';
import AdminDashboard from './pages/admin/Dashboard';
import AdminUsers from './pages/admin/Users';
import AdminAnalytics from '../src/pages/admin/Analytics';
import SignInPage from './pages/auth/SignIn';
import SignUpPage from './pages/auth/SignUp';

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

function App() {
  if (!clerkPubKey) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-red-500">Missing Clerk Publishable Key</p>
      </div>
    );
  }

  return (
    <ClerkProvider publishableKey={clerkPubKey}>
      <ThemeProvider>
        <Router>
          <Routes>
            {/* Auth Routes */}
            <Route element={<AuthLayout />}>
              <Route path="/sign-in" element={<SignInPage />} />
              <Route path="/sign-up" element={<SignUpPage />} />
            </Route>

            {/* Protected Routes */}
            <Route element={<MainLayout />}>
              <Route path="/" element={<Home />} />
              <Route path="/gallery" element={<Gallery />} />
              <Route path="/upload" element={<Upload />} />
              
              {/* Admin Routes */}
              <Route path="/admin">
                <Route index element={<AdminDashboard />} />
                <Route path="users" element={<AdminUsers />} />
                <Route path="analytics" element={<AdminAnalytics />} />
              </Route>
            </Route>
          </Routes>
        </Router>
        <Toaster position="top-center" />
      </ThemeProvider>
    </ClerkProvider>
  );
}

export default App;
