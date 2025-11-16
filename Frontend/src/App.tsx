import ProtectedRoute from "@/components/SimpleProtectedRoute";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/SimpleAuthContext";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AIChatDemo from "./pages/AIChatDemo";
import AILab from "./pages/AILab";
import Agenti from "./pages/Agenti";
import BrowseStock from "./pages/BrowseStock";
import BuyerDashboard from "./pages/BuyerDashboard";
import BuyerProfileSetup from "./pages/BuyerProfileSetup";
import Contracts from "./pages/Contracts";
import ControlSera from "./pages/ControlSera";
import Dashboard from "./pages/Dashboard";
import FarmerProfileSetup from "./pages/FarmerProfileSetup";
import MyContracts from "./pages/MyContracts";
import NotFound from "./pages/NotFound";
import PanouriSolare from "./pages/PanouriSolare";
import Rapoarte from "./pages/Rapoarte";
import Senzori from "./pages/Senzori";
import Setari from "./pages/Setari";
import SimpleLogin from "./pages/SimpleLogin";
import SimpleRegister from "./pages/SimpleRegister";
import StockManagement from "./pages/StockManagement";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<SimpleLogin />} />
            <Route path="/register" element={<SimpleRegister />} />

            {/* Protected routes - Farmer only */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/stock"
              element={
                <ProtectedRoute requireRole="farmer">
                  <Layout>
                    <StockManagement />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/senzori"
              element={
                <ProtectedRoute requireRole="farmer">
                  <Layout>
                    <Senzori />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/sera"
              element={
                <ProtectedRoute requireRole="farmer">
                  <Layout>
                    <ControlSera />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/panouri"
              element={
                <ProtectedRoute requireRole="farmer">
                  <Layout>
                    <PanouriSolare />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/ai"
              element={
                <ProtectedRoute requireRole="farmer">
                  <Layout>
                    <AILab />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/ai-chat"
              element={
                <ProtectedRoute requireRole="farmer">
                  <Layout>
                    <AIChatDemo />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/agenti"
              element={
                <ProtectedRoute requireRole="farmer">
                  <Layout>
                    <Agenti />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/rapoarte"
              element={
                <ProtectedRoute requireRole="farmer">
                  <Layout>
                    <Rapoarte />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/setari"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Setari />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/contracts"
              element={
                <ProtectedRoute requireRole="farmer">
                  <Layout>
                    <Contracts />
                  </Layout>
                </ProtectedRoute>
              }
            />

            {/* Profile Setup Routes */}
            <Route
              path="/farmer/profile-setup"
              element={
                <ProtectedRoute requireRole="farmer">
                  <FarmerProfileSetup />
                </ProtectedRoute>
              }
            />

            {/* Buyer Routes */}
            <Route
              path="/buyer/profile-setup"
              element={
                <ProtectedRoute requireRole="buyer">
                  <BuyerProfileSetup />
                </ProtectedRoute>
              }
            />
            <Route
              path="/buyer/dashboard"
              element={
                <ProtectedRoute requireRole="buyer">
                  <Layout>
                    <BuyerDashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/buyer/browse"
              element={
                <ProtectedRoute requireRole="buyer">
                  <Layout>
                    <BrowseStock />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/buyer/orders"
              element={
                <ProtectedRoute requireRole="buyer">
                  <Layout>
                    <MyContracts />
                  </Layout>
                </ProtectedRoute>
              }
            />

            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
