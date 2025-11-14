import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Senzori from "./pages/Senzori";
import ControlSera from "./pages/ControlSera";
import PanouriSolare from "./pages/PanouriSolare";
import AILab from "./pages/AILab";
import Agenti from "./pages/Agenti";
import Rapoarte from "./pages/Rapoarte";
import Setari from "./pages/Setari";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/senzori" element={<Senzori />} />
            <Route path="/sera" element={<ControlSera />} />
            <Route path="/panouri" element={<PanouriSolare />} />
            <Route path="/ai" element={<AILab />} />
            <Route path="/agenti" element={<Agenti />} />
            <Route path="/rapoarte" element={<Rapoarte />} />
            <Route path="/setari" element={<Setari />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
