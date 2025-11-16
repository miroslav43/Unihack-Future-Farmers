import { useAuth } from "@/contexts/AuthContext";
import { Loader2 } from "lucide-react";
import { ReactNode, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

interface ProtectedRouteProps {
  children: ReactNode;
  requireRole?: "farmer" | "buyer";
}

export default function ProtectedRoute({
  children,
  requireRole,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, role, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!isLoading) {
      // Not authenticated - redirect to login
      if (!isAuthenticated) {
        login();
        return;
      }

      // Authenticated but no role set - redirect to role selection
      if (!role) {
        navigate("/select-role", { state: { from: location }, replace: true });
        return;
      }

      // Has role but wrong role for this route
      if (requireRole && role !== requireRole) {
        // Redirect to appropriate dashboard based on role
        if (role === "buyer") {
          navigate("/buyer/dashboard", { replace: true });
        } else {
          navigate("/", { replace: true });
        }
        return;
      }

      // Redirect buyer accessing root to buyer dashboard
      if (role === "buyer" && location.pathname === "/") {
        navigate("/buyer/dashboard", { replace: true });
        return;
      }
    }
  }, [
    isAuthenticated,
    isLoading,
    role,
    requireRole,
    navigate,
    location,
    login,
  ]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Show nothing while redirecting
  if (!isAuthenticated || !role || (requireRole && role !== requireRole)) {
    return null;
  }

  return <>{children}</>;
}
