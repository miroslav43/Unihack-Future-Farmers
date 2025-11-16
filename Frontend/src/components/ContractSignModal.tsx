import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { contractAPI } from "@/lib/api";
import {
  AlertTriangle,
  CheckCircle,
  Copy,
  FileSignature,
  Key,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface ContractSignModalProps {
  contract: any;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ContractSignModal({
  contract,
  isOpen,
  onClose,
  onSuccess,
}: ContractSignModalProps) {
  const [step, setStep] = useState<"generate" | "sign">("generate");
  const [privateKey, setPrivateKey] = useState("");
  const [publicKey, setPublicKey] = useState("");
  const [signature, setSignature] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [copiedKey, setCopiedKey] = useState<"private" | "public" | null>(null);

  const handleGenerateKeys = async () => {
    try {
      setIsLoading(true);
      const keys = await contractAPI.generateKeys(contract._id);
      setPrivateKey(keys.private_key);
      setPublicKey(keys.public_key);
      toast.success("Keys generated successfully");
      setStep("sign");
    } catch (error) {
      console.error("Error generating keys:", error);
      toast.error("Failed to generate keys");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSign = async () => {
    if (!signature || !publicKey) {
      toast.error("Please provide signature and public key");
      return;
    }

    try {
      setIsLoading(true);
      await contractAPI.sign(contract._id, signature, publicKey);
      toast.success("Contract signed successfully!");
      onSuccess();
    } catch (error: any) {
      console.error("Error signing contract:", error);
      const message = error.response?.data?.detail || "Failed to sign contract";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string, type: "private" | "public") => {
    navigator.clipboard.writeText(text);
    setCopiedKey(type);
    toast.success(`${type === "private" ? "Private" : "Public"} key copied!`);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const signDataWithPrivateKey = async () => {
    if (!privateKey) {
      toast.error("Please generate keys first");
      return;
    }

    // In a real app, this would use Web Crypto API or a library
    // For demo, we'll use a simulated signature
    try {
      setIsLoading(true);

      // Simulate signing process
      const contractData = JSON.stringify({
        contract_hash: contract.contract_hash,
        timestamp: new Date().toISOString(),
      });

      // In production: Use proper RSA signing with the private key
      // For demo: Create a hash-based signature
      const encoder = new TextEncoder();
      const data = encoder.encode(contractData + privateKey.slice(0, 100));
      const hashBuffer = await crypto.subtle.digest("SHA-256", data);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");
      const simulatedSignature = btoa(hashHex);

      setSignature(simulatedSignature);
      toast.success("Contract signed with your private key");
    } catch (error) {
      console.error("Error signing:", error);
      toast.error("Failed to sign contract");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileSignature className="h-5 w-5" />
            Sign Contract
          </DialogTitle>
          <DialogDescription>
            Contract #{contract._id.slice(-6)} - Total: {contract.total_amount.toFixed(2)} RON
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {step === "generate" && (
            <>
              <Alert>
                <Key className="h-4 w-4" />
                <AlertDescription>
                  Generate a cryptographic key pair to sign this contract
                  securely. Your private key will be used to create a digital
                  signature.
                </AlertDescription>
              </Alert>

              <div className="space-y-2">
                <h3 className="font-semibold">Contract Details:</h3>
                <div className="bg-muted p-4 rounded-lg space-y-1 text-sm">
                  <p>
                    <strong>Buyer:</strong> {contract.buyer_name}
                  </p>
                  <p>
                    <strong>Farmer:</strong> {contract.farmer_name}
                  </p>
                  <p>
                    <strong>Items:</strong> {contract.items.length} product(s)
                  </p>
                  <p>
                    <strong>Total:</strong> {contract.total_amount.toFixed(2)} RON
                  </p>
                  <p className="font-mono text-xs mt-2 break-all">
                    <strong>Hash:</strong> {contract.contract_hash}
                  </p>
                </div>
              </div>

              <Button
                onClick={handleGenerateKeys}
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? "Generating..." : "Generate Signing Keys"}
              </Button>
            </>
          )}

          {step === "sign" && (
            <>
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <strong>IMPORTANT:</strong> Save your private key securely!
                  You'll need it to prove ownership. Never share it with anyone.
                </AlertDescription>
              </Alert>

              <div className="space-y-4">
                {/* Private Key */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <Label>Private Key (Keep Secret!)</Label>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(privateKey, "private")}
                    >
                      {copiedKey === "private" ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  <Textarea
                    value={privateKey}
                    readOnly
                    className="font-mono text-xs h-32 bg-red-50"
                  />
                </div>

                {/* Public Key */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <Label>Public Key</Label>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(publicKey, "public")}
                    >
                      {copiedKey === "public" ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                  <Textarea
                    value={publicKey}
                    readOnly
                    className="font-mono text-xs h-32 bg-green-50"
                  />
                </div>

                {/* Sign Button */}
                <Button
                  onClick={signDataWithPrivateKey}
                  disabled={isLoading || !!signature}
                  className="w-full"
                  variant="outline"
                >
                  {signature ? "Signed ✓" : "Sign with Private Key"}
                </Button>

                {/* Signature */}
                {signature && (
                  <div className="space-y-2">
                    <Label>Digital Signature</Label>
                    <Textarea
                      value={signature}
                      readOnly
                      className="font-mono text-xs h-24 bg-blue-50"
                    />
                  </div>
                )}

                {/* Submit */}
                <div className="flex gap-2 pt-4">
                  <Button
                    onClick={onClose}
                    variant="outline"
                    className="flex-1"
                    disabled={isLoading}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSign}
                    disabled={!signature || isLoading}
                    className="flex-1"
                  >
                    {isLoading ? "Submitting..." : "Submit Signature"}
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
