import { parseEnvironment } from "@config/environment";

export const environment = parseEnvironment(
  process.env.NEXT_PUBLIC_ATLAS_API_BASE_URL,
);
