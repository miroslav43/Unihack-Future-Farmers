import { authAPI, setupAuthInterceptor } from "@/lib/api";
import { useAuth0 } from "@auth0/auth0-react";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";

interface User {
  id: string;
  auth0_id: string;
  email: string;
  role?: "farmer" | "buyer";
  name?: string;
  picture?: string;
  email_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  role: "farmer" | "buyer" | null;
  login: () => void;
  logout: () => void;
  setRole: (role: "farmer" | "buyer") => Promise<void>;
  syncUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const {
    isAuthenticated: auth0IsAuthenticated,
    isLoading: auth0IsLoading,
    loginWithRedirect,
    logout: auth0Logout,
    getAccessTokenSilently,
    user: auth0User,
  } = useAuth0();

  const [user, setUser] = useState<User | null>(null);
  const [role, setRoleState] = useState<"farmer" | "buyer" | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Setup axios interceptor with Auth0 token
  useEffect(() => {
    if (auth0IsAuthenticated) {
      setupAuthInterceptor(getAccessTokenSilently);
    }
  }, [auth0IsAuthenticated, getAccessTokenSilently]);

  // Sync user when Auth0 authentication completes
  useEffect(() => {
    const syncUserData = async () => {
      if (auth0IsAuthenticated && auth0User) {
        setIsLoading(true);
        try {
          // Sync user with backend
          const userData = await authAPI.syncUser();
          setUser(userData);
          setRoleState(userData.role || null);
        } catch (error) {
          console.error("Error syncing user:", error);
        } finally {
          setIsLoading(false);
        }
      } else {
        setUser(null);
        setRoleState(null);
        setIsLoading(false);
      }
    };

    if (!auth0IsLoading) {
      syncUserData();
    }
  }, [auth0IsAuthenticated, auth0IsLoading, auth0User]);

  const login = () => {
    loginWithRedirect({
      appState: { returnTo: window.location.pathname },
    });
  };

  const logout = () => {
    auth0Logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    });
    setUser(null);
    setRoleState(null);
  };

  const setRole = async (newRole: "farmer" | "buyer") => {
    try {
      const updatedUser = await authAPI.setUserRole(newRole);
      setUser(updatedUser);
      setRoleState(updatedUser.role);
    } catch (error) {
      console.error("Error setting role:", error);
      throw error;
    }
  };

  const syncUser = async () => {
    try {
      const userData = await authAPI.syncUser();
      setUser(userData);
      setRoleState(userData.role || null);
    } catch (error) {
      console.error("Error syncing user:", error);
      throw error;
    }
  };

  const value = {
    user,
    isLoading: auth0IsLoading || isLoading,
    isAuthenticated: auth0IsAuthenticated && !!user,
    role,
    login,
    logout,
    setRole,
    syncUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
