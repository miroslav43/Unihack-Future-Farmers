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
import { contractAPI } from "@/lib/api";
import { format } from "date-fns";
import {
  AlertCircle,
  CheckCircle,
  Clock,
  ExternalLink,
  FileText,
  Package,
  Truck,
  XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function MyContracts() {
  const [contracts, setContracts] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedContract, setSelectedContract] = useState<any | null>(null);
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

  const filterContracts = (group: string) => {
    switch (group) {
      case "needsSignature":
        return contracts.filter((c: any) => 
          (c.status === "pending" || c.status === "signed_farmer") && !c.buyer_signature
        );
      case "active":
        return contracts.filter((c: any) => c.status === "active");
      case "completed":
        return contracts.filter((c: any) => c.status === "completed");
      default:
        return contracts;
    }
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      pending: (
        <Badge variant="outline" className="bg-yellow-50">
          <Clock className="h-3 w-3 mr-1" />
          Pending Farmer
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
          <Truck className="h-3 w-3 mr-1" />
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

  const getStatusMessage = (contract: any) => {
    if (contract.status === "pending" && !contract.farmer_signature) {
      return "Waiting for farmer to sign the contract";
    }
    if (contract.status === "pending" || (contract.status === "signed_farmer" && !contract.buyer_signature)) {
      return "Farmer has signed. Click 'Sign Contract' to proceed";
    }
    if (contract.status === "active") {
      return "Contract is active. Order in progress";
    }
    if (contract.status === "completed") {
      return "Order completed successfully";
    }
    if (contract.status === "rejected") {
      return "Farmer rejected this contract";
    }
    return "";
  };

  const needsMySignature = (contract: any) => {
    return (contract.status === "pending" || contract.status === "signed_farmer") && 
           contract.farmer_signature && 
           !contract.buyer_signature;
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
              Farmer: {contract.farmer_name}
            </CardDescription>
          </div>
          {getStatusBadge(contract.status)}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Status Message */}
          <div className="bg-muted p-3 rounded-lg">
            <p className="text-sm">{getStatusMessage(contract)}</p>
          </div>

          {/* Items */}
          <div>
            <p className="text-sm font-medium mb-2 flex items-center gap-1">
              <Package className="h-4 w-4" />
              Items ({contract.items.length})
            </p>
            <div className="space-y-1 pl-5">
              {contract.items.map((item: any, idx: number) => (
                <div
                  key={idx}
                  className="text-sm text-muted-foreground flex justify-between"
                >
                  <span>
                    {item.product_name} - {item.quantity} {item.unit}
                  </span>
                  <span className="font-medium">
                    {item.total ? item.total.toFixed(2) : (item.price_per_unit * item.quantity).toFixed(2)} RON
                  </span>
                </div>
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

          {/* Delivery Info */}
          {contract.delivery_address && (
            <div className="text-sm">
              <p className="font-medium">Delivery Address:</p>
              <p className="text-muted-foreground">
                {contract.delivery_address}
              </p>
            </div>
          )}

          {/* Dates */}
          <div className="text-sm text-muted-foreground space-y-1">
            <p>Created: {format(new Date(contract.created_at), "PPP")}</p>
            {contract.delivery_date && (
              <p>
                Expected Delivery:{" "}
                {format(new Date(contract.delivery_date), "PPP")}
              </p>
            )}
            {contract.signed_at && (
              <p>Signed: {format(new Date(contract.signed_at), "PPP")}</p>
            )}
          </div>

          {/* Signatures */}
          {(contract.farmer_signature || contract.buyer_signature) && (
            <div className="space-y-2 pt-2 border-t">
              <p className="text-sm font-medium">Signatures:</p>
              {contract.farmer_signature && (
                <div className="flex items-center gap-2 text-xs text-green-700 bg-green-50 p-2 rounded">
                  <CheckCircle className="h-3 w-3" />
                  <span>
                    Farmer signed on{" "}
                    {format(
                      new Date(contract.farmer_signature.signed_at),
                      "PPP"
                    )}
                  </span>
                </div>
              )}
              {contract.buyer_signature && (
                <div className="flex items-center gap-2 text-xs text-blue-700 bg-blue-50 p-2 rounded">
                  <CheckCircle className="h-3 w-3" />
                  <span>
                    You signed on{" "}
                    {format(
                      new Date(contract.buyer_signature.signed_at),
                      "PPP"
                    )}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Blockchain TX */}
          {contract.blockchain_tx_id && (
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">
                Blockchain Transaction:
              </p>
              <div className="flex items-center gap-2 text-xs bg-muted p-2 rounded">
                <ExternalLink className="h-3 w-3" />
                <span className="font-mono truncate">
                  {contract.blockchain_tx_id}
                </span>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            {needsMySignature(contract) && (
              <Button
                onClick={() => handleSign(contract)}
                className="flex-1"
                size="sm"
              >
                <CheckCircle className="h-4 w-4 mr-1" />
                Sign Contract
              </Button>
            )}
            {!needsMySignature(contract) && (
              <Button variant="outline" className="flex-1" size="sm">
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
          <p className="mt-4 text-muted-foreground">
            Loading your contracts...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">My Contracts</h1>
        <p className="text-muted-foreground mt-1">
          Track your orders and blockchain contracts
        </p>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="all" className="w-full">
        <TabsList>
          <TabsTrigger value="all">All ({contracts.length})</TabsTrigger>
          <TabsTrigger value="needsSignature">
            Needs Signature ({filterContracts("needsSignature").length})
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
            contracts.map((contract: any) => (
              <ContractCard key={contract._id} contract={contract} />
            ))
          )}
        </TabsContent>

        <TabsContent value="needsSignature" className="space-y-4">
          {filterContracts("needsSignature").length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <CheckCircle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">All contracts signed</p>
              </CardContent>
            </Card>
          ) : (
            filterContracts("needsSignature").map((contract: any) => (
              <ContractCard key={contract._id} contract={contract} />
            ))
          )}
        </TabsContent>

        <TabsContent value="active" className="space-y-4">
          {filterContracts("active").map((contract: any) => (
            <ContractCard key={contract._id} contract={contract} />
          ))}
        </TabsContent>

        <TabsContent value="completed" className="space-y-4">
          {filterContracts("completed").map((contract: any) => (
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
