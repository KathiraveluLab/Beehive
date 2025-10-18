import { useUser } from "@clerk/clerk-react";

export const useAuth = () => {
  const { user } = useUser();
  
  const isAdmin = () => {
    // console.log(user?.publicMetadata?.role);
    return user?.publicMetadata?.role === "admin";
  };

  const isUser = () => {
    // console.log(user?.publicMetadata?.role);
    return !user?.publicMetadata?.role || user?.publicMetadata?.role === "user";
  };

  return {
    isAdmin,
    isUser,
    user
  };
}; 