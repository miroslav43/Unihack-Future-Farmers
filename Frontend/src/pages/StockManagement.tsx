import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
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
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { farmerAPI, inventoryAPI } from "@/lib/api";
import {
  AlertCircle,
  DollarSign,
  Edit,
  Package,
  Plus,
  Search,
  Trash2,
  TrendingUp,
} from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

interface InventoryItem {
  _id: string;
  product_name: string;
  category: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  total_value: number;
  is_available_for_sale: boolean;
  location?: string;
  description?: string;
  min_order_quantity?: number;
  max_order_quantity?: number;
}

interface Statistics {
  total_items: number;
  total_value: number;
  available_for_sale: number;
  low_stock_items: Array<{ product_name: string; quantity: number }>;
}

export default function StockManagement() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<InventoryItem | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    product_name: "",
    category: "vegetables",
    quantity: 0,
    unit: "kg",
    price_per_unit: 0,
    location: "",
    description: "",
    is_available_for_sale: false,
    min_order_quantity: 0,
    max_order_quantity: 0,
  });

  useEffect(() => {
    fetchFarmerAndInventory();
  }, []);

  const fetchFarmerAndInventory = async () => {
    try {
      // Get farmer profile first
      const farmerProfile = await farmerAPI.getMyProfile();

      // Then get inventory for this farmer
      const data = await inventoryAPI.getByFarmer(farmerProfile.id);
      setItems(data);

      // Calculate statistics client-side
      const totalItems = data.length;
      const totalValue = data.reduce(
        (sum: number, item: any) =>
          sum + parseFloat(item.quantity) * parseFloat(item.price_per_unit),
        0
      );
      const availableItems = data.filter(
        (item: any) => item.is_available_for_sale
      ).length;
      const lowStockItems = data.filter(
        (item: any) => parseFloat(item.quantity) < 10
      ).length;

      setStatistics({
        total_items: totalItems,
        total_value: totalValue,
        available_for_sale: availableItems,
        low_stock_items: [],
      });
    } catch (error: any) {
      console.error("Error fetching inventory:", error);
      if (error?.response?.status === 404) {
        toast.error("Please create your farmer profile first!", {
          action: {
            label: "Create Profile",
            onClick: () => (window.location.href = "/farmer/profile-setup"),
          },
        });
      } else {
        toast.error("Failed to load inventory");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (editingItem) {
        await inventoryAPI.update(editingItem._id, formData);
        toast.success("Item updated successfully!");
      } else {
        // Mock farmer ID
        await inventoryAPI.create({
          ...formData,
          farmer_id: "current-farmer-id",
        });
        toast.success("Item created successfully!");
      }

      fetchFarmerAndInventory();
      handleCloseDialog();
    } catch (error) {
      console.error("Error saving item:", error);
      toast.error("Failed to save item");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this item?")) return;

    try {
      await inventoryAPI.delete(id);
      toast.success("Item deleted successfully!");
      fetchFarmerAndInventory();
    } catch (error) {
      console.error("Error deleting item:", error);
      toast.error("Failed to delete item");
    }
  };

  const handleEdit = (item: InventoryItem) => {
    setEditingItem(item);
    setFormData({
      product_name: item.product_name,
      category: item.category,
      quantity: item.quantity,
      unit: item.unit,
      price_per_unit: item.price_per_unit,
      location: item.location || "",
      description: item.description || "",
      is_available_for_sale: item.is_available_for_sale,
      min_order_quantity: item.min_order_quantity,
      max_order_quantity: item.max_order_quantity,
    });
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    setEditingItem(null);
    setFormData({
      product_name: "",
      category: "vegetables",
      quantity: 0,
      unit: "kg",
      price_per_unit: 0,
      location: "",
      description: "",
      is_available_for_sale: false,
      min_order_quantity: undefined,
      max_order_quantity: undefined,
    });
  };

  const filteredItems = items.filter((item) =>
    item.product_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Stock Management</h1>
          <p className="text-muted-foreground">
            Manage your farm inventory and products
          </p>
        </div>

        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditingItem(null)}>
              <Plus className="mr-2 h-4 w-4" />
              Add Product
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingItem ? "Edit Product" : "Add New Product"}
              </DialogTitle>
              <DialogDescription>
                {editingItem ? "Update" : "Add"} your inventory item details
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="product_name">Product Name</Label>
                  <Input
                    id="product_name"
                    value={formData.product_name}
                    onChange={(e) =>
                      setFormData({ ...formData, product_name: e.target.value })
                    }
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value) =>
                      setFormData({ ...formData, category: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
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
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    type="number"
                    step="0.01"
                    value={formData.quantity}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        quantity: parseFloat(e.target.value),
                      })
                    }
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="unit">Unit</Label>
                  <Input
                    id="unit"
                    value={formData.unit}
                    onChange={(e) =>
                      setFormData({ ...formData, unit: e.target.value })
                    }
                    placeholder="kg, tone, bucăți"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="price_per_unit">Price per Unit</Label>
                  <Input
                    id="price_per_unit"
                    type="number"
                    step="0.01"
                    value={formData.price_per_unit}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        price_per_unit: parseFloat(e.target.value),
                      })
                    }
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    value={formData.location}
                    onChange={(e) =>
                      setFormData({ ...formData, location: e.target.value })
                    }
                    placeholder="Depozit, Câmp A"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  placeholder="Product details..."
                  rows={3}
                />
              </div>

              <div className="flex items-center space-x-2 rounded-lg border p-4">
                <Switch
                  id="available"
                  checked={formData.is_available_for_sale}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, is_available_for_sale: checked })
                  }
                />
                <Label htmlFor="available" className="cursor-pointer">
                  Available for buyers to purchase
                </Label>
              </div>

              {formData.is_available_for_sale && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="min_order">Min Order Quantity</Label>
                    <Input
                      id="min_order"
                      type="number"
                      step="0.01"
                      value={formData.min_order_quantity || ""}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          min_order_quantity: e.target.value
                            ? parseFloat(e.target.value)
                            : undefined,
                        })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="max_order">Max Order Quantity</Label>
                    <Input
                      id="max_order"
                      type="number"
                      step="0.01"
                      value={formData.max_order_quantity || ""}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          max_order_quantity: e.target.value
                            ? parseFloat(e.target.value)
                            : undefined,
                        })
                      }
                    />
                  </div>
                </div>
              )}

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleCloseDialog}
                >
                  Cancel
                </Button>
                <Button type="submit">
                  {editingItem ? "Update" : "Create"} Product
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Products
              </CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics?.total_items || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Value</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics?.total_value?.toFixed(2) || "0.00"} RON
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Available for Sale
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics?.available_for_sale || 0}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Low Stock</CardTitle>
              <AlertCircle className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {statistics?.low_stock_items?.length || 0}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Inventory Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Inventory Items</CardTitle>
              <CardDescription>View and manage your stock</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Search className="h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Price/Unit</TableHead>
                <TableHead>Total Value</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredItems.map((item) => (
                <TableRow key={item._id}>
                  <TableCell className="font-medium">
                    {item.product_name}
                  </TableCell>
                  <TableCell className="capitalize">{item.category}</TableCell>
                  <TableCell>
                    {item.quantity} {item.unit}
                    {item.quantity < 10 && (
                      <Badge variant="destructive" className="ml-2">
                        Low
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>{item.price_per_unit} RON</TableCell>
                  <TableCell>{item.total_value.toFixed(2)} RON</TableCell>
                  <TableCell>{item.location || "-"}</TableCell>
                  <TableCell>
                    {item.is_available_for_sale ? (
                      <Badge variant="default">For Sale</Badge>
                    ) : (
                      <Badge variant="secondary">Internal</Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEdit(item)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(item._id)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {filteredItems.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={8}
                    className="text-center py-8 text-muted-foreground"
                  >
                    {searchTerm
                      ? "No products found"
                      : "No inventory items yet. Add your first product!"}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
