import { Navigate, Outlet } from "react-router-dom";
import { isAuthenticated, getUserRole } from "../utils/auth";

export const AdminRoute = () => {
  if (!isAuthenticated()) {
    return <Navigate to="/sign-in" replace />;
  }

  if (getUserRole() !== "admin") {
    return <Navigate to="/no-access" replace />;
  }

  return <Outlet />;
};

export const UserRoute = () => {
  const authenticated = isAuthenticated();

  if (!authenticated) {
    return <Navigate to="/sign-in" replace />;
  }

  return <Outlet />;
};
