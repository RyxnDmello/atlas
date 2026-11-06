"use client";

import { z } from "zod";
import { useRef } from "react";
import { useMutation } from "@tanstack/react-query";

import http from "@services/http/axios";
import { startAuth, finishLogout } from "@services/auth/auth";

import { AuthFailure, validatedResponse } from "@/services/http/validate";

import { AUTH_ENDPOINTS } from "@constants/auth";

const empty = z.union([z.literal(""), z.null(), z.undefined()]);

export default function useLogout() {
  const pending = useRef(false);

  const onLogout = async () => {
    if (pending.current) {
      throw new AuthFailure(0, "REQUEST_PENDING");
    }

    pending.current = true;

    const operation = startAuth("logout");
    let confirmed = false;

    try {
      await operation.ready;

      operation.check();

      const response = await http.post<unknown>(
        AUTH_ENDPOINTS.LOGOUT,
        undefined,
        {
          isProtected: false,
          withCredentials: true,
          validateStatus: () => true,
        },
      );

      validatedResponse(response, 204, empty);

      confirmed = true;
    } catch {
      confirmed = false;
    } finally {
      operation.release();
    }

    try {
      return await finishLogout(operation, confirmed);
    } finally {
      pending.current = false;
    }
  };

  return useMutation({
    gcTime: 0,
    retry: false,
    mutationFn: onLogout,
  });
}
