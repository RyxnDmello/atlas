import { expect, test } from "bun:test";

import "./environment";

import { createKeyStore, type KeyStore } from "@services/auth/key";
import {
  createTokenStorage,
  signoutRecord,
  tokenRecord,
} from "@services/auth/token";

import { deferred } from "./fixtures";

class MemoryStorage implements Storage {
  private records = new Map<string, string>();

  get length() {
    return this.records.size;
  }

  key = (index: number) => {
    return Array.from(this.records.keys())[index] ?? null;
  };

  getItem = (name: string) => {
    return this.records.get(name) ?? null;
  };

  setItem = (name: string, value: string) => {
    this.records.set(name, value);
  };

  removeItem = (name: string) => {
    this.records.delete(name);
  };

  clear = () => {
    this.records.clear();
  };
}

const fixture = () => {
  const storage = new MemoryStorage();
  let key: CryptoKey | undefined;

  const keys: KeyStore = {
    delete: async () => {
      key = undefined;
    },
    get: async () => {
      return key && structuredClone(key);
    },

    create: async (candidate) => {
      key ??= structuredClone(candidate);

      return key;
    },
  };

  const environment = {
    storage: () => storage,
    crypto: () => crypto,
    keys,
  };

  return {
    storage,
    keys,
    environment,
    tokens: createTokenStorage(environment),
  };
};

test("AES-256-GCM nonextractable structured-clone key survives store reopening; every write has fresh IV", async () => {
  const context = fixture();
  const plaintext = "synthetic.jwt.fixture";

  expect(await context.tokens.save(plaintext, () => true)).toBe(true);

  const first = context.storage.getItem(tokenRecord)!;

  expect(first).not.toContain(plaintext);

  const key = await context.keys.get();

  expect(key?.algorithm.name).toBe("AES-GCM");
  expect(key && "length" in key.algorithm && key.algorithm.length).toBe(256);
  expect(key?.extractable).toBe(false);
  expect(key?.usages).toEqual(["encrypt", "decrypt"]);

  await expect(crypto.subtle.exportKey("raw", key!)).rejects.toThrow();

  const reopened = createTokenStorage(context.environment);

  expect(await reopened.load(() => true)).toBe(plaintext);
  expect(await reopened.save(plaintext, () => true)).toBe(true);
  expect(context.storage.getItem(tokenRecord)).not.toBe(first);

  const record: unknown = JSON.parse(first);

  expect(Object.keys(record as Record<string, unknown>).sort()).toEqual([
    "ciphertext",
    "iv",
    "version",
  ]);
});

test.each(["json", "version", "iv", "ciphertext", "encoding", "length"])(
  "corrupt %s record fails closed and removes only Atlas ciphertext",
  async (kind) => {
    const context = fixture();

    context.storage.setItem("unrelated", "keep");

    await context.tokens.save("synthetic.jwt", () => true);

    const record = JSON.parse(context.storage.getItem(tokenRecord)!) as Record<
      string,
      unknown
    >;

    if (kind === "version") {
      record.version = 2;
    }

    if (kind === "iv") {
      record.iv = btoa("000000000000");
    }

    if (kind === "ciphertext") {
      record.ciphertext = btoa("tampered ciphertext");
    }

    if (kind === "encoding") {
      record.iv = "%%%";
    }

    if (kind === "length") {
      record.iv = btoa("short");
    }

    context.storage.setItem(
      tokenRecord,
      kind === "json" ? "{" : JSON.stringify(record),
    );

    expect(await context.tokens.load(() => true)).toBeUndefined();
    expect(context.storage.getItem(tokenRecord)).toBeNull();
    expect(context.storage.getItem("unrelated")).toBe("keep");
  },
);

test("missing record/key and crypto/storage failures degrade without plaintext fallback", async () => {
  const context = fixture();

  expect(await context.tokens.load(() => true)).toBeUndefined();

  await context.tokens.save("synthetic.jwt", () => true);

  const missing = createTokenStorage({
    ...context.environment,
    keys: {
      ...context.keys,

      get: async () => {
        return undefined;
      },
    },
  });

  expect(await missing.load(() => true)).toBeUndefined();

  for (const environment of [
    {
      ...context.environment,
      storage: () => {
        throw new Error("blocked");
      },
    },
    {
      ...context.environment,
      crypto: () => {
        throw new Error("unavailable");
      },
    },
    {
      ...context.environment,
      keys: {
        ...context.keys,
        get: async () => {
          throw new Error("IDB");
        },
      },
    },
    {
      ...context.environment,
      keys: {
        ...context.keys,
        get: async () => undefined,
        create: async () => {
          throw new Error("IDB write");
        },
      },
    },
  ]) {
    const tokens = createTokenStorage(environment);

    expect(await tokens.save("synthetic.jwt", () => true)).toBe(false);
    expect(await tokens.load(() => true)).toBeUndefined();

    await tokens.clear();
  }

  context.storage.setItem = () => {
    throw new Error("quota");
  };

  expect(await context.tokens.save("synthetic.jwt", () => true)).toBe(false);
});

test("serialized key creation and stale encryption writes cannot restore after clear", async () => {
  const context = fixture();
  const pending = deferred<CryptoKey>();
  let creates = 0;
  let active = true;

  const tokens = createTokenStorage({
    ...context.environment,
    keys: {
      ...context.keys,
      get: async () => {
        return undefined;
      },

      create: async () => {
        creates++;

        return pending.promise;
      },
    },
  });

  const writing = tokens.save("old", () => active);

  await Bun.sleep(1);

  active = false;

  const clearing = tokens.clear();

  pending.resolve(
    await crypto.subtle.generateKey(
      {
        name: "AES-GCM",
        length: 256,
      },
      false,
      ["encrypt", "decrypt"],
    ),
  );

  expect(await writing).toBe(false);

  await clearing;

  expect(creates).toBe(1);
  expect(context.storage.getItem(tokenRecord)).toBeNull();

  await Promise.all([
    context.tokens.save("first", () => true),
    context.tokens.save("second", () => true),
  ]);

  expect(await context.tokens.load(() => true)).toBe("second");
});

test("signout record is nonsecret, cleanup preserves other origin data and key", async () => {
  const context = fixture();

  context.storage.setItem("unrelated", "keep");

  await context.tokens.save("fixture", () => true);

  expect(context.tokens.signout(true)).toBe(true);
  expect(context.storage.getItem(signoutRecord)).toBe("1");
  expect(context.tokens.signedOut()).toBe(true);

  await context.tokens.clear();

  expect(context.storage.getItem("unrelated")).toBe("keep");
  expect(await context.keys.get()).toBeDefined();

  context.tokens.signout(false);

  expect(context.tokens.signedOut()).toBe(false);
});

/** Narrow asynchronous IndexedDB fake, not evidence of a real browser database. */
const fakeIndexedDb = () => {
  const records = new Map<string, unknown>();
  let opens = 0;
  let closes = 0;

  const factory = {
    open: () => {
      opens++;

      const opening: Record<string, unknown> = {};

      queueMicrotask(() => {
        const connection = {
          createObjectStore: () => {},

          close: () => {
            closes++;
          },

          transaction: () => {
            const transaction: Record<string, unknown> = {};

            transaction.objectStore = () => ({
              get: (name: string) => {
                const reading: Record<string, unknown> = {};

                queueMicrotask(() => {
                  reading.result = structuredClone(records.get(name));

                  (reading.onsuccess as () => void)();

                  queueMicrotask(() =>
                    (transaction.oncomplete as () => void)(),
                  );
                });

                return reading;
              },

              put: (value: unknown, name: string) => {
                records.set(name, structuredClone(value));
              },

              delete: (name: string) => {
                records.delete(name);
              },
            });

            return transaction;
          },
        };

        opening.result = connection;

        if (opens === 1) {
          (opening.onupgradeneeded as () => void)();
        }

        (opening.onsuccess as () => void)();
      });

      return opening;
    },
  };

  return {
    factory: factory as unknown as IDBFactory,
    closes: () => closes,
  };
};

test("IndexedDB adapter atomically reuses stored CryptoKey and closes reopened connections", async () => {
  const fake = fakeIndexedDb();
  const keys = createKeyStore(() => fake.factory);

  expect(await keys.get()).toBeUndefined();

  const key = await crypto.subtle.generateKey(
    {
      name: "AES-GCM",
      length: 256,
    },
    false,
    ["encrypt", "decrypt"],
  );

  await keys.create(key);

  const reopened = createKeyStore(() => fake.factory);
  const recovered = await reopened.get();

  expect(recovered?.extractable).toBe(false);

  const alternate = await crypto.subtle.generateKey(
    {
      name: "AES-GCM",
      length: 256,
    },
    false,
    ["encrypt", "decrypt"],
  );

  const same = await reopened.create(alternate);
  const iv = crypto.getRandomValues(new Uint8Array(12));

  const encrypted = await crypto.subtle.encrypt(
    {
      name: "AES-GCM",
      iv,
    },
    key,
    new Uint8Array([1, 2]),
  );

  expect(
    new Uint8Array(
      await crypto.subtle.decrypt(
        {
          name: "AES-GCM",
          iv,
        },
        same,
        encrypted,
      ),
    ),
  ).toEqual(new Uint8Array([1, 2]));
  expect(fake.closes()).toBe(4);

  await reopened.delete();

  expect(await keys.get()).toBeUndefined();
  expect(fake.closes()).toBe(6);
});

test("logout destroys only auth ciphertext/key, then a new login encrypts with a fresh key", async () => {
  const context = fixture();

  context.storage.setItem("unrelated", "keep");

  await context.tokens.save("old.fixture", () => true);

  const oldKey = await context.keys.get();
  const oldRecord = context.storage.getItem(tokenRecord)!;

  expect(await context.tokens.destroy()).toBe(true);
  expect(await context.keys.get()).toBeUndefined();
  expect(context.storage.getItem(tokenRecord)).toBeNull();
  expect(context.storage.getItem("unrelated")).toBe("keep");

  expect(await context.tokens.save("new.fixture", () => true)).toBe(true);

  const key = await context.keys.get();
  const old = JSON.parse(oldRecord);

  await expect(
    crypto.subtle.decrypt(
      {
        name: "AES-GCM",
        iv: Uint8Array.from(atob(old.iv), (c) => c.charCodeAt(0)),
      },
      key!,
      Uint8Array.from(atob(old.ciphertext), (c) => c.charCodeAt(0)),
    ),
  ).rejects.toThrow();

  expect(key).not.toBe(oldKey);
  expect(await createTokenStorage(context.environment).load(() => true)).toBe(
    "new.fixture",
  );
});

test("failed key deletion is reported and does not prevent ciphertext removal", async () => {
  const context = fixture();
  const tokens = createTokenStorage({
    ...context.environment,
    keys: {
      ...context.keys,
      delete: async () => {
        throw new Error("blocked");
      },
    },
  });

  await tokens.save("fixture", () => true);

  expect(await tokens.destroy()).toBe(false);
  expect(context.storage.getItem(tokenRecord)).toBeNull();
});

test("pre-refactor version-1 record decrypts without using the new storage writer", async () => {
  const context = fixture();
  const key = await crypto.subtle.generateKey(
    {
      name: "AES-GCM",
      length: 256,
    },
    false,
    ["encrypt", "decrypt"],
  );
  const iv = new Uint8Array(12).fill(17);
  const ciphertext = await crypto.subtle.encrypt(
    {
      name: "AES-GCM",
      iv,
    },
    key,
    new TextEncoder().encode("old.version1.fixture"),
  );

  await context.keys.create(key);

  context.storage.setItem(
    tokenRecord,
    JSON.stringify({
      version: 1,
      iv: btoa(String.fromCharCode(...iv)),
      ciphertext: btoa(String.fromCharCode(...new Uint8Array(ciphertext))),
    }),
  );

  expect(await context.tokens.load(() => true)).toBe("old.version1.fixture");
});

test("destroy is ordered between an obsolete encryption and a newer login write", async () => {
  const context = fixture();
  const pending = deferred<CryptoKey>();
  let active = true;
  let reads = 0;

  const tokens = createTokenStorage({
    ...context.environment,
    keys: {
      ...context.keys,
      get: async () => {
        reads++;

        if (reads === 1) {
          return pending.promise;
        }

        return context.keys.get();
      },
    },
  });

  const obsolete = tokens.save("old", () => active);

  await Bun.sleep(0);

  active = false;

  const destroy = tokens.destroy();
  const fresh = tokens.save("new", () => true);

  pending.resolve(
    await crypto.subtle.generateKey(
      {
        name: "AES-GCM",
        length: 256,
      },
      false,
      ["encrypt", "decrypt"],
    ),
  );

  expect(await obsolete).toBe(false);
  expect(await destroy).toBe(true);
  expect(await fresh).toBe(true);
  expect(await tokens.load(() => true)).toBe("new");
});
