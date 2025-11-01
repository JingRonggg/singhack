import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import RTMSection from "@/components/aml/RTMSection";
import DocumentAnalysisSection from "@/components/aml/DocumentAnalysisSection";

const AMLMonitoring = () => {
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-foreground mb-6">RecTech Intelligence</h1>

        <Tabs defaultValue="rtm" className="w-full">
          <TabsList className="grid w-full max-w-md grid-cols-2 mb-6">
            <TabsTrigger value="rtm">RTM of AML</TabsTrigger>
            <TabsTrigger value="doc-analysis">Doc and image analysis</TabsTrigger>
          </TabsList>

          <TabsContent value="rtm" className="space-y-4">
            <RTMSection />
          </TabsContent>

          <TabsContent value="doc-analysis" className="space-y-4">
            <DocumentAnalysisSection />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AMLMonitoring;
