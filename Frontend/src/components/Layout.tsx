import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/contexts/SimpleAuthContext";
import { cn } from "@/lib/utils";
import {
  Bot,
  FileChartLine,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageCircle,
  Package,
  ScanLine,
  Settings,
  ShoppingCart,
  Signal,
  Sprout,
  Sun,
  User,
  Warehouse,
  X,
} from "lucide-react";
import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

const farmerNavItems = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/stock", label: "Stock Management", icon: Package },
  { path: "/contracts", label: "Contracts", icon: FileChartLine },
  { path: "/senzori", label: "Senzori", icon: Signal },
  { path: "/sera", label: "Control Seră", icon: Warehouse },
  { path: "/panouri", label: "Panouri Solare", icon: Sun },
  { path: "/ai", label: "AI Lab", icon: ScanLine },
  { path: "/ai-chat", label: "AI Chat", icon: MessageCircle },
  { path: "/agenti", label: "Agenți", icon: Bot },
  { path: "/rapoarte", label: "Rapoarte", icon: FileChartLine },
  { path: "/setari", label: "Setări", icon: Settings },
];

const buyerNavItems = [
  { path: "/buyer/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { path: "/buyer/browse", label: "Browse Products", icon: Package },
  { path: "/buyer/orders", label: "My Orders", icon: ShoppingCart },
  { path: "/setari", label: "Settings", icon: Settings },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  // Select navigation items based on role
  const navItems = user?.role === "buyer" ? buyerNavItems : farmerNavItems;

  const getInitials = (name?: string, email?: string) => {
    if (name) {
      return name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);
    }
    if (email) {
      return email.substring(0, 2).toUpperCase();
    }
    return "U";
  };

  const getRoleBadge = (userRole?: string) => {
    if (userRole === "farmer") {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/10 text-primary">
          Farmer
        </span>
      );
    }
    if (userRole === "buyer") {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-accent/10 text-accent">
          Buyer
        </span>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen gradient-subtle">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-border/50 bg-card/80 backdrop-blur-xl supports-[backdrop-filter]:bg-card/60 shadow-sm">
        <div className="container flex h-20 items-center px-6">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden mr-3 hover:bg-muted/50"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          >
            {isSidebarOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </Button>

          <Link to="/" className="flex items-center gap-3 group">
            <div className="p-2 rounded-xl bg-primary/10 group-hover:bg-primary/20 transition-colors">
              <Sprout className="h-6 w-6 text-primary" />
            </div>
            <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Future Farmers
            </span>
          </Link>

          <div className="ml-auto flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 border border-success/20">
              <div className="h-2 w-2 rounded-full bg-success animate-pulse shadow-glow" />
              <span className="text-sm font-medium text-success">Live</span>
            </div>

            {/* User Menu */}
            {user && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="relative h-10 w-10 rounded-full"
                  >
                    <Avatar className="h-10 w-10">
                      <AvatarFallback className="bg-primary text-primary-foreground">
                        {getInitials(user.name, user.email)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {user.name || "User"}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user.email}
                      </p>
                      <div className="pt-1">{getRoleBadge(user.role)}</div>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/setari" className="cursor-pointer">
                      <User className="mr-2 h-4 w-4" />
                      <span>Profile</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/setari" className="cursor-pointer">
                      <Settings className="mr-2 h-4 w-4" />
                      <span>Settings</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={logout}
                    className="cursor-pointer text-destructive"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside
          className={cn(
            "fixed inset-y-0 left-0 z-40 w-72 transform border-r border-border/50 bg-card/60 backdrop-blur-xl transition-transform duration-300 ease-in-out mt-20 shadow-premium",
            isSidebarOpen ? "translate-x-0" : "-translate-x-full",
            "md:translate-x-0 md:static"
          )}
        >
          <nav className="space-y-2 p-6">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setIsSidebarOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200",
                    isActive
                      ? "gradient-primary text-white shadow-md shadow-primary/20"
                      : "hover:bg-muted/50 text-foreground/80 hover:text-foreground hover:translate-x-1"
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Overlay for mobile */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-background/80 backdrop-blur-sm md:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Main content */}
        <main className="flex-1 p-4 sm:p-6 md:p-8 lg:p-10">{children}</main>
      </div>
    </div>
  );
}
