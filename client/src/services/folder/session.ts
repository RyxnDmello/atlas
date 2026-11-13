import { CanceledError } from "axios";

import {
  coordination,
  currentLease,
  type AuthLease,
} from "@services/auth/auth";

import useAuthStore from "@stores/auth";

interface FolderSession {
  user: string;
  lease: AuthLease;
}

export const folderSession = (): FolderSession | undefined => {
  const state = useAuthStore.getState();

  if (
    state.status !== "authenticated" ||
    !state.user ||
    !state.accessToken ||
    state.logout !== "none"
  ) {
    return undefined;
  }

  return {
    user: state.user.id,
    lease: {
      token: state.accessToken,
      tokenVersion: coordination.tokenVersion,
      sessionVersion: coordination.sessionVersion,
    },
  };
};

export const currentFolderSession = (session?: FolderSession): boolean => {
  const state = useAuthStore.getState();

  return (
    !!session &&
    currentLease(session.lease) &&
    state.user?.id === session.user &&
    state.logout === "none"
  );
};

export const checkFolderSession = (
  session?: FolderSession,
  signal?: AbortSignal,
) => {
  if (signal?.aborted || !currentFolderSession(session)) {
    throw new CanceledError("Folder request retired.");
  }
};
