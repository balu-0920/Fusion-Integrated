import type { RouteObject } from "react-router-dom";

export interface ModuleManifest {
  code: string;
  basePath: string;
  load: () => Promise<{ routes: RouteObject[] }>;
}

export const MODULE_REGISTRY: Record<string, ModuleManifest> = {
  placement: {
    code: "placement",
    basePath: "/placement",
    load: () => import("../modules/placement/routes"),
  },
};