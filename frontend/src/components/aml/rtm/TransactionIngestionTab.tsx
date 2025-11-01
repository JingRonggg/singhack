import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

const TransactionIngestionTab = () => {
  const [singleTransaction, setSingleTransaction] = useState("");
  const [batchTransactions, setBatchTransactions] = useState("");
  const { toast } = useToast();

  const handleSingleIngestion = () => {
    if (!singleTransaction.trim()) {
      toast({
        title: "Error",
        description: "Please enter transaction data",
        variant: "destructive"
      });
      return;
    }
    toast({
      title: "Transaction Ingested",
      description: "Single transaction has been processed successfully"
    });
    setSingleTransaction("");
  };

  const handleBatchIngestion = () => {
    if (!batchTransactions.trim()) {
      toast({
        title: "Error",
        description: "Please enter batch transaction data",
        variant: "destructive"
      });
      return;
    }
    toast({
      title: "Batch Ingestion Complete",
      description: "Batch transactions have been processed successfully"
    });
    setBatchTransactions("");
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Single Transaction Ingestion</CardTitle>
          <CardDescription>
            Ingest transaction data one row at a time
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input
            placeholder="Enter transaction data (e.g., TXN-001, Amount: 1000, Customer: ABC Corp)"
            value={singleTransaction}
            onChange={(e) => setSingleTransaction(e.target.value)}
          />
          <Button onClick={handleSingleIngestion}>Ingest Transaction</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Batch Transaction Ingestion</CardTitle>
          <CardDescription>
            Ingest multiple transactions using CSV format
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Paste CSV data here (one transaction per line)"
            value={batchTransactions}
            onChange={(e) => setBatchTransactions(e.target.value)}
            rows={8}
          />
          <Button onClick={handleBatchIngestion}>Ingest Batch</Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default TransactionIngestionTab;
