import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";
import { Loader2, ShoppingCart, Sprout } from "lucide-react";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";

export default function SelectRole() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { setRole, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = (location.state as any)?.from?.pathname || "/";

  const handleSelectRole = async (selectedRole: "farmer" | "buyer") => {
    setIsSubmitting(true);
    try {
      await setRole(selectedRole);
      toast.success(`Welcome! You are now registered as a ${selectedRole}.`);
      navigate(from, { replace: true });
    } catch (error) {
      console.error("Error setting role:", error);
      toast.error("Failed to set role. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // If user already has a role, redirect
  if (user?.role) {
    navigate(from, { replace: true });
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center gradient-subtle p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <Sprout className="h-10 w-10 text-primary" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Future Farmers
            </h1>
          </div>
          <h2 className="text-2xl font-semibold mb-2">Welcome!</h2>
          <p className="text-muted-foreground">
            Choose your role to get started with our platform
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Farmer Card */}
          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:scale-105 border-2 hover:border-primary"
            onClick={() => !isSubmitting && handleSelectRole("farmer")}
          >
            <CardHeader className="text-center">
              <div className="mx-auto w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Sprout className="h-10 w-10 text-primary" />
              </div>
              <CardTitle className="text-2xl">I'm a Farmer</CardTitle>
              <CardDescription>
                Manage your farm, track inventory, and connect with buyers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">✓</span>
                  <span>Manage farm inventory and stock</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">✓</span>
                  <span>Monitor sensors and greenhouse</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">✓</span>
                  <span>Receive and sign contracts</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">✓</span>
                  <span>Track orders and deliveries</span>
                </li>
              </ul>
              <Button
                className="w-full mt-6"
                disabled={isSubmitting}
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectRole("farmer");
                }}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Setting up...
                  </>
                ) : (
                  "Continue as Farmer"
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Buyer Card */}
          <Card
            className="cursor-pointer transition-all hover:shadow-lg hover:scale-105 border-2 hover:border-accent"
            onClick={() => !isSubmitting && handleSelectRole("buyer")}
          >
            <CardHeader className="text-center">
              <div className="mx-auto w-20 h-20 rounded-full bg-accent/10 flex items-center justify-center mb-4">
                <ShoppingCart className="h-10 w-10 text-accent" />
              </div>
              <CardTitle className="text-2xl">I'm a Buyer</CardTitle>
              <CardDescription>
                Browse fresh produce and place orders directly from farms
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-accent">✓</span>
                  <span>Browse available farm products</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent">✓</span>
                  <span>Place orders with smart contracts</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent">✓</span>
                  <span>Track order status and delivery</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent">✓</span>
                  <span>Direct communication with farmers</span>
                </li>
              </ul>
              <Button
                variant="secondary"
                className="w-full mt-6"
                disabled={isSubmitting}
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelectRole("buyer");
                }}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Setting up...
                  </>
                ) : (
                  "Continue as Buyer"
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        <p className="text-center text-sm text-muted-foreground mt-8">
          You can't change your role after selection. Choose carefully!
        </p>
      </div>
    </div>
  );
}
