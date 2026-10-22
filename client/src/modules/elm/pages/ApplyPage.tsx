import { useState } from "react";
import { 
  TextInput, Select, Textarea, Button, Paper, Title, Stack, Checkbox, Group 
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useNavigate } from "react-router-dom";
import { useApplyLeave } from "../api/hooks";
import { ApplyPayload } from "../api/types";

export default function ApplyPage() {
  const navigate = useNavigate();
  const applyMutation = useApplyLeave();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const form = useForm<ApplyPayload>({
    initialValues: {
      category: "cl",
      start_date: "",
      end_date: "",
      is_first_half: false,
      is_second_half: false,
      purpose: "",
      station_leave: false,
      substitute_id: undefined,
    },
    validate: {
      start_date: (value) => (value ? null : "Start date is required"),
      end_date: (value) => (value ? null : "End date is required"),
      purpose: (value) => (value ? null : "Purpose is required"),
    },
  });

  const handleSubmit = (values: ApplyPayload) => {
    setErrorMsg(null);
    applyMutation.mutate(values, {
      onSuccess: () => {
        // Redirect to history/dashboard upon successful submission
        navigate("../history");
      },
      onError: (error: any) => {
        setErrorMsg(
          error.response?.data?.error?.message || "Failed to submit application."
        );
      },
    });
  };

  return (
    <Paper p="md" shadow="sm" radius="md" withBorder>
      <Title order={2} mb="lg">Apply for Leave</Title>
      
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack gap="md">
          <Select
            label="Leave Category"
            placeholder="Select leave type"
            data={[
              { value: "cl", label: "Casual Leave (CL)" },
              { value: "rh", label: "Restricted Holiday (RH)" },
              { value: "scl", label: "Special Casual Leave (SCL)" },
              { value: "el", label: "Earned Leave (EL)" },
              { value: "col", label: "Commuted Leave (COL)" },
              { value: "vl", label: "Vacation Leave (VL)" },
            ]}
            {...form.getInputProps("category")}
          />

          <Group grow>
            <TextInput
              type="date"
              label="Start Date"
              withAsterisk
              {...form.getInputProps("start_date")}
            />
            <TextInput
              type="date"
              label="End Date"
              withAsterisk
              {...form.getInputProps("end_date")}
            />
          </Group>

          {form.values.category === "cl" && (
            <Group>
              <Checkbox
                label="First Half"
                {...form.getInputProps("is_first_half", { type: "checkbox" })}
              />
              <Checkbox
                label="Second Half"
                {...form.getInputProps("is_second_half", { type: "checkbox" })}
              />
            </Group>
          )}

          <Textarea
            label="Purpose / Reason"
            placeholder="Provide a reason for your leave"
            withAsterisk
            minRows={3}
            {...form.getInputProps("purpose")}
          />

          <TextInput
            type="number"
            label="Substitute ID (Optional)"
            placeholder="Enter User ID of your substitute if required"
            {...form.getInputProps("substitute_id")}
          />

          <Checkbox
            label="Requires Station Leave (Leaving Jabalpur)"
            {...form.getInputProps("station_leave", { type: "checkbox" })}
          />

          {errorMsg && <div style={{ color: "red" }}>{errorMsg}</div>}

          <Button 
            type="submit" 
            loading={applyMutation.isPending}
            mt="md"
          >
            Submit Application
          </Button>
        </Stack>
      </form>
    </Paper>
  );
}