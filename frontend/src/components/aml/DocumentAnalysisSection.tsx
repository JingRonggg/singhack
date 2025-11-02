import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DocumentUploadTab from "./analysis/DocumentUploadTab";
import ImageUploadTab from "./analysis/ImageUploadTab";
import { useState } from "react";

export interface DocumentAnalysis {
  file_id: string;
  filename: string;
  document_metadata: {
    file_type: string;
    page_count: number;
    total_text_length: number;
  };
  document_structure?: {
    headers: string[];
    paragraph_count: number;
  };
  format_validation: {
    double_spacing_occurrences: number;
    spelling_mistakes: {
      total_errors: number;
      spelling_errors_count: number;
      spelling_errors?: Array<{
        word: string;
        message: string;
        replacements: string[];
      }>;
      characters_checked?: number;
    };
    font_size_variants?: number;
    indentation_inconsistent?: boolean;
    irregular_fonts?: string[];
    note?: string;
  };
  risk_analysis?: {
    triggered_rules: Record<string, string[]>;
    risk_score: number;
  };
}

export interface ImageAnalysis {
  file_id: string;
  filename: string;
  analysis: {
    authenticity: {
      score: number;
      status: string;
    };
    ai_detection: {
      is_ai_generated: boolean;
      confidence: number;
      risk_level: string;
    };
    tampering: {
      is_tampered: boolean;
      indicators: string[];
      indicator_count: number;
    };
    forensics: {
      metadata: {
        format: string;
        mode: string;
        size: string;
      };
      findings: string[];
    };
    reverse_search: {
      results: {
        uploaded_image_hash?: string;
        reference_image_hash?: string;
        exact_match?: string;
        perceptual_similarity?: string;
        match_status?: string;
        verdict?: string;
        reference_image_url?: string;
        hamming_distance?: string;
        error?: string;
        note?: string;
      };
      summary: {
        match_status: string;
        verdict: string;
        exact_match: boolean;
        similarity: string;
      };
    };
    recommendations: string[];
    timestamp: string;
  };
}

const DocumentAnalysisSection = () => {
  const [documentResults, setDocumentResults] = useState<DocumentAnalysis[]>(
    []
  );
  const [imageResults, setImageResults] = useState<ImageAnalysis[]>([]);

  return (
    <Tabs defaultValue="document" className="w-full">
      <TabsList className="grid w-full max-w-md grid-cols-2 mb-4">
        <TabsTrigger value="document">Upload Documents</TabsTrigger>
        <TabsTrigger value="image">Upload Images</TabsTrigger>
      </TabsList>

      <TabsContent value="document">
        <DocumentUploadTab
          results={documentResults}
          setResults={setDocumentResults}
        />
      </TabsContent>

      <TabsContent value="image">
        <ImageUploadTab results={imageResults} setResults={setImageResults} />
      </TabsContent>
    </Tabs>
  );
};

export default DocumentAnalysisSection;
