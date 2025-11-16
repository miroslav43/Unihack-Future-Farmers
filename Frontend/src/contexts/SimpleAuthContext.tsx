import axios from "axios";
import Cookies from "js-cookie";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

interface User {
  id: string;
  email: string;
  name: string;
  role: "farmer" | "buyer";
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    name: string,
    role: "farmer" | "buyer"
  ) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Load token from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem("access_token");
    const savedUser = localStorage.getItem("user");

    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const API_URL =
        import.meta.env.VITE_API_URL || "http://localhost:8001/api/v1";
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password,
      });

      const { access_token, user: userData } = response.data;

      setToken(access_token);
      setUser(userData);

      // Save to localStorage
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(userData));

      // Redirect based on role
      if (userData.role === "buyer") {
        navigate("/buyer/dashboard");
      } else {
        navigate("/");
      }
    } catch (error) {
      console.error("Login error:", error);
      throw error;
    }
  };

  const register = async (
    email: string,
    password: string,
    name: string,
    role: "farmer" | "buyer"
  ) => {
    try {
      const API_URL =
        import.meta.env.VITE_API_URL || "http://localhost:8001/api/v1";
      const response = await axios.post(`${API_URL}/auth/register`, {
        email,
        password,
        name,
        role,
      });

      const { access_token, user: userData } = response.data;

      setToken(access_token);
      setUser(userData);

      // Save to localStorage
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(userData));

      // Redirect NEW users to profile setup
      if (userData.role === "buyer") {
        navigate("/buyer/profile-setup");
      } else {
        navigate("/farmer/profile-setup");
      }
    } catch (error) {
      console.error("Register error:", error);
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <AuthContext.Provider
      value={{ user, token, login, register, logout, isLoading }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
