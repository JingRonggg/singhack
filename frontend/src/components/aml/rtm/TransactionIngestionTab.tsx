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

interface TransactionRiskResult {
  triggered_rules: Record<string, string[]>;
  risk_score: number;
}

const TransactionIngestionTab = () => {
  const [singleTransaction, setSingleTransaction] = useState("");
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isBatchEvaluating, setIsBatchEvaluating] = useState(false);
  const [evaluationResults, setEvaluationResults] =
    useState<EvaluationResult | null>(null);
  const [transactionRisk, setTransactionRisk] =
    useState<TransactionRiskResult | null>(null);
  const [batchTransactionRisk, setBatchTransactionRisk] =
    useState<TransactionRiskResult | null>(null);
  const [isCalculatingRisk, setIsCalculatingRisk] = useState(false);
  const [isCalculatingBatchRisk, setIsCalculatingBatchRisk] = useState(false);
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
    setTransactionRisk(null);

    try {
      // Parse the JSON input
      const transactionData = JSON.parse(singleTransaction);

      // Fetch rules from the backend
      const rulesResponse = await fetch(
        "http://localhost:8000/api/dashboard/rules"
      );
      if (!rulesResponse.ok) {
        throw new Error("Failed to fetch rules");
      }
      const rulesData = await rulesResponse.json();
      const rules = rulesData.rules;

      // Call the evaluate endpoint
      const response = await fetch(
        "http://localhost:8000/api/evaluation/evaluate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            transaction: transactionData,
            rules: rules,
          }),
        }
      );

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

  const handleCalculateTransactionRisk = async () => {
    if (!singleTransaction.trim()) {
      toast({
        title: "Error",
        description: "Please enter transaction data in JSON format",
        variant: "destructive",
      });
      return;
    }

    setIsCalculatingRisk(true);

    try {
      // Parse the JSON input
      const transactionData = JSON.parse(singleTransaction);

      // Call the transaction-risk endpoint
      const response = await fetch(
        "http://localhost:8000/api/risk-score/transaction-single",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(transactionData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Risk calculation failed: ${response.status}`
        );
      }

      const riskData = await response.json();
      setTransactionRisk(riskData);

      toast({
        title: "Risk Calculated",
        description: `Transaction risk score: ${riskData.risk_score.toFixed(
          2
        )}`,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      toast({
        title: "Risk Calculation Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsCalculatingRisk(false);
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

    setIsBatchEvaluating(true);

    try {
      // Fetch rules from the backend
      const rulesResponse = await fetch(
        "http://localhost:8000/api/dashboard/rules"
      );
      if (!rulesResponse.ok) {
        throw new Error("Failed to fetch rules");
      }
      const rulesData = await rulesResponse.json();
      const rules = rulesData.rules;

      // Create form data for file upload
      const formData = new FormData();
      formData.append("file", batchFile);
      formData.append("rules", JSON.stringify(rules));

      // Call the evaluate-batch endpoint
      const response = await fetch(
        "http://localhost:8000/api/evaluation/evaluate-batch",
        {
          method: "POST",
          body: formData,
        }
      );

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
      setIsBatchEvaluating(false);
    }
  };

  const handleCalculateBatchRisk = async () => {
    if (!batchFile) {
      toast({
        title: "Error",
        description: "Please select a CSV file",
        variant: "destructive",
      });
      return;
    }

    setIsCalculatingBatchRisk(true);

    try {
      // Create form data for file upload
      const formData = new FormData();
      formData.append("file", batchFile);

      // Call the transaction-batch endpoint
      const response = await fetch(
        "http://localhost:8000/api/risk-score/transaction-batch",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail ||
            `Batch risk calculation failed: ${response.status}`
        );
      }

      const riskData = await response.json();
      setBatchTransactionRisk(riskData);

      toast({
        title: "Batch Risk Calculated",
        description: `Batch risk score: ${riskData.risk_score.toFixed(2)}`,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Unknown error occurred";
      toast({
        title: "Batch Risk Calculation Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsCalculatingBatchRisk(false);
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
            placeholder='Enter transaction data in JSON format. Example (copy and modify):
{
  "transaction_id": "TXN-001",
  "booking_jurisdiction": "HK",
  "regulator": "HKMA",
  "booking_datetime": "2024-01-01T10:00:00",
  "value_date": "01/01/2024",
  "amount": 50000,
  "currency": "USD",
  "channel": "RTGS",
  "product_type": "wire_transfer",
  "originator_name": "John Doe",
  "originator_account": "ACC001",
  "originator_country": "US",
  "beneficiary_name": "Jane Smith",
  "beneficiary_account": "ACC002",
  "beneficiary_country": "HK",
  "swift_mt": "MT103",
  "ordering_institution_bic": "ABCDUS33",
  "beneficiary_institution_bic": "XYZZHKHH",
  "swift_f50_present": "TRUE",
  "swift_f59_present": "TRUE",
  "swift_f70_purpose": "Payment for goods",
  "swift_f71_charges": "SHA",
  "travel_rule_complete": "TRUE",
  "fx_indicator": "FALSE",
  "fx_base_ccy": "",
  "fx_quote_ccy": "",
  "fx_applied_rate": 0,
  "fx_market_rate": 0,
  "fx_spread_bps": 0,
  "fx_counterparty": "",
  "customer_id": "CUST-001",
  "customer_type": "individual",
  "customer_risk_rating": "Low",
  "customer_is_pep": "FALSE",
  "kyc_last_completed": "01/01/2023",
  "kyc_due_date": "01/01/2025",
  "edd_required": "FALSE",
  "edd_performed": "FALSE",
  "sow_documented": "TRUE",
  "purpose_code": "GOODS",
  "narrative": "Payment for goods",
  "payment_type": "WIRE",
  "is_advised": "FALSE",
  "product_complex": "FALSE",
  "client_risk_profile": "Low",
  "suitability_assessed": "TRUE",
  "suitability_result": "match",
  "product_has_va_exposure": "FALSE",
  "va_disclosure_provided": "FALSE",
  "cash_id_verified": "FALSE",
  "daily_cash_total_customer": 0,
  "daily_cash_txn_count": 1,
  "sanctions_screening": "passed",
  "suspicion_determined_datetime": "",
  "str_filed_datetime": ""
}'
            value={singleTransaction}
            onChange={(e) => setSingleTransaction(e.target.value)}
            rows={20}
            disabled={isEvaluating || isCalculatingRisk}
          />
          <div className="flex gap-2">
            <Button
              onClick={handleSingleIngestion}
              disabled={isEvaluating || isCalculatingRisk}
            >
              {isEvaluating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Evaluating...
                </>
              ) : (
                "Evaluate Transaction"
              )}
            </Button>
            <Button
              onClick={handleCalculateTransactionRisk}
              disabled={isEvaluating || isCalculatingRisk}
              variant="outline"
            >
              {isCalculatingRisk ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Calculating...
                </>
              ) : (
                "Calculate Risk Score"
              )}
            </Button>
          </div>

          {transactionRisk && (
            <div className="mt-4 p-4 border rounded-lg space-y-3 bg-amber-50 dark:bg-amber-950">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">Transaction Risk Analysis</h3>
                <span
                  className={`text-lg font-bold px-3 py-1 rounded ${
                    transactionRisk.risk_score > 70
                      ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                      : transactionRisk.risk_score > 40
                      ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
                      : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                  }`}
                >
                  Risk Score: {transactionRisk.risk_score.toFixed(2)}
                </span>
              </div>

              {Object.keys(transactionRisk.triggered_rules).length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm">Triggered Rules:</h4>
                  {Object.entries(transactionRisk.triggered_rules).map(
                    ([rule, descriptions]) => (
                      <div
                        key={rule}
                        className="bg-white dark:bg-gray-800 rounded p-3 space-y-1"
                      >
                        <div className="text-sm font-semibold capitalize">
                          {rule.replace(/_/g, " ")}
                        </div>
                        {descriptions.map((desc, idx) => (
                          <div
                            key={idx}
                            className="text-xs text-muted-foreground"
                          >
                            • {desc}
                          </div>
                        ))}
                      </div>
                    )
                  )}
                </div>
              )}
            </div>
          )}

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
              disabled={isBatchEvaluating || isCalculatingBatchRisk}
              className="cursor-pointer"
            />
            {batchFile && (
              <span className="text-sm text-muted-foreground">
                {batchFile.name}
              </span>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              onClick={handleBatchIngestion}
              disabled={
                isBatchEvaluating || isCalculatingBatchRisk || !batchFile
              }
            >
              {isBatchEvaluating ? (
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
            <Button
              onClick={handleCalculateBatchRisk}
              disabled={
                isBatchEvaluating || isCalculatingBatchRisk || !batchFile
              }
              variant="outline"
            >
              {isCalculatingBatchRisk ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Calculating...
                </>
              ) : (
                "Calculate Batch Risk"
              )}
            </Button>
          </div>

          {batchTransactionRisk && (
            <div className="mt-4 p-4 border rounded-lg space-y-3 bg-amber-50 dark:bg-amber-950">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">
                  Batch Transaction Risk Analysis
                </h3>
                <span
                  className={`text-lg font-bold px-3 py-1 rounded ${
                    batchTransactionRisk.risk_score > 70
                      ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                      : batchTransactionRisk.risk_score > 40
                      ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
                      : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                  }`}
                >
                  Risk Score: {batchTransactionRisk.risk_score.toFixed(2)}
                </span>
              </div>

              {Object.keys(batchTransactionRisk.triggered_rules).length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-semibold text-sm">Triggered Rules:</h4>
                  {Object.entries(batchTransactionRisk.triggered_rules).map(
                    ([rule, descriptions]) => (
                      <div
                        key={rule}
                        className="bg-white dark:bg-gray-800 rounded p-3 space-y-1"
                      >
                        <div className="text-sm font-semibold capitalize">
                          {rule.replace(/_/g, " ")}
                        </div>
                        {descriptions.map((desc, idx) => (
                          <div
                            key={idx}
                            className="text-xs text-muted-foreground"
                          >
                            • {desc}
                          </div>
                        ))}
                      </div>
                    )
                  )}
                </div>
              )}
            </div>
          )}

          <p className="text-xs text-muted-foreground">
            CSV file must match the Transaction schema with all required fields
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default TransactionIngestionTab;
