import { z } from "zod";

import { createKeyStore, type KeyStore } from "@services/auth/key";

export const tokenRecord = "atlas.auth.access";
export const signoutRecord = "atlas.auth.signout";

const encoded = z
  .string()
  .max(65536)
  .regex(/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/);

const recordSchema = z.strictObject({
  iv: encoded,
  ciphertext: encoded,
  version: z.literal(1),
});

export interface TokenStorage {
  load(current: () => boolean): Promise<string | undefined>;
  save(token: string, current: () => boolean): Promise<boolean>;
  clear(): Promise<void>;
  destroy(): Promise<boolean>;
  signedOut(): boolean;
  signout(value: boolean): boolean;
}

export interface StorageEnvironment {
  storage(): Storage;
  crypto(): Crypto;
  keys: KeyStore;
}

const encode = (bytes: Uint8Array): string => {
  return btoa(String.fromCharCode(...bytes));
};

const decode = (value: string): Uint8Array<ArrayBuffer> => {
  return Uint8Array.from(atob(value), (character) => character.charCodeAt(0));
};

const readRecord = (raw: string | null) => {
  if (!raw || raw.length > 100000) {
    throw new Error();
  }

  const record = recordSchema.parse(JSON.parse(raw));
  const iv = decode(record.iv);
  const ciphertext = decode(record.ciphertext);

  if (
    iv.length === 12 &&
    ciphertext.length >= 17 &&
    ciphertext.length <= 32784
  ) {
    return {
      iv,
      ciphertext,
    };
  }

  throw new Error();
};

const encodeToken = (token: string): Uint8Array<ArrayBuffer> => {
  const plaintext = new TextEncoder().encode(token);

  if (plaintext.length > 0 && plaintext.length <= 32768) {
    return plaintext;
  }

  throw new Error();
};

const decodeToken = (plaintext: ArrayBuffer): string => {
  const token = new TextDecoder("utf-8", {
    fatal: true,
  }).decode(plaintext);

  if (token && token.length <= 32768) {
    return token;
  }

  throw new Error();
};

export const createTokenStorage = (
  environment: StorageEnvironment,
): TokenStorage => {
  let tail: Promise<unknown> = Promise.resolve();

  const serial = <T>(operation: () => Promise<T>): Promise<T> => {
    const result = tail.then(operation, operation);

    tail = result.catch(() => undefined);

    return result;
  };

  const remove = () => {
    try {
      environment.storage().removeItem(tokenRecord);
    } catch {}
  };

  const encrypt = async (token: string) => {
    const crypto = environment.crypto();
    const plaintext = encodeToken(token);

    let key = await environment.keys.get();

    if (!key) {
      const candidate = await crypto.subtle.generateKey(
        {
          name: "AES-GCM",
          length: 256,
        },
        false,
        ["encrypt", "decrypt"],
      );

      key = await environment.keys.create(candidate);
    }

    const iv = crypto.getRandomValues(new Uint8Array(12));

    const ciphertext = await crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv,
      },
      key,
      plaintext,
    );

    return {
      version: 1,
      iv: encode(iv),
      ciphertext: encode(new Uint8Array(ciphertext)),
    };
  };

  return {
    load: (current) => {
      return serial(async () => {
        try {
          const raw = environment.storage().getItem(tokenRecord);
          const record = readRecord(raw);
          const key = await environment.keys.get();

          if (!key) {
            throw new Error();
          }

          const plaintext = await environment.crypto().subtle.decrypt(
            {
              name: "AES-GCM",
              iv: record.iv,
            },
            key,
            record.ciphertext,
          );

          const token = decodeToken(plaintext);

          return current() ? token : undefined;
        } catch {
          if (current()) {
            remove();
          }

          return undefined;
        }
      });
    },

    save: (token, current) => {
      return serial(async () => {
        try {
          if (!current()) {
            return false;
          }

          const record = await encrypt(token);

          if (!current()) {
            return false;
          }

          environment.storage().setItem(tokenRecord, JSON.stringify(record));

          return true;
        } catch {
          if (current()) {
            remove();
          }

          return false;
        }
      });
    },

    clear: () => {
      return serial(async () => remove());
    },

    destroy: () => {
      return serial(async () => {
        let removed = true;

        try {
          environment.storage().removeItem(tokenRecord);
        } catch {
          removed = false;
        }

        try {
          await environment.keys.delete();
        } catch {
          removed = false;
        }

        return removed;
      });
    },

    signedOut: () => {
      try {
        return environment.storage().getItem(signoutRecord) === "1";
      } catch {
        return false;
      }
    },

    signout: (value) => {
      try {
        if (value) {
          environment.storage().setItem(signoutRecord, "1");
        } else {
          environment.storage().removeItem(signoutRecord);
        }

        return true;
      } catch {
        return false;
      }
    },
  };
};

export const tokenStorage = createTokenStorage({
  keys: createKeyStore(() => window.indexedDB),
  crypto: () => window.crypto,
  storage: () => window.localStorage,
});
