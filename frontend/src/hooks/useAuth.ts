import { useUser } from "@clerk/clerk-react";

export const useAuth = () => {
  const { user } = useUser();
  
  const isAdmin = () => {
    // console.log(user?.unsafeMetadata?.role);
    return user?.unsafeMetadata?.role === "admin";
  };

  const isUser = () => {
    // console.log(user?.unsafeMetadata?.role);
    return !user?.unsafeMetadata?.role || user?.unsafeMetadata?.role === "user";
  };

  return {
    isAdmin,
    isUser,
    user
  };
}; 