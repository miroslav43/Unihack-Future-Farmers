import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useAuth } from "@/contexts/SimpleAuthContext";
import { buyerAPI, inventoryAPI } from "@/lib/api";
import { Clock, Package, ShoppingCart, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

interface BuyerStats {
  total_orders: number;
  pending_orders: number;
  available_products: number;
}

export default function BuyerDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<BuyerStats>({
    total_orders: 0,
    pending_orders: 0,
    available_products: 0,
  });
  const [loading, setLoading] = useState(true);
  const [hasProfile, setHasProfile] = useState(false);

  useEffect(() => {
    checkProfile();
    fetchStats();
  }, []);

  const checkProfile = async () => {
    try {
      await buyerAPI.getMyProfile();
      setHasProfile(true);
    } catch (error) {
      console.log("No buyer profile yet");
      setHasProfile(false);
    }
  };

  const fetchStats = async () => {
    try {
      // Get available products count
      const products = await inventoryAPI.getAvailable();

      setStats({
        total_orders: 0, // TODO: Implement when orders are ready
        pending_orders: 0,
        available_products: products.length,
      });
    } catch (error) {
      console.error("Error fetching stats:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!hasProfile) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-200px)]">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Complete Your Buyer Profile</CardTitle>
            <CardDescription>
              Before you can browse and order products, please complete your
              buyer profile.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/buyer/profile-setup">
              <Button className="w-full">Complete Profile</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">
          Welcome, {user?.name || "Buyer"}!
        </h1>
        <p className="text-muted-foreground">
          Browse fresh products directly from local farms
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Available Products
            </CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.available_products}</div>
            <p className="text-xs text-muted-foreground">
              Fresh products ready to order
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">My Orders</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_orders}</div>
            <p className="text-xs text-muted-foreground">Total orders placed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending_orders}</div>
            <p className="text-xs text-muted-foreground">
              Awaiting confirmation
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-primary/10">
                <Package className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle>Browse Products</CardTitle>
                <CardDescription>
                  View available products from local farms
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Link to="/buyer/browse">
              <Button className="w-full">Browse Stock</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-full bg-accent/10">
                <ShoppingCart className="h-6 w-6 text-accent" />
              </div>
              <div>
                <CardTitle>My Orders</CardTitle>
                <CardDescription>
                  View and track your order history
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Link to="/buyer/orders">
              <Button variant="secondary" className="w-full">
                View Orders
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity / Featured Products */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Getting Started
          </CardTitle>
          <CardDescription>Here's how to make your first order</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start gap-3">
            <div className="rounded-full bg-primary/10 p-2 text-primary font-semibold text-sm">
              1
            </div>
            <div>
              <h4 className="font-medium">Browse Available Products</h4>
              <p className="text-sm text-muted-foreground">
                Explore fresh products from verified local farms
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="rounded-full bg-primary/10 p-2 text-primary font-semibold text-sm">
              2
            </div>
            <div>
              <h4 className="font-medium">Select Quantity</h4>
              <p className="text-sm text-muted-foreground">
                Choose the amount you need (within min/max limits)
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="rounded-full bg-primary/10 p-2 text-primary font-semibold text-sm">
              3
            </div>
            <div>
              <h4 className="font-medium">Place Order</h4>
              <p className="text-sm text-muted-foreground">
                A blockchain contract will be generated automatically
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="rounded-full bg-primary/10 p-2 text-primary font-semibold text-sm">
              4
            </div>
            <div>
              <h4 className="font-medium">Sign & Confirm</h4>
              <p className="text-sm text-muted-foreground">
                Both you and the farmer will digitally sign the contract
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
