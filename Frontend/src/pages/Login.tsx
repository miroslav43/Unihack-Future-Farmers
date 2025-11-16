import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";
import { Lock, Shield, Sprout, Zap } from "lucide-react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      navigate("/", { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center gradient-subtle p-4">
      <div className="w-full max-w-5xl grid md:grid-cols-2 gap-8 items-center">
        {/* Left side - Branding */}
        <div className="text-center md:text-left space-y-6">
          <div className="inline-flex items-center gap-3">
            <div className="p-3 rounded-xl bg-primary/10">
              <Sprout className="h-12 w-12 text-primary" />
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Future Farmers
            </h1>
          </div>

          <p className="text-xl text-foreground/80 max-w-md">
            Smart farming meets blockchain technology. Connect farmers and
            buyers with transparent, secure contracts.
          </p>

          <div className="space-y-4 pt-4">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-primary/5">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">Secure Authentication</h3>
                <p className="text-sm text-muted-foreground">
                  Enterprise-grade security with Auth0
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-primary/5">
                <Lock className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">Blockchain Contracts</h3>
                <p className="text-sm text-muted-foreground">
                  Transparent, immutable order agreements
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-primary/5">
                <Zap className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">Real-time Monitoring</h3>
                <p className="text-sm text-muted-foreground">
                  Live sensor data and AI-powered insights
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right side - Login Card */}
        <Card className="shadow-2xl">
          <CardHeader className="text-center space-y-2">
            <CardTitle className="text-3xl">Welcome Back</CardTitle>
            <CardDescription>Sign in to access your dashboard</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Button onClick={login} size="lg" className="w-full text-lg h-14">
              <Lock className="mr-2 h-5 w-5" />
              Sign in with Auth0
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  New to Future Farmers?
                </span>
              </div>
            </div>

            <Button
              onClick={login}
              variant="outline"
              size="lg"
              className="w-full text-lg h-14"
            >
              Create Account
            </Button>

            <p className="text-xs text-center text-muted-foreground">
              By continuing, you agree to our Terms of Service and Privacy
              Policy. After signing in, you'll choose your role as a Farmer or
              Buyer.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
