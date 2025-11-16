import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { farmerAPI } from "@/lib/api";
import { Tractor, X } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export default function FarmerProfileSetup() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [certifications, setCertifications] = useState<string[]>([]);
  const [certInput, setCertInput] = useState("");

  const [formData, setFormData] = useState({
    farm_name: "",
    contact_person: "",
    phone: "",
    email: "",
    address: "",
    city: "",
    county: "",
    postal_code: "",
    farm_size_hectares: "",
  });

  const addCertification = () => {
    if (certInput.trim() && !certifications.includes(certInput.trim())) {
      setCertifications([...certifications, certInput.trim()]);
      setCertInput("");
    }
  };

  const removeCertification = (cert: string) => {
    setCertifications(certifications.filter((c) => c !== cert));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const data = {
        ...formData,
        farm_size_hectares: formData.farm_size_hectares
          ? parseFloat(formData.farm_size_hectares)
          : undefined,
        certifications: certifications.length > 0 ? certifications : undefined,
      };

      await farmerAPI.createProfile(data);
      toast.success("Farm profile created successfully!");
      navigate("/");
    } catch (error: any) {
      console.error("Error creating profile:", error);
      const message =
        error.response?.data?.detail || "Failed to create profile";
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center gradient-subtle p-4">
      <Card className="max-w-2xl w-full">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
            <Tractor className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-2xl">Complete Your Farm Profile</CardTitle>
          <CardDescription>
            Tell us about your farm to start selling to local businesses
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="farm_name">Farm Name *</Label>
                <Input
                  id="farm_name"
                  value={formData.farm_name}
                  onChange={(e) =>
                    setFormData({ ...formData, farm_name: e.target.value })
                  }
                  placeholder="Green Valley Farm"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="contact_person">Contact Person *</Label>
                <Input
                  id="contact_person"
                  value={formData.contact_person}
                  onChange={(e) =>
                    setFormData({ ...formData, contact_person: e.target.value })
                  }
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone *</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) =>
                    setFormData({ ...formData, phone: e.target.value })
                  }
                  placeholder="+40 123 456 789"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="farm_size_hectares">Farm Size (hectares)</Label>
                <Input
                  id="farm_size_hectares"
                  type="number"
                  step="0.1"
                  value={formData.farm_size_hectares}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      farm_size_hectares: e.target.value,
                    })
                  }
                  placeholder="50.5"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Address *</Label>
              <Textarea
                id="address"
                value={formData.address}
                onChange={(e) =>
                  setFormData({ ...formData, address: e.target.value })
                }
                rows={2}
                required
              />
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="city">City *</Label>
                <Input
                  id="city"
                  value={formData.city}
                  onChange={(e) =>
                    setFormData({ ...formData, city: e.target.value })
                  }
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="county">County *</Label>
                <Input
                  id="county"
                  value={formData.county}
                  onChange={(e) =>
                    setFormData({ ...formData, county: e.target.value })
                  }
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="postal_code">Postal Code</Label>
                <Input
                  id="postal_code"
                  value={formData.postal_code}
                  onChange={(e) =>
                    setFormData({ ...formData, postal_code: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="certifications">Certifications</Label>
              <div className="flex gap-2">
                <Input
                  id="certifications"
                  value={certInput}
                  onChange={(e) => setCertInput(e.target.value)}
                  placeholder="e.g., BIO, EU Organic"
                  onKeyPress={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      addCertification();
                    }
                  }}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={addCertification}
                >
                  Add
                </Button>
              </div>
              {certifications.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {certifications.map((cert) => (
                    <Badge key={cert} variant="secondary" className="gap-1">
                      {cert}
                      <X
                        className="h-3 w-3 cursor-pointer"
                        onClick={() => removeCertification(cert)}
                      />
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={() => navigate("/")}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" className="flex-1" disabled={isSubmitting}>
                {isSubmitting ? "Creating..." : "Create Farm Profile"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
