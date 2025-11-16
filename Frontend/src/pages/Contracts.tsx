import ContractSignModal from "@/components/ContractSignModal";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/contexts/SimpleAuthContext";
import { contractAPI } from "@/lib/api";
import { format } from "date-fns";
import {
  AlertCircle,
  CheckCircle,
  Clock,
  ExternalLink,
  FileText,
  Package,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function Contracts() {
  const { user } = useAuth();
  const [contracts, setContracts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedContract, setSelectedContract] = useState<any | null>(
    null
  );
  const [isSignModalOpen, setIsSignModalOpen] = useState(false);

  useEffect(() => {
    loadContracts();
  }, []);

  const loadContracts = async () => {
    try {
      setIsLoading(true);
      const data = await contractAPI.getAll();
      setContracts(data);
    } catch (error) {
      console.error("Error loading contracts:", error);
      toast.error("Failed to load contracts");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSign = (contract: any) => {
    setSelectedContract(contract);
    setIsSignModalOpen(true);
  };

  const handleReject = async (contractId: string) => {
    if (!confirm("Are you sure you want to reject this contract?")) return;

    try {
      await contractAPI.reject(contractId);
      toast.success("Contract rejected");
      loadContracts();
    } catch (error) {
      console.error("Error rejecting contract:", error);
      toast.error("Failed to reject contract");
    }
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: (
        <Badge variant="outline" className="bg-yellow-50">
          <Clock className="h-3 w-3 mr-1" />
          Pending
        </Badge>
      ),
      signed_farmer: (
        <Badge variant="outline" className="bg-blue-50">
          <AlertCircle className="h-3 w-3 mr-1" />
          Farmer Signed
        </Badge>
      ),
      active: (
        <Badge variant="outline" className="bg-green-50">
          <CheckCircle className="h-3 w-3 mr-1" />
          Active
        </Badge>
      ),
      completed: (
        <Badge variant="outline" className="bg-gray-50">
          <CheckCircle className="h-3 w-3 mr-1" />
          Completed
        </Badge>
      ),
      rejected: (
        <Badge variant="destructive">
          <XCircle className="h-3 w-3 mr-1" />
          Rejected
        </Badge>
      ),
      cancelled: (
        <Badge variant="outline">
          <XCircle className="h-3 w-3 mr-1" />
          Cancelled
        </Badge>
      ),
    };
    return badges[status] || <Badge>{status}</Badge>;
  };

  const filterContracts = (status?: string) => {
    if (!status) return contracts;
    return contracts.filter((c: any) => c.status === status);
  };

  const ContractCard = ({ contract }: { contract: any }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Contract #{contract._id.slice(-6)}
            </CardTitle>
            <CardDescription className="mt-1">
              Buyer: {contract.buyer_name}
            </CardDescription>
          </div>
          {getStatusBadge(contract.status)}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Items */}
          <div>
            <p className="text-sm font-medium mb-2 flex items-center gap-1">
              <Package className="h-4 w-4" />
              Items ({contract.items.length})
            </p>
            <div className="space-y-1 pl-5">
              {contract.items.map((item: any, idx: number) => (
                <p key={idx} className="text-sm text-muted-foreground">
                  {item.product_name} - {item.quantity} {item.unit} @ {item.price_per_unit} RON
                </p>
              ))}
            </div>
          </div>

          {/* Total */}
          <div className="flex justify-between items-center pt-2 border-t">
            <span className="font-semibold">Total Amount:</span>
            <span className="text-lg font-bold text-primary">
              {contract.total_amount.toFixed(2)} RON
            </span>
          </div>

          {/* Dates */}
          <div className="text-sm text-muted-foreground space-y-1">
            <p>Created: {format(new Date(contract.created_at), "PPP")}</p>
            {contract.delivery_date && (
              <p>Delivery: {format(new Date(contract.delivery_date), "PPP")}</p>
            )}
          </div>

          {/* Blockchain TX */}
          {contract.blockchain_tx_id && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted p-2 rounded">
              <ExternalLink className="h-3 w-3" />
              <span className="font-mono">{contract.blockchain_tx_id}</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            {contract.status === "pending" && (
              <>
                <Button
                  onClick={() => handleSign(contract)}
                  className="flex-1"
                  size="sm"
                >
                  <CheckCircle className="h-4 w-4 mr-1" />
                  Sign Contract
                </Button>
                <Button
                  onClick={() => handleReject(contract._id)}
                  variant="destructive"
                  className="flex-1"
                  size="sm"
                >
                  <XCircle className="h-4 w-4 mr-1" />
                  Reject
                </Button>
              </>
            )}
            {contract.status === "signed_farmer" && (
              <Button disabled className="w-full" size="sm">
                Waiting for buyer signature...
              </Button>
            )}
            {contract.status === "active" && (
              <Button variant="outline" className="w-full" size="sm">
                View Details
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading contracts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Contracts</h1>
        <p className="text-muted-foreground mt-1">
          Manage your blockchain-secured contracts
        </p>
      </div>

      <Tabs defaultValue="all" className="w-full">
        <TabsList>
          <TabsTrigger value="all">All ({contracts.length})</TabsTrigger>
          <TabsTrigger value="pending">
            Pending ({filterContracts("pending").length})
          </TabsTrigger>
          <TabsTrigger value="active">
            Active ({filterContracts("active").length})
          </TabsTrigger>
          <TabsTrigger value="completed">
            Completed ({filterContracts("completed").length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {contracts.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No contracts yet</p>
              </CardContent>
            </Card>
          ) : (
            contracts.map((contract) => (
              <ContractCard key={contract._id} contract={contract} />
            ))
          )}
        </TabsContent>

        <TabsContent value="pending" className="space-y-4">
          {filterContracts("pending").map((contract) => (
            <ContractCard key={contract._id} contract={contract} />
          ))}
        </TabsContent>

        <TabsContent value="active" className="space-y-4">
          {filterContracts("active").map((contract) => (
            <ContractCard key={contract._id} contract={contract} />
          ))}
        </TabsContent>

        <TabsContent value="completed" className="space-y-4">
          {filterContracts("completed").map((contract) => (
            <ContractCard key={contract._id} contract={contract} />
          ))}
        </TabsContent>
      </Tabs>

      {/* Sign Modal */}
      {selectedContract && (
        <ContractSignModal
          contract={selectedContract}
          isOpen={isSignModalOpen}
          onClose={() => {
            setIsSignModalOpen(false);
            setSelectedContract(null);
          }}
          onSuccess={() => {
            loadContracts();
            setIsSignModalOpen(false);
            setSelectedContract(null);
          }}
        />
      )}
    </div>
  );
}
