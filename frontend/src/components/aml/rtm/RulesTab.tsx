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
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";
import { Trash2, Edit, RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface Rule {
  rule_id: string;
  statement: string;
  jurisdiction: string[];
  source_url: string;
  suggested_action: string;
  created_at?: string;
}

const RulesTab = () => {
  const [rules, setRules] = useState<Rule[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  // Fetch rules from backend
  const fetchRules = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        "http://localhost:8000/api/dashboard/rules?limit=100"
      );

      if (!response.ok) {
        throw new Error("Failed to fetch rules");
      }

      const data = await response.json();
      setRules(data.rules || []);

      toast({
        title: "Rules Loaded",
        description: `Successfully loaded ${data.total} rules`,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to load rules";
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Load rules on component mount
  useEffect(() => {
    fetchRules();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDelete = (ruleId: string) => {
    // TODO: Implement DELETE endpoint in backend
    setRules(rules.filter((rule) => rule.rule_id !== ruleId));
    toast({
      title: "Rule Deleted",
      description: `Rule ${ruleId} has been removed (local only - backend delete not implemented)`,
      variant: "default",
    });
  };

  const handleEdit = (ruleId: string) => {
    // TODO: Implement EDIT functionality
    toast({
      title: "Edit Mode",
      description: `Editing rule ${ruleId} (edit functionality not yet implemented)`,
      variant: "default",
    });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Rules Database</CardTitle>
            <CardDescription>
              View, edit, and delete compliance rules
            </CardDescription>
          </div>
          <Button
            onClick={fetchRules}
            disabled={isLoading}
            variant="outline"
            size="sm"
          >
            <RefreshCw
              className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {isLoading && rules.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            Loading rules...
          </div>
        ) : rules.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No rules found. Rules will appear here once they are created.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">Rule ID</TableHead>
                <TableHead>Rule Statement</TableHead>
                <TableHead className="w-[150px]">Jurisdiction</TableHead>
                <TableHead className="w-[150px]">Suggested Action</TableHead>
                <TableHead className="w-[200px]">Source URL</TableHead>
                <TableHead className="w-[100px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rules.map((rule) => (
                <TableRow key={rule.rule_id}>
                  <TableCell className="font-mono text-xs">
                    {rule.rule_id.substring(0, 8)}...
                  </TableCell>
                  <TableCell className="max-w-md">
                    <div className="line-clamp-2" title={rule.statement}>
                      {rule.statement}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {rule.jurisdiction?.map((j, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10"
                        >
                          {j}
                        </span>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ${
                        rule.suggested_action === "transaction blocking"
                          ? "bg-red-50 text-red-700 ring-red-600/20"
                          : rule.suggested_action === "escalation"
                          ? "bg-yellow-50 text-yellow-800 ring-yellow-600/20"
                          : "bg-green-50 text-green-700 ring-green-600/20"
                      }`}
                    >
                      {rule.suggested_action}
                    </span>
                  </TableCell>
                  <TableCell className="max-w-xs">
                    <a
                      href={rule.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:underline text-sm truncate block"
                      title={rule.source_url}
                    >
                      {rule.source_url}
                    </a>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => handleEdit(rule.rule_id)}
                        title="Edit rule"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="destructive"
                        size="icon"
                        onClick={() => handleDelete(rule.rule_id)}
                        title="Delete rule"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
};

export default RulesTab;
