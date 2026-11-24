import { useRef } from "react";

import useLogout from "@hooks/auth/useLogout";

import { Button } from "@components/ui/button";
import AuthGate from "@components/Auth/AuthGate";
import NotFound from "@components/Common/NotFound";
import DriveWorkspace from "@components/Drive/DriveWorkspace";
import { Card, CardHeader, CardTitle, CardContent } from "@components/ui/card";

import { coordination } from "@services/auth/auth";

import { validFolderId } from "@utils/folder/folder";

import useAuthStore from "@stores/auth";

interface DrivePanelProps {
  folderId?: string;
}

export default function DrivePanel({ folderId }: DrivePanelProps) {
  const pending = useRef(false);

  const { logout, isLogoutLoading } = useLogout();

  const user = useAuthStore((state) => state.user);
  const persistence = useAuthStore((state) => state.persistence);

  if (folderId !== undefined && !validFolderId(folderId)) {
    return <NotFound />;
  }

  const onLogout = async () => {
    if (pending.current) {
      return;
    }

    pending.current = true;

    try {
      await logout();
    } catch {
    } finally {
      pending.current = false;
    }
  };

  return (
    <AuthGate mode="protected">
      <Card>
        <CardHeader>
          <CardTitle>Drive</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <dl className="space-y-2">
            <dt>Name</dt>
            <dd>{user?.name}</dd>
            <dt>Email</dt>
            <dd>{user?.email}</dd>
          </dl>

          <Button disabled={isLogoutLoading} onClick={() => void onLogout()}>
            Logout
          </Button>

          {persistence === "unavailable" && (
            <p role="alert">
              Session persistence is unavailable. This session may not survive a
              reload.
            </p>
          )}

          <DriveWorkspace
            key={`${coordination.sessionVersion}:${user?.id}:${folderId ?? "root"}`}
            folderId={folderId ?? null}
          />
        </CardContent>
      </Card>
    </AuthGate>
  );
}
