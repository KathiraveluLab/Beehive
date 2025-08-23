import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from '../src/context/ThemeContext';

// Layout
import MainLayout from '../src/layouts/MainLayout';
import AuthLayout from '../src/layouts/AuthLayout';
import AdminLayout from '../src/layouts/AdminLayout';

// Protected Routes
import { AdminRoute, UserRoute } from './components/ProtectedRoutes';

// Pages
import Home from './pages/Home';
import Gallery from '../src/pages/Gallery';
import Upload from '../src/pages/Upload';
import AdminDashboard from './pages/admin/Dashboard';
import AdminUsers from './pages/admin/Users';
import AdminAnalytics from '../src/pages/admin/Analytics';
import UserUploads from './pages/admin/UserUploads';
import SignInPage from './pages/auth/SignIn';
import SignUpPage from './pages/auth/SignUp';
import Landing from './pages/Landing';
import NoAccess from './pages/NoAccess';
import AboutUs from './pages/AboutUs';
import PrivacyPolicy from './pages/Privacy';
import TermsOfService from './pages/TermsofService';

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
    <ClerkProvider 
      publishableKey={clerkPubKey}
    >
      <ThemeProvider>
        <Router>
          <Routes>
            {/* Public Routes */}
            <Route path="/landing" element={<Landing />} />
            <Route path="/no-access" element={<NoAccess />} />
            <Route path="/about" element={<AboutUs />} />
            <Route path="/privacy" element={<PrivacyPolicy />} />
            <Route path="/terms" element={<TermsOfService />} />
            
            {/* Auth Routes */}
            <Route element={<AuthLayout />}>
              <Route path="/sign-in/*" element={<SignInPage />} />
              <Route path="/sign-up/*" element={<SignUpPage />} />
              <Route path="/one-factor" element={<SignInPage />} />
            </Route>

            {/* Protected User Routes */}
            <Route element={<UserRoute />}>
              <Route element={<MainLayout />}>
                <Route path="/dashboard" element={<Home />} />
                <Route path="/gallery" element={<Gallery />} />
                <Route path="/upload" element={<Upload />} />
              </Route>
            </Route>

            {/* Protected Admin Routes */}
            <Route element={<AdminRoute />}>
              <Route element={<AdminLayout />}>
                <Route path="/admin">
                  <Route index element={<AdminDashboard />} />
                  <Route path="users" element={<AdminUsers />} />
                  <Route path="users/:userId/uploads" element={<UserUploads />} />
                  <Route path="analytics" element={<AdminAnalytics />} />
                </Route>
              </Route>
            </Route>

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/landing" replace />} />
          </Routes>
        </Router>
        <Toaster position="top-center" />
      </ThemeProvider>
    </ClerkProvider>
  );
}

export default App;
