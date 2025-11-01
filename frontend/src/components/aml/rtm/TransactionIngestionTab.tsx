import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Upload } from "lucide-react";

interface EvaluationResult {
  transaction_id: string;
  total_rules_evaluated: number;
  violated_rules: Array<{
    rule_id: string;
    rule_statement: string;
    confidence_score: number;
    reasoning: string;
    suggested_action: string;
  }>;
  passed_rules: Array<{
    rule_id: string;
    rule_statement: string;
  }>;
  overall_risk_level: string;
  requires_action: boolean;
}

const TransactionIngestionTab = () => {
  const [singleTransaction, setSingleTransaction] = useState("");
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationResults, setEvaluationResults] =
    useState<EvaluationResult | null>(null);
  const { toast } = useToast();

  const handleSingleIngestion = async () => {
    if (!singleTransaction.trim()) {
      toast({
        title: "Error",
        description: "Please enter transaction data in JSON format",
        variant: "destructive",
      });
      return;
    }

    setIsEvaluating(true);
    setEvaluationResults(null);

    try {
      // Parse the JSON input
      const transactionData = JSON.parse(singleTransaction);

      // Fetch rules from the backend
      const rulesResponse = await fetch("/api/dashboard/rules");
      if (!rulesResponse.ok) {
        throw new Error("Failed to fetch rules");
      }
      const rules = await rulesResponse.json();

      // Call the evaluate endpoint
      const response = await fetch("/api/evaluation/evaluate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          transaction: transactionData,
          rules: rules,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Evaluation failed");
      }

      const result = await response.json();
      setEvaluationResults(result);

      toast({
        title: "Evaluation Complete",
        description: `Transaction evaluated against ${
          result.total_rules_evaluated
        } rules. Risk Level: ${result.overall_risk_level.toUpperCase()}`,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      toast({
        title: "Evaluation Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleBatchIngestion = async () => {
    if (!batchFile) {
      toast({
        title: "Error",
        description: "Please select a CSV file",
        variant: "destructive",
      });
      return;
    }

    setIsEvaluating(true);

    try {
      // Fetch rules from the backend
      const rulesResponse = await fetch("/api/dashboard/rules");
      if (!rulesResponse.ok) {
        throw new Error("Failed to fetch rules");
      }
      const rules = await rulesResponse.json();

      // Create form data for file upload
      const formData = new FormData();
      formData.append("file", batchFile);
      formData.append("rules", JSON.stringify(rules));

      // Call the evaluate-batch endpoint
      const response = await fetch("/api/evaluation/evaluate-batch", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Batch evaluation failed");
      }

      const result = await response.json();

      toast({
        title: "Batch Evaluation Complete",
        description: `Processed ${result.total_transactions} transactions. Success: ${result.successful_evaluations}, Failed: ${result.failed_evaluations}`,
      });

      setBatchFile(null);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      toast({
        title: "Batch Evaluation Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.endsWith(".csv")) {
        toast({
          title: "Invalid File",
          description: "Please select a CSV file",
          variant: "destructive",
        });
        return;
      }
      setBatchFile(file);
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Single Transaction Evaluation</CardTitle>
          <CardDescription>
            Evaluate a single transaction against all compliance rules
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder='Enter transaction data in JSON format, e.g.:
{
  "transaction_id": "TXN-001",
  "amount": 50000,
  "currency": "USD",
  "booking_jurisdiction": "HK",
  "regulator": "HKMA",
  ...
}'
            value={singleTransaction}
            onChange={(e) => setSingleTransaction(e.target.value)}
            rows={10}
            disabled={isEvaluating}
          />
          <Button onClick={handleSingleIngestion} disabled={isEvaluating}>
            {isEvaluating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Evaluating...
              </>
            ) : (
              "Evaluate Transaction"
            )}
          </Button>

          {evaluationResults && (
            <div className="mt-4 p-4 border rounded-lg space-y-3">
              <h3 className="font-semibold">Evaluation Results</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-muted-foreground">Transaction ID:</span>
                  <p className="font-mono">
                    {evaluationResults.transaction_id}
                  </p>
                </div>
                <div>
                  <span className="text-muted-foreground">Risk Level:</span>
                  <p className="font-semibold">
                    <span
                      className={
                        evaluationResults.overall_risk_level === "high"
                          ? "text-red-600"
                          : evaluationResults.overall_risk_level === "medium"
                          ? "text-yellow-600"
                          : "text-green-600"
                      }
                    >
                      {evaluationResults.overall_risk_level.toUpperCase()}
                    </span>
                  </p>
                </div>
                <div>
                  <span className="text-muted-foreground">
                    Rules Evaluated:
                  </span>
                  <p>{evaluationResults.total_rules_evaluated}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">
                    Requires Action:
                  </span>
                  <p
                    className={
                      evaluationResults.requires_action
                        ? "text-red-600 font-semibold"
                        : "text-green-600"
                    }
                  >
                    {evaluationResults.requires_action ? "YES" : "NO"}
                  </p>
                </div>
              </div>

              {evaluationResults.violated_rules.length > 0 && (
                <div className="mt-3">
                  <h4 className="font-semibold text-red-600 mb-2">
                    Violated Rules ({evaluationResults.violated_rules.length})
                  </h4>
                  <div className="space-y-2">
                    {evaluationResults.violated_rules.map((rule) => (
                      <div
                        key={rule.rule_id}
                        className="p-2 bg-red-50 border border-red-200 rounded text-sm"
                      >
                        <p className="font-medium">{rule.rule_statement}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {rule.reasoning}
                        </p>
                        <p className="text-xs mt-1">
                          <span className="font-semibold">
                            Suggested Action:
                          </span>{" "}
                          {rule.suggested_action}
                        </p>
                        <p className="text-xs">
                          <span className="font-semibold">Confidence:</span>{" "}
                          {(rule.confidence_score * 100).toFixed(0)}%
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {evaluationResults.passed_rules.length > 0 && (
                <div className="mt-3">
                  <h4 className="font-semibold text-green-600 mb-2">
                    Passed Rules ({evaluationResults.passed_rules.length})
                  </h4>
                  <div className="text-xs text-muted-foreground">
                    {evaluationResults.passed_rules.map((rule) => (
                      <p key={rule.rule_id}>• {rule.rule_statement}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Batch Transaction Evaluation</CardTitle>
          <CardDescription>
            Upload a CSV file to evaluate multiple transactions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              disabled={isEvaluating}
              className="cursor-pointer"
            />
            {batchFile && (
              <span className="text-sm text-muted-foreground">
                {batchFile.name}
              </span>
            )}
          </div>
          <Button
            onClick={handleBatchIngestion}
            disabled={isEvaluating || !batchFile}
          >
            {isEvaluating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Evaluate Batch
              </>
            )}
          </Button>
          <p className="text-xs text-muted-foreground">
            CSV file must match the Transaction schema with all required fields
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default TransactionIngestionTab;
