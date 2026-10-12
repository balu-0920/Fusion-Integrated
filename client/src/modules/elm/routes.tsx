import { lazy } from "react";
import { Navigate, type RouteObject } from "react-router-dom";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const ApplyPage = lazy(() => import("./pages/ApplyPage"));
const ApprovalsPage = lazy(() => import("./pages/ApprovalsPage"));
const HistoryPage = lazy(() => import("./pages/HistoryPage"));

export const routes: RouteObject[] = [
  { index: true, element: <Navigate to="dashboard" replace /> },
  { path: "dashboard", element: <DashboardPage /> },
  { path: "apply", element: <ApplyPage /> },
  { path: "approvals", element: <ApprovalsPage /> },
  { path: "history", element: <HistoryPage /> },
];