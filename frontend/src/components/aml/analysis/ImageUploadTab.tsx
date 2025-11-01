import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { Upload } from "lucide-react";
import { ImageAnalysis } from "../DocumentAnalysisSection";

const mockAnalysis: ImageAnalysis = {
  file_id: "74360218-898f-4712-8e70-3d62b0750567",
  filename: "BankStatementChequing.png",
  analysis: {
    authenticity: {
      score: 40,
      status: "suspicious",
    },
    ai_detection: {
      is_ai_generated: false,
      confidence: 10,
      risk_level: "low",
    },
    tampering: {
      is_tampered: true,
      indicators: [
        "Inconsistent font styles",
        "Unusual alignment of text elements",
        "Potential alteration of financial figures",
      ],
      indicator_count: 3,
    },
    forensics: {
      metadata: {
        format: "PNG",
        mode: "RGB",
        size: "690x533",
      },
      findings: [
        "Red channel shows unnatural concentration",
        "Inconsistent edge patterns detected",
      ],
    },
    recommendations: [
      "Verify document with original bank records",
      "Check for matching documents online",
    ],
    timestamp: new Date().toISOString(),
  },
};

interface ImageUploadTabProps {
  results: ImageAnalysis[];
  setResults: React.Dispatch<React.SetStateAction<ImageAnalysis[]>>;
}

const ImageUploadTab = ({ results, setResults }: ImageUploadTabProps) => {
  const { toast } = useToast();

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const newResult = {
        ...mockAnalysis,
        filename: files[0].name,
        file_id: Math.random().toString(36).substring(7),
      };
      setResults([...results, newResult]);
      toast({
        title: "Image Analyzed",
        description: `${files[0].name} has been processed successfully`,
      });
    }
  };

  const getAuthenticityBadge = (score: number) => {
    if (score < 50)
      return { variant: "destructive" as const, label: "Suspicious" };
    if (score < 75) return { variant: "secondary" as const, label: "Moderate" };
    return { variant: "outline" as const, label: "Authentic" };
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Upload Image</CardTitle>
          <CardDescription>
            Upload images for authenticity and tampering detection
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center min-h-[300px] space-y-4">
          <div className="border-2 border-dashed border-border rounded-lg p-8 w-full text-center">
            <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <Input
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="max-w-xs mx-auto"
            />
          </div>
          <Button>Analyze Image</Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Analysis Results</CardTitle>
          <CardDescription>
            Authenticity, tampering, and AI detection results
          </CardDescription>
        </CardHeader>
        <CardContent>
          {results.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No images analyzed yet
            </div>
          ) : (
            <div className="space-y-4 max-h-[500px] overflow-y-auto">
              {results.map((result) => (
                <div
                  key={result.file_id}
                  className="border rounded-lg p-4 space-y-3"
                >
                  <div className="font-semibold">{result.filename}</div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        Authenticity Score:
                      </span>
                      <Badge
                        variant={
                          getAuthenticityBadge(
                            result.analysis.authenticity.score
                          ).variant
                        }
                      >
                        {result.analysis.authenticity.score}% -{" "}
                        {
                          getAuthenticityBadge(
                            result.analysis.authenticity.score
                          ).label
                        }
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">AI Generated:</span>
                      <Badge
                        variant={
                          result.analysis.ai_detection.is_ai_generated
                            ? "destructive"
                            : "outline"
                        }
                      >
                        {result.analysis.ai_detection.is_ai_generated
                          ? "Yes"
                          : "No"}{" "}
                        ({result.analysis.ai_detection.confidence}%)
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        Tampering Detected:
                      </span>
                      <Badge
                        variant={
                          result.analysis.tampering.is_tampered
                            ? "destructive"
                            : "outline"
                        }
                      >
                        {result.analysis.tampering.is_tampered ? "Yes" : "No"}
                      </Badge>
                    </div>
                  </div>

                  {result.analysis.tampering.is_tampered && (
                    <div className="space-y-1 text-sm">
                      <div className="font-medium">Tampering Indicators:</div>
                      <ul className="list-disc list-inside text-muted-foreground space-y-1">
                        {result.analysis.tampering.indicators.map(
                          (indicator, idx) => (
                            <li key={idx}>{indicator}</li>
                          )
                        )}
                      </ul>
                    </div>
                  )}

                  <div className="space-y-1 text-sm">
                    <div className="font-medium">Forensic Findings:</div>
                    <div className="text-muted-foreground">
                      Format: {result.analysis.forensics.metadata.format} |
                      Size: {result.analysis.forensics.metadata.size}
                    </div>
                    <ul className="list-disc list-inside text-muted-foreground space-y-1">
                      {result.analysis.forensics.findings.map(
                        (finding, idx) => (
                          <li key={idx}>{finding}</li>
                        )
                      )}
                    </ul>
                  </div>

                  <div className="space-y-1 text-sm">
                    <div className="font-medium">Recommendations:</div>
                    <ul className="list-disc list-inside text-muted-foreground space-y-1">
                      {result.analysis.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
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

export default ImageUploadTab;
