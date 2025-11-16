import { useEffect, useState } from "react";
import { ThermometerSun, Droplets, Sprout, Waves, Sun, CloudRain, TrendingUp, AlertTriangle, Package, CheckCircle, XCircle } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import KPICard from "@/components/KPICard";
import heroFarm from "@/assets/hero-farm.jpg";
import { Link } from "react-router-dom";
import { orderAPI } from "@/lib/api";
import { toast } from "sonner";

// Sample real-time data
const initialSensorData = {
  air_temp: 24.7,
  air_hum: 58.2,
  soil_hum: 41.0,
  water_level: 72.0,
  light_lux: 13500,
  rain_detected: false,
  ts: new Date().toISOString(),
};

// Sample historical data for charts
const generateHistoricalData = () => {
  const data = [];
  const now = new Date();
  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    data.push({
      time: time.toLocaleTimeString("ro-RO", { hour: "2-digit", minute: "2-digit" }),
      temp: 18 + Math.random() * 12,
      humidity: 45 + Math.random() * 25,
    });
  }
  return data;
};

const generateSoilData = () => {
  const plots = ["Parcelă A", "Parcelă B", "Parcelă C"];
  const data = [];
  const now = new Date();
  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    const entry: any = {
      time: time.toLocaleTimeString("ro-RO", { hour: "2-digit", minute: "2-digit" }),
    };
    plots.forEach(plot => {
      entry[plot] = 35 + Math.random() * 20;
    });
    data.push(entry);
  }
  return data;
};

export default function Dashboard() {
  const [sensorData, setSensorData] = useState(initialSensorData);
  const [historicalData] = useState(generateHistoricalData());
  const [soilData] = useState(generateSoilData());
  
  // Orders state
  const [orders, setOrders] = useState<any[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(true);
  const [selectedOrder, setSelectedOrder] = useState<any>(null);
  const [showAcceptDialog, setShowAcceptDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [farmerResponse, setFarmerResponse] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Fetch orders
  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const data = await orderAPI.getAll();
      const pendingOrders = data.filter((order: any) => order.status === "pending");
      setOrders(pendingOrders);
    } catch (error) {
      console.error("Error fetching orders:", error);
    } finally {
      setLoadingOrders(false);
    }
  };

  const handleAccept = async () => {
    if (!selectedOrder) return;
    
    setSubmitting(true);
    try {
      const response = await orderAPI.accept(selectedOrder._id, farmerResponse || undefined);
      toast.success(`Order accepted! Contract created: ${response.contract_id.substring(0, 8)}...`);
      setShowAcceptDialog(false);
      setFarmerResponse("");
      setSelectedOrder(null);
      fetchOrders(); // Refresh orders
    } catch (error: any) {
      console.error("Error accepting order:", error);
      toast.error(error.response?.data?.detail || "Failed to accept order");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReject = async () => {
    if (!selectedOrder) return;
    
    if (!farmerResponse.trim()) {
      toast.error("Please provide a rejection reason");
      return;
    }
    
    setSubmitting(true);
    try {
      await orderAPI.reject(selectedOrder._id, farmerResponse);
      toast.success("Order rejected");
      setShowRejectDialog(false);
      setFarmerResponse("");
      setSelectedOrder(null);
      fetchOrders(); // Refresh orders
    } catch (error: any) {
      console.error("Error rejecting order:", error);
      toast.error(error.response?.data?.detail || "Failed to reject order");
    } finally {
      setSubmitting(false);
    }
  };

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSensorData(prev => ({
        ...prev,
        air_temp: 18 + Math.random() * 12,
        air_hum: 45 + Math.random() * 25,
        soil_hum: 35 + Math.random() * 20,
        water_level: 60 + Math.random() * 30,
        light_lux: 8000 + Math.random() * 10000,
        rain_detected: Math.random() > 0.9,
        ts: new Date().toISOString(),
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getSoilStatus = (value: number) => {
    if (value < 35) return "danger";
    if (value < 45) return "warning";
    return "normal";
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl">
        <div className="absolute inset-0">
          <img 
            src={heroFarm} 
            alt="Future Farmers - Modern agricultural monitoring"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-primary/90 via-primary/70 to-transparent" />
        </div>
        <div className="relative z-10 p-6 sm:p-8 md:p-12 lg:p-16 text-primary-foreground">
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-3 sm:mb-4">
            Future Farmers
          </h1>
          <p className="text-lg sm:text-xl md:text-2xl mb-2 opacity-95">
            Starea culturilor, în timp real
          </p>
          <p className="text-base sm:text-lg mb-4 sm:mb-6 opacity-90 max-w-2xl">
            Date live din senzori + recomandări AI pentru decizii rapide
          </p>
          <Button asChild size="lg" variant="secondary" className="text-sm sm:text-base">
            <Link to="/senzori">Vezi detalii senzori</Link>
          </Button>
        </div>
      </div>

      {/* Pending Orders Section */}
      {!loadingOrders && orders.length > 0 && (
        <Card className="border-primary/50 bg-primary/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Pending Orders ({orders.length})
            </CardTitle>
            <CardDescription>New orders waiting for your response</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {orders.map((order) => (
                <Card key={order._id} className="border-2">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle className="text-base">Order from {order.buyer_name}</CardTitle>
                        <CardDescription>
                          {new Date(order.created_at).toLocaleString()} • Total: {order.total_amount.toFixed(2)} RON
                        </CardDescription>
                      </div>
                      <Badge variant="outline">Pending</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Items:</h4>
                      <div className="space-y-1">
                        {order.items.map((item: any, idx: number) => (
                          <div key={idx} className="flex justify-between text-sm">
                            <span>{item.product_name}</span>
                            <span className="text-muted-foreground">
                              {item.quantity} {item.unit} × {item.price_per_unit} RON = {item.total.toFixed(2)} RON
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {order.buyer_message && (
                      <div>
                        <h4 className="font-medium mb-1">Message:</h4>
                        <p className="text-sm text-muted-foreground">{order.buyer_message}</p>
                      </div>
                    )}
                    
                    {order.expected_delivery_date && (
                      <div>
                        <h4 className="font-medium mb-1">Expected Delivery:</h4>
                        <p className="text-sm text-muted-foreground">{order.expected_delivery_date}</p>
                      </div>
                    )}
                    
                    <div className="flex gap-2 pt-2">
                      <Button
                        onClick={() => {
                          setSelectedOrder(order);
                          setShowAcceptDialog(true);
                        }}
                        className="flex-1"
                      >
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Accept Order
                      </Button>
                      <Button
                        variant="destructive"
                        onClick={() => {
                          setSelectedOrder(order);
                          setShowRejectDialog(true);
                        }}
                        className="flex-1"
                      >
                        <XCircle className="mr-2 h-4 w-4" />
                        Reject Order
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* KPI Grid */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <KPICard
          label="Temperatură aer"
          value={sensorData.air_temp.toFixed(1)}
          unit="°C"
          icon={ThermometerSun}
          status={sensorData.air_temp > 32 ? "warning" : "normal"}
        />
        <KPICard
          label="Umiditate aer"
          value={sensorData.air_hum.toFixed(1)}
          unit="%"
          icon={Droplets}
        />
        <KPICard
          label="Umiditate sol"
          value={sensorData.soil_hum.toFixed(1)}
          unit="%"
          icon={Sprout}
          status={getSoilStatus(sensorData.soil_hum)}
        />
        <KPICard
          label="Nivel apă"
          value={sensorData.water_level.toFixed(0)}
          unit="%"
          icon={Waves}
          status={sensorData.water_level < 30 ? "danger" : sensorData.water_level < 50 ? "warning" : "normal"}
        />
        <KPICard
          label="Luminozitate"
          value={Math.round(sensorData.light_lux)}
          unit="lx"
          icon={Sun}
        />
        <KPICard
          label="Ploaie"
          value={sensorData.rain_detected ? "Da" : "Nu"}
          icon={CloudRain}
          status={sensorData.rain_detected ? "warning" : "normal"}
        />
      </div>

      {/* Charts Row */}
      <div className="grid gap-4 md:gap-6 lg:grid-cols-2">
        {/* Temperature & Humidity Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Evoluție temperatură & umiditate (24h)
            </CardTitle>
            <CardDescription>Monitorizare continuă a condițiilor atmosferice</CardDescription>
          </CardHeader>
          <CardContent>
              <ResponsiveContainer width="100%" height={250}>
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="time" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: "hsl(var(--card))", 
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem"
                  }} 
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="temp" 
                  stroke="hsl(var(--chart-1))" 
                  strokeWidth={2}
                  name="Temperatură (°C)"
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="humidity" 
                  stroke="hsl(var(--chart-2))" 
                  strokeWidth={2}
                  name="Umiditate (%)"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Soil Humidity Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sprout className="h-5 w-5 text-primary" />
              Umiditate sol pe parcele
            </CardTitle>
            <CardDescription>Monitorizare umiditate pentru fiecare parcelă</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={soilData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="time" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: "hsl(var(--card))", 
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem"
                  }} 
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="Parcelă A" 
                  stackId="1"
                  stroke="hsl(var(--chart-1))" 
                  fill="hsl(var(--chart-1))"
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="Parcelă B" 
                  stackId="2"
                  stroke="hsl(var(--chart-2))" 
                  fill="hsl(var(--chart-2))"
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="Parcelă C" 
                  stackId="3"
                  stroke="hsl(var(--chart-3))" 
                  fill="hsl(var(--chart-3))"
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* AI Summary Card */}
      <Card className="border-accent">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-accent" />
            Rezumat AI
          </CardTitle>
          <CardDescription>Analiză automată și recomandări</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 rounded-full bg-success mt-2" />
            <p className="text-sm">
              <span className="font-semibold">Starea frunzelor:</span> Foarte bună - 94% sănătoase în toate parcelele
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 rounded-full bg-warning mt-2" />
            <p className="text-sm">
              <span className="font-semibold">Dăunători detectați:</span> Afide verzi (nivel scăzut) pe Parcelă B
            </p>
          </div>
          <div className="flex items-start gap-3">
            <div className="h-2 w-2 rounded-full bg-primary mt-2" />
            <p className="text-sm">
              <span className="font-semibold">Recomandări:</span> Creșterea temperaturii prognozată - planifică irigare suplimentară pentru următoarele 48h. Umiditatea solului este optimă în prezent.
            </p>
          </div>
          <Button asChild variant="outline" className="w-full mt-4">
            <Link to="/ai">Accesează AI Lab pentru analize detaliate</Link>
          </Button>
        </CardContent>
      </Card>

      {/* Accept Order Dialog */}
      <Dialog open={showAcceptDialog} onOpenChange={setShowAcceptDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Accept Order</DialogTitle>
            <DialogDescription>
              Accepting this order will create a contract that requires both parties to sign.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="accept-response">Response Message (Optional)</Label>
              <Textarea
                id="accept-response"
                placeholder="Thank you for your order! We'll process it promptly..."
                value={farmerResponse}
                onChange={(e) => setFarmerResponse(e.target.value)}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAcceptDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleAccept} disabled={submitting}>
              {submitting ? "Accepting..." : "Accept & Create Contract"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Order Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Order</DialogTitle>
            <DialogDescription>
              Please provide a reason for rejecting this order.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="reject-reason">Rejection Reason *</Label>
              <Textarea
                id="reject-reason"
                placeholder="Unfortunately, we cannot fulfill this order because..."
                value={farmerResponse}
                onChange={(e) => setFarmerResponse(e.target.value)}
                rows={3}
                required
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRejectDialog(false)}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleReject} 
              disabled={submitting || !farmerResponse.trim()}
            >
              {submitting ? "Rejecting..." : "Reject Order"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
