import { create } from "zustand";

import type { AuthenticatedUser } from "@schemas/auth/auth";

export type AuthStateType =
  "restoring" | "authenticated" | "unauthenticated" | "error";

export type AuthLogoutResultType = "confirmed" | "unconfirmed";
export type AuthLogoutType = "none" | "pending" | AuthLogoutResultType;
export type AuthErrorType = "session_uncertain" | "inconsistent_session";
export type AuthPersistenceType = "pending" | "available" | "unavailable";

export interface AuthState {
  status: AuthStateType;
  logout: AuthLogoutType;
  signoutPersisted: boolean;
  accessToken: string | null;
  error: AuthErrorType | null;
  persistence: AuthPersistenceType;
  user: Readonly<AuthenticatedUser> | null;
}

interface AuthStore extends AuthState {
  update(change: Partial<AuthState>): void;
}

export const initialAuth: AuthState = {
  user: null,
  error: null,
  logout: "none",
  accessToken: null,
  status: "restoring",
  persistence: "pending",
  signoutPersisted: true,
};

export const createAuthStore = () => {
  return create<AuthStore>()((set) => ({
    ...initialAuth,

    update: (change) => {
      set(change);
    },
  }));
};

const useAuthStore = createAuthStore();

export default useAuthStore;
