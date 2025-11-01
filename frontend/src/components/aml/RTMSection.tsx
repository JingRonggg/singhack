import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DashboardTab from "./rtm/DashboardTab";
import TransactionIngestionTab from "./rtm/TransactionIngestionTab";
import RulesTab from "./rtm/RulesTab";
import CrawlingTab from "./rtm/CrawlingTab";

const RTMSection = () => {
  return (
    <Tabs defaultValue="dashboard" className="w-full">
      <TabsList className="grid w-full grid-cols-4 mb-4">
        <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
        <TabsTrigger value="ingestion">Transaction Ingestion</TabsTrigger>
        <TabsTrigger value="rules">Rules</TabsTrigger>
        <TabsTrigger value="crawling">Crawling</TabsTrigger>
      </TabsList>

      <TabsContent value="dashboard">
        <DashboardTab />
      </TabsContent>

      <TabsContent value="ingestion">
        <TransactionIngestionTab />
      </TabsContent>

      <TabsContent value="rules">
        <RulesTab />
      </TabsContent>

      <TabsContent value="crawling">
        <CrawlingTab />
      </TabsContent>
    </Tabs>
  );
};

export default RTMSection;
