import AuthGate from "@components/Auth/AuthGate";
import NotFound from "@components/Common/NotFound";
import FileWorkspace from "@components/File/FileWorkspace";
import { Card, CardContent } from "@components/ui/card";

import { coordination } from "@services/auth/auth";

import { validFolderId } from "@utils/folder/folder";

import useAuthStore from "@stores/auth";

interface FilePanelProps {
  fileId: string;
}

export default function FilePanel({ fileId }: FilePanelProps) {
  const user = useAuthStore((state) => state.user);

  if (!validFolderId(fileId)) {
    return <NotFound />;
  }

  return (
    <AuthGate mode="protected">
      <Card>
        <CardContent className="space-y-4">
          <FileWorkspace
            key={`${coordination.sessionVersion}:${user?.id}:${fileId}`}
            fileId={fileId}
          />
        </CardContent>
      </Card>
    </AuthGate>
  );
}
