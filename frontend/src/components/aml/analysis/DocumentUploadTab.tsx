import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { Upload } from "lucide-react";
import { DocumentAnalysis } from "../DocumentAnalysisSection";

interface DocumentUploadTabProps {
  results: DocumentAnalysis[];
  setResults: React.Dispatch<React.SetStateAction<DocumentAnalysis[]>>;
}

const DocumentUploadTab = ({ results, setResults }: DocumentUploadTabProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      setIsLoading(true);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch("http://localhost:8000/api/upload/", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Upload failed");
        }

        const data = await response.json();
        console.log("API Response:", data);

        // Document response
        const newResult: DocumentAnalysis = {
          file_id: data.file_id,
          filename: data.filename || file.name,
          document_metadata: data.document_metadata,
          document_structure: data.document_structure,
          format_validation: data.format_validation,
        };

        setResults([...results, newResult]);
        toast({
          title: "Document Analyzed",
          description: `${file.name} has been processed successfully`,
        });
      } catch (error) {
        toast({
          title: "Upload Failed",
          description:
            error instanceof Error
              ? error.message
              : "An error occurred during upload",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Upload Document</CardTitle>
          <CardDescription>
            Upload documents (PDF, TXT, XLSX) or images for analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center min-h-[300px] space-y-4">
          <div className="border-2 border-dashed border-border rounded-lg p-8 w-full text-center">
            <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <Input
              type="file"
              accept=".pdf,.doc,.docx,.txt,.xlsx,.xls,.jpg,.jpeg,.png,.bmp,.tiff,.webp"
              onChange={handleFileUpload}
              className="max-w-xs mx-auto"
              disabled={isLoading}
            />
          </div>
          <Button disabled={isLoading}>
            {isLoading ? "Analyzing..." : "Analyze Document"}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Analysis Results</CardTitle>
          <CardDescription>
            Document validation and error reports
          </CardDescription>
        </CardHeader>
        <CardContent>
          {results.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No documents analyzed yet
            </div>
          ) : (
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {results.map((result) => (
                <div
                  key={result.file_id}
                  className="border rounded-lg p-4 space-y-3"
                >
                  <div className="font-semibold">{result.filename}</div>

                  {/* Document Metadata */}
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">File Type:</span>{" "}
                      {result.document_metadata.file_type.toUpperCase()}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Pages:</span>{" "}
                      {result.document_metadata.page_count}
                    </div>
                    <div>
                      <span className="text-muted-foreground">
                        Text Length:
                      </span>{" "}
                      {result.document_metadata.total_text_length}
                    </div>
                    {result.format_validation.font_size_variants !==
                      undefined && (
                      <div>
                        <span className="text-muted-foreground">
                          Font Variants:
                        </span>{" "}
                        {result.format_validation.font_size_variants}
                      </div>
                    )}
                  </div>

                  {/* Document Structure */}
                  {result.document_structure && (
                    <div className="border-t pt-3 space-y-2">
                      <div className="font-medium text-sm">
                        Document Structure
                      </div>
                      <div className="text-sm">
                        <span className="text-muted-foreground">
                          Paragraphs:
                        </span>{" "}
                        {result.document_structure.paragraph_count}
                      </div>
                      {result.document_structure.headers.length > 0 && (
                        <div className="text-sm">
                          <span className="text-muted-foreground">
                            Headers:
                          </span>
                          <div className="mt-1 space-y-1">
                            {result.document_structure.headers
                              .slice(0, 5)
                              .map((header, idx) => (
                                <div
                                  key={idx}
                                  className="text-xs bg-muted px-2 py-1 rounded"
                                >
                                  {header}
                                </div>
                              ))}
                            {result.document_structure.headers.length > 5 && (
                              <div className="text-xs text-muted-foreground">
                                +{result.document_structure.headers.length - 5}{" "}
                                more
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Format Validation */}
                  <div className="border-t pt-3 space-y-2">
                    <div className="font-medium text-sm">Format Validation</div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        Double Spacing:
                      </span>
                      <Badge
                        variant={
                          result.format_validation.double_spacing_occurrences >
                          0
                            ? "secondary"
                            : "outline"
                        }
                      >
                        {result.format_validation.double_spacing_occurrences}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        Spelling Errors:
                      </span>
                      <Badge
                        variant={
                          result.format_validation.spelling_mistakes
                            .total_errors > 5
                            ? "destructive"
                            : "secondary"
                        }
                      >
                        {
                          result.format_validation.spelling_mistakes
                            .total_errors
                        }
                      </Badge>
                    </div>

                    {result.format_validation.spelling_mistakes
                      .spelling_errors &&
                      result.format_validation.spelling_mistakes.spelling_errors
                        .length > 0 && (
                        <div className="text-sm">
                          <span className="text-muted-foreground">
                            Spelling Issues:
                          </span>
                          <div className="mt-1 space-y-1">
                            {result.format_validation.spelling_mistakes.spelling_errors.map(
                              (error, idx) => (
                                <div
                                  key={idx}
                                  className="text-xs bg-destructive/10 px-2 py-1 rounded"
                                >
                                  <span className="font-medium">
                                    {error.word}
                                  </span>
                                  {error.replacements.length > 0 && (
                                    <span className="text-muted-foreground">
                                      {" → "}
                                      {error.replacements.join(", ")}
                                    </span>
                                  )}
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}

                    {result.format_validation.indentation_inconsistent !==
                      undefined && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">
                          Indentation Issues:
                        </span>
                        <Badge
                          variant={
                            result.format_validation.indentation_inconsistent
                              ? "destructive"
                              : "outline"
                          }
                        >
                          {result.format_validation.indentation_inconsistent
                            ? "Yes"
                            : "No"}
                        </Badge>
                      </div>
                    )}

                    {result.format_validation.irregular_fonts &&
                      result.format_validation.irregular_fonts.length > 0 && (
                        <div className="text-sm">
                          <span className="text-muted-foreground">
                            Irregular Fonts:
                          </span>
                          <div className="mt-1 text-xs bg-muted px-2 py-1 rounded">
                            {result.format_validation.irregular_fonts.join(
                              ", "
                            )}
                          </div>
                        </div>
                      )}

                    {result.format_validation.note && (
                      <div className="text-xs text-muted-foreground italic">
                        {result.format_validation.note}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DocumentUploadTab;
