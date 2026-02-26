import { useMemo } from "react";

interface JwtPayload {
  sub: string;
  role?: "admin" | "user";
  exp?: number;
  iat?: number;
  name?: string;
  given_name?: string;
  family_name?: string;
  firstName?: string;
  lastName?: string;
}

type User = {
  id: string;
  role?: "admin" | "user";
  exp?: number;
  iat?: number;
  name?: string;
  firstName?: string;
  lastName?: string;
};

function decodeToken(): User | null {
  const token = localStorage.getItem("access_token");
  if (!token) return null;

  try {
    const payload = JSON.parse(atob(token.split(".")[1])) as JwtPayload;

    return {
      id: payload.sub,
      role: payload.role,
      exp: payload.exp,
      iat: payload.iat,
      // Normalize possible name fields from different issuers
      name: payload.name,
      firstName: payload.firstName || payload.given_name,
      lastName: payload.lastName || payload.family_name,
    } as User;
  } catch {
    return null;
  }
}

export const useAuth = () => {
  const user = useMemo(() => decodeToken(), []);

  const isAuthenticated = () => {
    if (!user) return false;
    return (user.exp ?? 0) * 1000 > Date.now(); // token not expired
  };

  const isAdmin = () => {
    return isAuthenticated() && user?.role === "admin";
  };

  const isUser = () => {
    return isAuthenticated() && user?.role === "user";
  };

  return {
    user,
    isAuthenticated,
    isAdmin,
    isUser,
  };
};
