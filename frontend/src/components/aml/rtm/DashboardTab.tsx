import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";

// Mock data for rule evaluations in last 24h
const mockEvaluations = [
  {
    transaction_id: "TXN-001",
    rule_id: "950fca9a-4aa9-4bda-a388-0af5f343f397",
    rule_statement: "Financial institutions must obtain written authorisation from MAS",
    conditions_met: false,
    confidence_score: 0.85,
    reasoning: "Transaction lacks proper MAS authorization documentation",
    suggested_action: "enhanced due diligence",
    evaluated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
  },
  {
    transaction_id: "TXN-002",
    rule_id: "950fca9a-4aa9-4bda-a388-0af5f343f398",
    rule_statement: "Applicants must satisfy MAS admission criteria",
    conditions_met: false,
    confidence_score: 0.92,
    reasoning: "High risk indicators detected in transaction pattern",
    suggested_action: "transaction blocking",
    evaluated_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString()
  },
  {
    transaction_id: "TXN-003",
    rule_id: "950fca9a-4aa9-4bda-a388-0af5f343f399",
    rule_statement: "Payment must include proper reference codes",
    conditions_met: false,
    confidence_score: 0.78,
    reasoning: "Missing UEN reference in payment details",
    suggested_action: "escalation",
    evaluated_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString()
  }
];

const DashboardTab = () => {
  const [evaluations] = useState(mockEvaluations);

  const getActionBadgeVariant = (action: string) => {
    switch (action) {
      case "transaction blocking":
        return "destructive";
      case "escalation":
        return "default";
      case "enhanced due diligence":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Dashboard - Recent Flagged Actions</CardTitle>
        <CardDescription>
          Displaying actions flagged in the last 24 hours requiring attention
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Transaction ID</TableHead>
              <TableHead>Rule Statement</TableHead>
              <TableHead>Confidence</TableHead>
              <TableHead>Reasoning</TableHead>
              <TableHead>Suggested Action</TableHead>
              <TableHead>Evaluated At</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {evaluations.map((evaluation) => (
              <TableRow key={evaluation.transaction_id}>
                <TableCell className="font-medium">{evaluation.transaction_id}</TableCell>
                <TableCell className="max-w-xs truncate">{evaluation.rule_statement}</TableCell>
                <TableCell>{(evaluation.confidence_score * 100).toFixed(0)}%</TableCell>
                <TableCell className="max-w-xs truncate">{evaluation.reasoning}</TableCell>
                <TableCell>
                  <Badge variant={getActionBadgeVariant(evaluation.suggested_action)}>
                    {evaluation.suggested_action}
                  </Badge>
                </TableCell>
                <TableCell>{new Date(evaluation.evaluated_at).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};

export default DashboardTab;
