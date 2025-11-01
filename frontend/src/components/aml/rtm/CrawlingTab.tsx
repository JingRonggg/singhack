import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { Card as ResultCard } from "@/components/ui/card";

const CrawlingTab = () => {
  const [urls, setUrls] = useState("");
  const [crawlResults, setCrawlResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleCrawl = async () => {
    setIsLoading(true);

    try {
      // Parse URLs from textarea (one per line)
      const urlList = urls
        .split("\n")
        .map((url) => url.trim())
        .filter((url) => url.length > 0);

      // Prepare request body
      const requestBody = urlList.length > 0 ? { urls: urlList } : null;

      const response = await fetch("http://localhost:8000/api/scraper/scrape", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: requestBody ? JSON.stringify(requestBody) : JSON.stringify({}),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Crawling failed");
      }

      const data = await response.json();
      console.log("Crawl Response:", data);

      setCrawlResults(data);
      toast({
        title: "Crawl Complete",
        description: `Rules have been extracted from ${
          Object.keys(data).length
        } source(s)`,
      });
    } catch (error) {
      toast({
        title: "Crawl Failed",
        description:
          error instanceof Error
            ? error.message
            : "An error occurred during crawling",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Manual Trigger Crawl</CardTitle>
          <CardDescription>
            Define a list of URLs to crawl and generate compliance rules
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Enter URLs (one per line) - Optional&#10;https://www.mas.gov.sg&#10;https://www.example.com"
            value={urls}
            onChange={(e) => setUrls(e.target.value)}
            rows={6}
            disabled={isLoading}
          />
          <Button onClick={handleCrawl} disabled={isLoading}>
            {isLoading ? "Crawling..." : "Start Crawling"}
          </Button>
        </CardContent>
      </Card>

      {crawlResults && (
        <ResultCard>
          <CardHeader>
            <CardTitle>Crawl Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(crawlResults).map(
                ([url, data]: [string, any]) => (
                  <div key={url} className="border rounded-lg p-4 space-y-2">
                    <div className="font-semibold">URL: {url}</div>
                    <div className="text-sm text-muted-foreground">
                      Ruleset ID: {data.ruleset_id}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Created:{" "}
                      {new Date(data.created_at * 1000).toLocaleString()}
                    </div>
                    <div className="mt-2">
                      <div className="font-medium mb-2">Extracted Rules:</div>
                      <div className="space-y-2">
                        {Object.entries(data.rules).map(
                          ([id, rule]: [string, any]) => (
                            <div
                              key={id}
                              className="text-sm bg-muted p-2 rounded"
                            >
                              <span className="font-medium">Rule {id}:</span>{" "}
                              {rule}
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  </div>
                )
              )}
            </div>
          </CardContent>
        </ResultCard>
      )}
    </div>
  );
};

export default CrawlingTab;
