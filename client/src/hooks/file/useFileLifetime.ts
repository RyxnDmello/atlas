import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { fileLifetime } from "@services/file/lifetime";

export default function useFileLifetime() {
  const cache = useQueryClient();

  const [request] = useState(() => fileLifetime(cache));

  useEffect(() => {
    request.activate();

    return request.retire;
  }, [request]);

  return request;
}
