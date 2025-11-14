import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface KPICardProps {
  label: string;
  value: string | number;
  unit?: string;
  icon: LucideIcon;
  trend?: "up" | "down" | "stable";
  status?: "normal" | "warning" | "danger";
}

export default function KPICard({ label, value, unit, icon: Icon, status = "normal" }: KPICardProps) {
  return (
    <Card className={cn(
      "group hover:shadow-premium transition-all duration-300 hover:-translate-y-1 border-border/50 bg-gradient-to-br from-card to-card/50 backdrop-blur-sm overflow-hidden relative",
      status === "warning" && "border-warning/40",
      status === "danger" && "border-destructive/40"
    )}>
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      <CardContent className="p-4 sm:p-6 relative">
        <div className="flex items-start justify-between">
          <div className="space-y-3 flex-1">
            <p className="text-xs sm:text-sm font-medium text-muted-foreground tracking-wide uppercase">{label}</p>
            <div className="flex items-baseline gap-1 sm:gap-2">
              <span className="text-2xl sm:text-4xl font-bold tracking-tight">{value}</span>
              {unit && <span className="text-lg sm:text-xl text-muted-foreground font-medium">{unit}</span>}
            </div>
          </div>
          <div className={cn(
            "rounded-xl p-2 sm:p-3 transition-all duration-300 group-hover:scale-110",
            status === "normal" && "bg-primary/10 text-primary group-hover:bg-primary/20 shadow-sm",
            status === "warning" && "bg-warning/10 text-warning group-hover:bg-warning/20 shadow-sm",
            status === "danger" && "bg-destructive/10 text-destructive group-hover:bg-destructive/20 shadow-sm"
          )}>
            <Icon className="h-5 w-5 sm:h-6 sm:w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
