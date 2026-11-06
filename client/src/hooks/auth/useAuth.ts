"use client";

import { useQuery } from "@tanstack/react-query";

import http from "@services/http/axios";

import { safeAuthError, validatedResponse } from "@/services/http/validate";

import { userSchema } from "@schemas/auth/auth";

import { AUTH_ENDPOINTS } from "@constants/auth";

export default function useAuth() {
  const onAuth = async (signal: AbortSignal) => {
    try {
      const response = await http.get<unknown>(AUTH_ENDPOINTS.AUTH, {
        signal,
        isProtected: true,
        withCredentials: false,
        validateStatus: () => true,
      });

      return validatedResponse(response, 200, userSchema);
    } catch (error) {
      throw safeAuthError(error);
    }
  };

  return useQuery({
    queryKey: ["auth", "current"],
    gcTime: 0,
    retry: false,
    enabled: false,
    queryFn: ({ signal }) => onAuth(signal),
  });
}
