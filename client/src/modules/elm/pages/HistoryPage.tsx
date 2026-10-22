import { Paper, Title, Table, Button, Group, Badge } from "@mantine/core";
import { usePendingApprovals, useReviewLeave } from "../api/hooks";

export default function ApprovalsPage() {
  const { data: approvals, isLoading } = usePendingApprovals();
  const reviewMutation = useReviewLeave();

  const handleAction = (id: number, action: string) => {
    reviewMutation.mutate({ id, action });
  };

  return (
    <Paper p="md" shadow="sm" radius="md" withBorder>
      <Title order={2} mb="lg">Pending Approvals</Title>
      <Table striped highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Applicant ID</Table.Th>
            <Table.Th>Category</Table.Th>
            <Table.Th>Duration</Table.Th>
            <Table.Th>Reason</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {isLoading ? (
            <Table.Tr><Table.Td colSpan={5}>Loading...</Table.Td></Table.Tr>
          ) : (
            approvals?.map((app) => (
              <Table.Tr key={app.id}>
                <Table.Td>{app.applicant_id}</Table.Td>
                <Table.Td><Badge>{app.category.toUpperCase()}</Badge></Table.Td>
                <Table.Td>{app.start_date} to {app.end_date}</Table.Td>
                <Table.Td>{app.purpose}</Table.Td>
                <Table.Td>
                  <Group gap="xs">
                    {app.category === "cl" || app.category === "rh" ? (
                      <>
                        <Button size="xs" color="green" onClick={() => handleAction(app.id, "approve")}>Approve</Button>
                        <Button size="xs" color="red" variant="outline" onClick={() => handleAction(app.id, "reject")}>Reject</Button>
                      </>
                    ) : (
                      <>
                        <Button size="xs" color="blue" onClick={() => handleAction(app.id, "recommend")}>Recommend</Button>
                        <Button size="xs" color="orange" variant="outline" onClick={() => handleAction(app.id, "not_recommend")}>Not Recommend</Button>
                      </>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))
          )}
        </Table.Tbody>
      </Table>
    </Paper>
  );
}