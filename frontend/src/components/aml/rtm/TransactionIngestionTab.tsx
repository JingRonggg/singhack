import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { Upload, FileText, Loader2 } from "lucide-react";

const TransactionIngestionTab = () => {
  const [singleTransaction, setSingleTransaction] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
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

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.csv')) {
        toast({
          title: "Invalid File",
          description: "Please select a CSV file",
          variant: "destructive"
        });
        return;
      }
      setSelectedFile(file);
      toast({
        title: "File Selected",
        description: `${file.name} (${(file.size / 1024).toFixed(2)} KB)`
      });
    }
  };

  const handleBatchIngestion = async () => {
    if (!selectedFile) {
      toast({
        title: "Error",
        description: "Please select a CSV file",
        variant: "destructive"
      });
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://localhost:8000/api/evaluation/evaluate-batch', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();

      toast({
        title: "Batch Ingestion Complete",
        description: `Successfully processed ${result.successful_evaluations} transactions. Failed: ${result.failed_evaluations}`
      });

      // Reset state
      setSelectedFile(null);
      // Reset file input
      const fileInput = document.getElementById('csv-upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

    } catch (error) {
      toast({
        title: "Upload Failed",
        description: error instanceof Error ? error.message : "An error occurred during upload",
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
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
            Upload a CSV file to process multiple transactions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <Input
                id="csv-upload"
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                disabled={isUploading}
                className="cursor-pointer"
              />
            </div>
          </div>

          {selectedFile && (
            <div className="flex items-center gap-2 p-3 bg-muted rounded-md">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">{selectedFile.name}</span>
              <span className="text-sm text-muted-foreground ml-auto">
                {(selectedFile.size / 1024).toFixed(2)} KB
              </span>
            </div>
          )}

          <Button
            onClick={handleBatchIngestion}
            disabled={!selectedFile || isUploading}
            className="w-full"
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Upload and Process CSV
              </>
            )}
          </Button>

          <p className="text-xs text-muted-foreground">
            CSV file should contain transaction data matching the required schema
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default TransactionIngestionTab;
