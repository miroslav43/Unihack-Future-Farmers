import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AIChatDemo from "./pages/AIChatDemo";
import AILab from "./pages/AILab";
import Agenti from "./pages/Agenti";
import ControlSera from "./pages/ControlSera";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";
import PanouriSolare from "./pages/PanouriSolare";
import Rapoarte from "./pages/Rapoarte";
import Senzori from "./pages/Senzori";
import Setari from "./pages/Setari";

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
            <Route path="/ai-chat" element={<AIChatDemo />} />
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
