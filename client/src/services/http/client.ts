import axios from "axios";

import { environment } from "@config/environmentPublic";

export const http = axios.create({
  baseURL: environment.apiBaseUrl,
  withCredentials: false,
});
