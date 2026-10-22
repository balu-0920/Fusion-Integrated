import { useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

import { useQuery } from "@tanstack/react-query";
import { ApplyPayload, LeaveApplication } from "./types";

// Note: Fusion uses standard axios instances configured with CSRF tokens.
// Adjust the axios import to match your client/src/lib/http.ts if necessary.

export function useApplyLeave() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: ApplyPayload) => {
      const response = await axios.post<LeaveApplication>(
        "/api/v1/elm/applications/apply",
        payload
      );
      return response.data;
    },
    onSuccess: () => {
      // Invalidate queries to refresh leave balances and history tables
      queryClient.invalidateQueries({ queryKey: ["elm", "balances"] });
      queryClient.invalidateQueries({ queryKey: ["elm", "history"] });
    },
  });
}

export function useWithdrawLeave() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (applicationId: number) => {
      const response = await axios.post<LeaveApplication>(
        `/api/v1/elm/applications/${applicationId}/withdraw`
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["elm", "history"] });
    },
  });
}


export function useLeaveHistory() {
  return useQuery({
    queryKey: ["elm", "history"],
    queryFn: async () => {
      const response = await axios.get<LeaveApplication[]>("/api/v1/elm/applications/mine");
      return response.data;
    },
  });
}

export function usePendingApprovals() {
  return useQuery({
    queryKey: ["elm", "approvals"],
    queryFn: async () => {
      const response = await axios.get<LeaveApplication[]>("/api/v1/elm/applications/pending");
      return response.data;
    },
  });
}

export function useReviewLeave() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, action }: { id: number; action: string }) => {
      const response = await axios.post(`/api/v1/elm/applications/${id}/unit-head-review`, { action });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["elm", "approvals"] });
    },
  });
}