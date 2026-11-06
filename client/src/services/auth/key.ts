export interface KeyStore {
  get(): Promise<CryptoKey | undefined>;
  create(candidate: CryptoKey): Promise<CryptoKey>;
  delete(): Promise<void>;
}

const store = "keys";
const database = "atlas.auth";

const valid = (value: unknown): value is CryptoKey => {
  return (
    typeof CryptoKey !== "undefined" &&
    value instanceof CryptoKey &&
    value.type === "secret" &&
    !value.extractable &&
    value.algorithm.name === "AES-GCM" &&
    "length" in value.algorithm &&
    value.algorithm.length === 256 &&
    value.usages.length === 2 &&
    value.usages.includes("encrypt") &&
    value.usages.includes("decrypt")
  );
};

export const createKeyStore = (factory: () => IDBFactory): KeyStore => {
  const access = (
    candidate?: CryptoKey,
    deleting = false,
  ): Promise<CryptoKey | undefined> => {
    return new Promise((resolve, reject) => {
      let abandoned = false;

      const opening = factory().open(database, 1);

      opening.onupgradeneeded = () => opening.result.createObjectStore(store);
      opening.onerror = () => reject(new Error("Key storage unavailable."));

      opening.onblocked = () => {
        abandoned = true;

        reject(new Error("Key storage blocked."));
      };

      opening.onsuccess = () => {
        const connection = opening.result;

        if (abandoned) {
          connection.close();
        } else {
          try {
            const transaction = connection.transaction(
              store,
              candidate || deleting ? "readwrite" : "readonly",
            );

            let key: CryptoKey | undefined;

            const records = transaction.objectStore(store);
            const reading = records.get("access");

            reading.onsuccess = () => {
              try {
                if (deleting) {
                  records.delete("access");
                } else if (valid(reading.result)) {
                  key = reading.result;
                } else if (candidate) {
                  key = candidate;

                  records.put(candidate, "access");
                }
              } catch {
                transaction.abort();
              }
            };

            transaction.oncomplete = () => {
              connection.close();

              resolve(key);
            };

            transaction.onabort = transaction.onerror = () => {
              connection.close();

              reject(new Error("Key storage unavailable."));
            };
          } catch {
            connection.close();

            reject(new Error("Key storage unavailable."));
          }
        }
      };
    });
  };

  return {
    get: () => access(),

    delete: async () => {
      await access(undefined, true);
    },

    create: async (candidate) => {
      const key = await access(candidate);

      if (key) {
        return key;
      } else {
        throw new Error("Key storage unavailable.");
      }
    },
  };
};
