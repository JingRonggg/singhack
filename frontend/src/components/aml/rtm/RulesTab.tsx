import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { Trash2, Edit } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

// Mock rules data
const mockRules = [
  {
    ruleset_uuid: "950fca9a-4aa9-4bda-a388-0af5f343f397",
    rule_id: "1",
    rule_text: "Financial institutions must obtain written authorisation from MAS before conducting any banking business in Singapore.",
    created_at: "2025-10-15",
    source_url: "https://www.mas.gov.sg"
  },
  {
    ruleset_uuid: "950fca9a-4aa9-4bda-a388-0af5f343f397",
    rule_id: "2",
    rule_text: "Applicants must satisfy MAS admission criteria, including financial soundness, reputable track record.",
    created_at: "2025-10-15",
    source_url: "https://www.mas.gov.sg"
  },
  {
    ruleset_uuid: "950fca9a-4aa9-4bda-a388-0af5f343f397",
    rule_id: "3",
    rule_text: "A non-refundable application fee of S$20,000 must be paid to MAS with each licence application.",
    created_at: "2025-10-15",
    source_url: "https://www.mas.gov.sg"
  }
];

const RulesTab = () => {
  const [rules, setRules] = useState(mockRules);
  const { toast } = useToast();

  const handleDelete = (ruleId: string) => {
    setRules(rules.filter(rule => rule.rule_id !== ruleId));
    toast({
      title: "Rule Deleted",
      description: `Rule ${ruleId} has been removed`
    });
  };

  const handleEdit = (ruleId: string) => {
    toast({
      title: "Edit Mode",
      description: `Editing rule ${ruleId}`
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Rules Database</CardTitle>
        <CardDescription>
          View, edit, and delete compliance rules
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Rule ID</TableHead>
              <TableHead>Rule Statement</TableHead>
              <TableHead>Source URL</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rules.map((rule) => (
              <TableRow key={rule.rule_id}>
                <TableCell className="font-medium">{rule.rule_id}</TableCell>
                <TableCell className="max-w-md">{rule.rule_text}</TableCell>
                <TableCell className="max-w-xs truncate">
                  <a href={rule.source_url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                    {rule.source_url}
                  </a>
                </TableCell>
                <TableCell>{rule.created_at}</TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleEdit(rule.rule_id)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => handleDelete(rule.rule_id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
};

export default RulesTab;
