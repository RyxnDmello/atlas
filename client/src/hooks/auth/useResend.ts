"use client";

import { useRef } from "react";
import { useMutation } from "@tanstack/react-query";

import http from "@services/http/axios";

import {
  AuthFailure,
  safeAuthError,
  validatedResponse,
} from "@/services/http/validate";

import {
  resendSchema,
  verificationRequiredSchema,
  type Resend,
} from "@schemas/auth/auth";

import { AUTH_ENDPOINTS } from "@constants/auth";

export default function useResend() {
  const pending = useRef(false);

  const onResend = async (input: Resend) => {
    if (pending.current) {
      throw new AuthFailure(0, "REQUEST_PENDING");
    }

    const data = resendSchema.parse(input);

    pending.current = true;

    try {
      const response = await http.post<unknown>(AUTH_ENDPOINTS.RESEND, data, {
        isProtected: false,
        withCredentials: false,
        validateStatus: () => true,
      });

      return validatedResponse(response, 200, verificationRequiredSchema);
    } catch (error) {
      throw safeAuthError(error);
    } finally {
      pending.current = false;
    }
  };

  return useMutation({
    gcTime: 0,
    retry: false,
    mutationFn: onResend,
  });
}
