import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { SignedIn } from '@clerk/clerk-react';

export const AdminRoute = () => {
  const { isAdmin, user } = useAuth();

  return (
    <SignedIn>
      {isAdmin() ? (
        <Outlet />
      ) : (
        <Navigate to="/no-access" replace />
      )}
    </SignedIn>
  );
};

export const UserRoute = () => {
  const { isUser } = useAuth();

  return (
    <SignedIn>
      {(isUser()) ? (
        <Outlet />
      ) : (
        <Navigate to="/landing" replace />
      )}
    </SignedIn>
  );
}; 