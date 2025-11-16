import { useAuth } from "@/contexts/SimpleAuthContext";
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
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!isLoading) {
      // Not authenticated - redirect to login
      if (!user) {
        navigate("/login", { state: { from: location }, replace: true });
        return;
      }

      // Check role requirement
      if (requireRole && user.role !== requireRole) {
        // Redirect to appropriate dashboard based on actual role
        if (user.role === "buyer") {
          navigate("/buyer/dashboard", { replace: true });
        } else {
          navigate("/", { replace: true });
        }
        return;
      }

      // Redirect buyer accessing root to buyer dashboard
      if (user.role === "buyer" && location.pathname === "/") {
        navigate("/buyer/dashboard", { replace: true });
        return;
      }
    }
  }, [user, isLoading, requireRole, navigate, location]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!user) {
    return null;
  }

  // Wrong role
  if (requireRole && user.role !== requireRole) {
    return null;
  }

  return <>{children}</>;
}
