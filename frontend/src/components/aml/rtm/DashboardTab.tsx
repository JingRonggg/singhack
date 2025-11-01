import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import {
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  TrendingUp,
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface DashboardStats {
  total_transactions: number;
  transactions_requiring_action: number;
  total_rule_violations: number;
  total_rules: number;
}

interface Transaction {
  transaction_id: string;
  booking_datetime: string;
  amount: number;
  currency: string;
  originator_name: string;
  beneficiary_name: string;
  originator_country?: string;
  beneficiary_country?: string;
  batch_evaluations?: Array<{
    total_rules_evaluated: number;
    violated_rules_count: number;
    passed_rules_count: number;
    overall_risk_level: string;
    requires_action: boolean;
  }>;
}

const DashboardTab = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [highRiskTransactions, setHighRiskTransactions] = useState<
    Transaction[]
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  // Fetch all dashboard data
  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch stats
      const statsResponse = await fetch(
        "http://localhost:8000/api/dashboard/stats"
      );
      if (!statsResponse.ok) throw new Error("Failed to fetch stats");
      const statsData = await statsResponse.json();
      setStats(statsData);

      // Fetch recent transactions requiring action
      const txnsResponse = await fetch(
        "http://localhost:8000/api/dashboard/transactions/requires-action?limit=10"
      );
      if (!txnsResponse.ok) throw new Error("Failed to fetch transactions");
      const txnsData = await txnsResponse.json();
      setTransactions(txnsData.transactions || []);

      // Fetch high-risk transactions
      const highRiskResponse = await fetch(
        "http://localhost:8000/api/dashboard/transactions/high-risk?limit=5"
      );
      if (!highRiskResponse.ok)
        throw new Error("Failed to fetch high-risk transactions");
      const highRiskData = await highRiskResponse.json();
      setHighRiskTransactions(highRiskData.transactions || []);

      toast({
        title: "Dashboard Refreshed",
        description: "Successfully loaded latest data",
      });
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard data");
      toast({
        title: "Error",
        description: err.message || "Failed to load dashboard data",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Load data on mount
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const getRiskBadgeVariant = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case "high":
        return "destructive";
      case "medium":
        return "default";
      case "low":
        return "secondary";
      default:
        return "outline";
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency || "USD",
    }).format(amount);
  };

  const formatDateTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="space-y-6">
      {/* Header with Refresh Button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            AML Monitoring Dashboard
          </h2>
          <p className="text-muted-foreground">
            Real-time overview of transaction monitoring and compliance
          </p>
        </div>
        <Button
          onClick={fetchDashboardData}
          disabled={isLoading}
          variant="outline"
        >
          <RefreshCw
            className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Transactions
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.total_transactions}
              </div>
              <p className="text-xs text-muted-foreground">
                Processed in system
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Requires Action
              </CardTitle>
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">
                {stats.transactions_requiring_action}
              </div>
              <p className="text-xs text-muted-foreground">
                Needs immediate review
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Rule Violations
              </CardTitle>
              <XCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {stats.total_rule_violations}
              </div>
              <p className="text-xs text-muted-foreground">
                Total violations detected
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Active Rules
              </CardTitle>
              <CheckCircle2 className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_rules}</div>
              <p className="text-xs text-muted-foreground">
                Compliance rules loaded
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* High Risk Transactions */}
      <Card>
        <CardHeader>
          <CardTitle>High Risk Transactions</CardTitle>
          <CardDescription>
            Transactions flagged with high risk requiring immediate attention
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && highRiskTransactions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading high-risk transactions...
            </div>
          ) : highRiskTransactions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No high-risk transactions found
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Transaction ID</TableHead>
                  <TableHead>Date/Time</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>From → To</TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead>Violations</TableHead>
                  <TableHead>Action Required</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {highRiskTransactions.map((txn) => {
                  const evaluation = txn.batch_evaluations?.[0];
                  return (
                    <TableRow key={txn.transaction_id}>
                      <TableCell className="font-mono text-xs">
                        {txn.transaction_id.substring(0, 8)}...
                      </TableCell>
                      <TableCell className="text-sm">
                        {formatDateTime(txn.booking_datetime)}
                      </TableCell>
                      <TableCell className="font-semibold">
                        {formatCurrency(txn.amount, txn.currency)}
                      </TableCell>
                      <TableCell className="text-sm">
                        <div className="flex flex-col">
                          <span
                            className="truncate max-w-[150px]"
                            title={txn.originator_name}
                          >
                            {txn.originator_name}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            ↓
                          </span>
                          <span
                            className="truncate max-w-[150px]"
                            title={txn.beneficiary_name}
                          >
                            {txn.beneficiary_name}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={getRiskBadgeVariant(
                            evaluation?.overall_risk_level || ""
                          )}
                        >
                          {evaluation?.overall_risk_level?.toUpperCase() ||
                            "N/A"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-red-600 font-semibold">
                            {evaluation?.violated_rules_count || 0}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            / {evaluation?.total_rules_evaluated || 0}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {evaluation?.requires_action ? (
                          <Badge variant="destructive">Yes</Badge>
                        ) : (
                          <Badge variant="outline">No</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Transactions Requiring Action */}
      <Card>
        <CardHeader>
          <CardTitle>Transactions Requiring Action</CardTitle>
          <CardDescription>
            Recent transactions that need compliance review
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && transactions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading transactions...
            </div>
          ) : transactions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No transactions requiring action
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Transaction ID</TableHead>
                  <TableHead>Date/Time</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Originator</TableHead>
                  <TableHead>Beneficiary</TableHead>
                  <TableHead>Risk Level</TableHead>
                  <TableHead>Rules Evaluated</TableHead>
                  <TableHead>Violations</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((txn) => {
                  const evaluation = txn.batch_evaluations?.[0];
                  return (
                    <TableRow key={txn.transaction_id}>
                      <TableCell className="font-mono text-xs">
                        {txn.transaction_id.substring(0, 8)}...
                      </TableCell>
                      <TableCell className="text-sm">
                        {formatDateTime(txn.booking_datetime)}
                      </TableCell>
                      <TableCell className="font-semibold">
                        {formatCurrency(txn.amount, txn.currency)}
                      </TableCell>
                      <TableCell
                        className="max-w-[150px] truncate"
                        title={txn.originator_name}
                      >
                        {txn.originator_name}
                      </TableCell>
                      <TableCell
                        className="max-w-[150px] truncate"
                        title={txn.beneficiary_name}
                      >
                        {txn.beneficiary_name}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={getRiskBadgeVariant(
                            evaluation?.overall_risk_level || ""
                          )}
                        >
                          {evaluation?.overall_risk_level?.toUpperCase() ||
                            "N/A"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {evaluation?.total_rules_evaluated || 0}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Badge
                            variant={
                              evaluation?.violated_rules_count
                                ? "destructive"
                                : "secondary"
                            }
                          >
                            {evaluation?.violated_rules_count || 0}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            ({evaluation?.passed_rules_count || 0} passed)
                          </span>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardTab;
