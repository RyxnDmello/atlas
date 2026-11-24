import { createElement } from "react";
import { renderToString } from "react-dom/server";
import {
  QueryClient,
  QueryClientProvider,
  QueryObserver,
} from "@tanstack/react-query";
import type { InternalAxiosRequestConfig } from "axios";

import "../auth/environment";

import useFolder from "@hooks/folder/useFolder";

import http from "@services/http/axios";
import { coordination } from "@services/auth/auth";

import { bindAuthCache } from "@providers/query/queryProvider";

import { folderKey } from "@utils/folder/folder";

import useAuthStore from "@stores/auth";

import { fixture, response, seedCredentials } from "../auth/fixtures";

export const id = "00000000-0000-4000-8000-000000000011";
export const child = "00000000-0000-4000-8000-000000000012";
export const other = "00000000-0000-4000-8000-000000000013";
export const folder = {
  id,
  name: "Selected folder",
  description: "Canonical description",
  parent_id: null,
  created_at: "2026-11-13T10:00:00Z",
  updated_at: "2026-11-13T10:00:00Z",
};
export const file = {
  id: other,
  name: "Read-only file",
  description: null,
  original_name: "source.md",
  extension: ".md",
  size_bytes: 25,
  status: "ready" as const,
  folder_id: id,
  created_at: folder.created_at,
  updated_at: folder.updated_at,
};
export const listing = {
  folder: null,
  folders: [],
  files: [],
};

/** Executes the real hooks without DOM effects; never contacts a live API. */
export const renderHook = <T>(hook: () => T, cache: QueryClient): T => {
  let value: T | undefined;
  const initial = useAuthStore.getInitialState();
  const previous = {
    ...initial,
  };

  function Probe() {
    value = hook();

    return null;
  }

  Object.assign(initial, useAuthStore.getState());

  try {
    renderToString(
      createElement(
        QueryClientProvider,
        {
          client: cache,
        },
        createElement(Probe),
      ),
    );
  } finally {
    Object.assign(initial, previous);
  }

  if (value === undefined) {
    throw new Error("Hook did not render.");
  }

  return value;
};

interface Reply {
  status: number;
  data: unknown;
}

export const harness = async (
  reply: Reply = {
    status: 200,
    data: listing,
  },
) => {
  const setup = fixture();
  const cache = new QueryClient();
  const requests: InternalAxiosRequestConfig[] = [];

  Object.assign(coordination, setup.session.context, {
    store: useAuthStore,
  });

  await seedCredentials(response, coordination);

  const unsubscribe = bindAuthCache(cache);

  http.defaults.adapter = async (config) => {
    requests.push(config);

    return {
      config,
      status: reply.status,
      statusText: "fixture",
      headers: {},
      data: reply.data,
    };
  };

  const onClose = () => {
    unsubscribe();
    cache.clear();
  };

  const onAdopt = async () =>
    seedCredentials(
      {
        ...response,
        user: {
          ...response.user,
          id: other,
        },
      },
      coordination,
    );

  return {
    cache,
    requests,
    reply,
    close: onClose,
    adopt: onAdopt,
  };
};

export const observeFolder = (cache: QueryClient, selected: string | null) => {
  const hook = renderHook(() => useFolder(selected), cache);
  const query = cache.getQueryCache().find({
    queryKey: folderKey(selected),
  });

  if (!query) {
    throw new Error("Folder query not registered.");
  }

  const observer = new QueryObserver(cache, {
    ...query.options,
    queryKey: query.queryKey,
    enabled: false,
  });

  return {
    hook,
    query,
    observer,
  };
};
