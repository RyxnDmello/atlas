import { createAskSession } from "@services/ask/askSession";
import { onAuthBoundary } from "@services/auth/auth";
import { folderSession, currentFolderSession } from "@services/folder/session";

export const createFileAskSession = (fileId: string) => {
  const owner = folderSession();
  let active = true;
  let unsubscribe: (() => void) | undefined;

  const current = () => active && currentFolderSession(owner);
  const session = createAskSession({
    current,
  });

  session.setScope(fileId);

  const retire = () => {
    active = false;
    unsubscribe?.();
    unsubscribe = undefined;
    session.setScope(undefined);
  };

  const activate = () => {
    unsubscribe?.();
    active = true;
    session.setScope(current() ? fileId : undefined);
    unsubscribe = onAuthBoundary(retire);
  };

  return {
    session,
    retire,
    activate,
  };
};
