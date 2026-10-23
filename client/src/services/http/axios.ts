import axios from "axios";

import { environment } from "@config/environmentPublic";

const client = axios.create({
  baseURL: environment.apiBaseUrl,
  withCredentials: false,
});

export default client;
