import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { inventoryAPI, orderAPI, farmerAPI } from "@/lib/api";
import { Filter, MapPin, Package, Search, ShoppingCart, Plus, Minus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

interface Product {
  _id: string;
  product_name: string;
  category: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  location?: string;
  description?: string;
  min_order_quantity?: number;
  max_order_quantity?: number;
  farmer_id: string;
}

interface CartItem {
  product: Product;
  quantity: number;
}

export default function BrowseStock() {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [minPrice, setMinPrice] = useState<string>("");
  const [maxPrice, setMaxPrice] = useState<string>("");
  
  // Cart state
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showCartDialog, setShowCartDialog] = useState(false);
  const [buyerMessage, setBuyerMessage] = useState("");
  const [expectedDeliveryDate, setExpectedDeliveryDate] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    filterProducts();
  }, [products, searchTerm, categoryFilter, minPrice, maxPrice]);

  const fetchProducts = async () => {
    try {
      const data = await inventoryAPI.getAvailable();
      setProducts(data);
      setFilteredProducts(data);
    } catch (error) {
      console.error("Error fetching products:", error);
      toast.error("Failed to load products");
    } finally {
      setLoading(false);
    }
  };

  const filterProducts = () => {
    let filtered = [...products];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (p) =>
          p.product_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          p.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Category filter
    if (categoryFilter && categoryFilter !== "all") {
      filtered = filtered.filter((p) => p.category === categoryFilter);
    }

    // Price filters
    if (minPrice) {
      filtered = filtered.filter(
        (p) => p.price_per_unit >= parseFloat(minPrice)
      );
    }
    if (maxPrice) {
      filtered = filtered.filter(
        (p) => p.price_per_unit <= parseFloat(maxPrice)
      );
    }

    setFilteredProducts(filtered);
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      vegetables: "bg-green-100 text-green-800",
      fruits: "bg-red-100 text-red-800",
      grains: "bg-yellow-100 text-yellow-800",
      dairy: "bg-blue-100 text-blue-800",
      meat: "bg-orange-100 text-orange-800",
      other: "bg-gray-100 text-gray-800",
    };
    return colors[category] || colors.other;
  };

  const addToCart = (product: Product, quantity: number = 1) => {
    const existingItem = cart.find((item) => item.product._id === product._id);
    
    if (existingItem) {
      updateCartQuantity(product._id, existingItem.quantity + quantity);
    } else {
      setCart([...cart, { product, quantity }]);
      toast.success(`Added ${product.product_name} to cart`);
    }
  };

  const updateCartQuantity = (productId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    
    setCart(cart.map(item => 
      item.product._id === productId 
        ? { ...item, quantity: newQuantity }
        : item
    ));
  };

  const removeFromCart = (productId: string) => {
    setCart(cart.filter(item => item.product._id !== productId));
    toast.info("Item removed from cart");
  };

  const getCartTotal = () => {
    return cart.reduce((total, item) => total + (item.product.price_per_unit * item.quantity), 0);
  };

  const handlePlaceOrder = async () => {
    if (cart.length === 0) {
      toast.error("Cart is empty");
      return;
    }

    // Group cart items by farmer
    const itemsByFarmer: Record<string, CartItem[]> = {};
    cart.forEach(item => {
      if (!itemsByFarmer[item.product.farmer_id]) {
        itemsByFarmer[item.product.farmer_id] = [];
      }
      itemsByFarmer[item.product.farmer_id].push(item);
    });

    const farmerIds = Object.keys(itemsByFarmer);

    if (farmerIds.length > 1) {
      toast.error("Cannot create orders from multiple farmers at once. Please order from one farmer at a time.");
      return;
    }

    setSubmitting(true);
    try {
      const farmerId = farmerIds[0];
      const items = cart.map(item => ({
        inventory_id: item.product._id,
        quantity: item.quantity
      }));

      const orderData = {
        farmer_id: farmerId,
        items,
        buyer_message: buyerMessage || undefined,
        expected_delivery_date: expectedDeliveryDate || undefined
      };

      const response = await orderAPI.create(orderData);
      
      toast.success("Order placed successfully!");
      setCart([]);
      setBuyerMessage("");
      setExpectedDeliveryDate("");
      setShowCartDialog(false);
      
      // Navigate to buyer orders/contracts page
      navigate("/buyer/orders");
    } catch (error: any) {
      console.error("Error placing order:", error);
      toast.error(error.response?.data?.detail || "Failed to place order");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Browse Products</h1>
          <p className="text-muted-foreground">Fresh products from local farms</p>
        </div>
        
        {/* Cart Summary */}
        {cart.length > 0 && (
          <Button
            onClick={() => setShowCartDialog(true)}
            size="lg"
            className="relative"
          >
            <ShoppingCart className="mr-2 h-5 w-5" />
            View Cart ({cart.length})
            <Badge variant="destructive" className="absolute -top-2 -right-2">
              {cart.length}
            </Badge>
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Search</label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Category</label>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="vegetables">Vegetables</SelectItem>
                  <SelectItem value="fruits">Fruits</SelectItem>
                  <SelectItem value="grains">Grains</SelectItem>
                  <SelectItem value="dairy">Dairy</SelectItem>
                  <SelectItem value="meat">Meat</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Min Price (RON)</label>
              <Input
                type="number"
                step="0.01"
                placeholder="0.00"
                value={minPrice}
                onChange={(e) => setMinPrice(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Max Price (RON)</label>
              <Input
                type="number"
                step="0.01"
                placeholder="999.99"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {filteredProducts.length} of {products.length} products
        </p>
        {(searchTerm || categoryFilter !== "all" || minPrice || maxPrice) && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSearchTerm("");
              setCategoryFilter("all");
              setMinPrice("");
              setMaxPrice("");
            }}
          >
            Clear Filters
          </Button>
        )}
      </div>

      {/* Products Grid */}
      {filteredProducts.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Package className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-lg font-medium">No products found</p>
            <p className="text-sm text-muted-foreground">
              Try adjusting your filters or check back later
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredProducts.map((product) => (
            <Card
              key={product._id}
              className="flex flex-col hover:shadow-lg transition-shadow"
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-xl">
                      {product.product_name}
                    </CardTitle>
                    <div className="mt-1">
                      <Badge className={getCategoryColor(product.category)}>
                        {product.category}
                      </Badge>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-primary">
                      {product.price_per_unit} RON
                    </div>
                    <div className="text-xs text-muted-foreground">
                      per {product.unit}
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="flex-1 space-y-3">
                {product.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {product.description}
                  </p>
                )}

                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Available:</span>
                    <span className="font-medium">
                      {product.quantity} {product.unit}
                    </span>
                  </div>

                  {product.location && (
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <MapPin className="h-4 w-4" />
                      <span>{product.location}</span>
                    </div>
                  )}

                  {(product.min_order_quantity ||
                    product.max_order_quantity) && (
                    <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
                      {product.min_order_quantity && (
                        <span key="min">
                          Min: {product.min_order_quantity} {product.unit}
                        </span>
                      )}
                      {product.max_order_quantity && (
                        <span key="max">
                          Max: {product.max_order_quantity} {product.unit}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>

              <CardFooter>
                <Button
                  className="w-full"
                  onClick={() => addToCart(product, product.min_order_quantity || 1)}
                >
                  <ShoppingCart className="mr-2 h-4 w-4" />
                  Add to Cart
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Cart Dialog */}
      <Dialog open={showCartDialog} onOpenChange={setShowCartDialog}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Your Cart</DialogTitle>
            <DialogDescription>
              Review your items and place your order
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Cart Items */}
            {cart.map((item) => (
              <div key={item.product._id} className="flex items-center gap-4 p-4 border rounded-lg">
                <div className="flex-1">
                  <h4 className="font-medium">{item.product.product_name}</h4>
                  <p className="text-sm text-muted-foreground">
                    {item.product.price_per_unit} RON / {item.product.unit}
                  </p>
                </div>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => updateCartQuantity(item.product._id, item.quantity - 1)}
                  >
                    <Minus className="h-4 w-4" />
                  </Button>
                  
                  <Input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => updateCartQuantity(item.product._id, parseFloat(e.target.value) || 0)}
                    className="w-20 text-center"
                    min={item.product.min_order_quantity || 0}
                    max={item.product.max_order_quantity || item.product.quantity}
                  />
                  
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => updateCartQuantity(item.product._id, item.quantity + 1)}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                  
                  <span className="w-24 text-right font-medium">
                    {(item.product.price_per_unit * item.quantity).toFixed(2)} RON
                  </span>
                  
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFromCart(item.product._id)}
                  >
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              </div>
            ))}

            {/* Order Details */}
            <div className="space-y-4 pt-4 border-t">
              <div>
                <Label htmlFor="buyer-message">Message to Farmer (Optional)</Label>
                <Textarea
                  id="buyer-message"
                  placeholder="Any special requests or notes..."
                  value={buyerMessage}
                  onChange={(e) => setBuyerMessage(e.target.value)}
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="delivery-date">Expected Delivery Date (Optional)</Label>
                <Input
                  id="delivery-date"
                  type="date"
                  value={expectedDeliveryDate}
                  onChange={(e) => setExpectedDeliveryDate(e.target.value)}
                />
              </div>

              {/* Total */}
              <div className="flex items-center justify-between text-lg font-bold pt-4 border-t">
                <span>Total:</span>
                <span>{getCartTotal().toFixed(2)} RON</span>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCartDialog(false)}>
              Continue Shopping
            </Button>
            <Button onClick={handlePlaceOrder} disabled={submitting || cart.length === 0}>
              {submitting ? "Placing Order..." : "Place Order"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
