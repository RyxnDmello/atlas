import { CanceledError } from "axios";
import type { QueryClient } from "@tanstack/react-query";

import {
  folderSession,
  checkFolderSession,
  currentFolderSession,
} from "@services/folder/session";
import { onAuthBoundary } from "@services/auth/auth";

import { fileError, FileFailure } from "@utils/file/file";

export interface FileRequest {
  controller: AbortController;
  unsubscribe(): void;
}

export const fileLifetime = (cache: QueryClient) => {
  const session = folderSession();

  let active = true;
  let pending: FileRequest | undefined;

  const check = (request?: FileRequest) => {
    if (!active) {
      throw new CanceledError("File request retired.");
    }

    checkFolderSession(session, request?.controller.signal);
  };

  const begin = (): FileRequest => {
    check();

    if (pending) {
      throw new FileFailure(409, "REQUEST_PENDING");
    }

    const controller = new AbortController();
    const unsubscribe = onAuthBoundary(() => controller.abort());

    pending = {
      controller,
      unsubscribe,
    };

    return pending;
  };

  const invalidate = async (request: FileRequest, confirmed: boolean) => {
    check(request);

    await cache.invalidateQueries({
      queryKey: ["drive"],
      refetchType: confirmed ? "active" : "none",
    });

    check(request);
  };

  const reject = async (
    request: FileRequest,
    error: unknown,
  ): Promise<never> => {
    check(request);

    const failure = fileError(error);

    if (failure.reconcile) {
      await invalidate(request, false);
    }

    check(request);

    throw failure;
  };

  const end = (request: FileRequest) => {
    request.unsubscribe();

    if (pending === request) {
      pending = undefined;
    }
  };

  const retire = () => {
    if (pending && currentFolderSession(session)) {
      void cache.invalidateQueries({
        queryKey: ["drive"],
        refetchType: "none",
      });
    }

    active = false;
    pending?.controller.abort();
    pending?.unsubscribe();
  };

  const activate = () => {
    active = true;
  };

  return {
    end,
    check,
    begin,
    retire,
    reject,
    activate,
    invalidate,
  };
};
