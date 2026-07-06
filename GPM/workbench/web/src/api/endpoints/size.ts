import type { WorkbenchResponse } from "../gpm-api";
import { request } from "../request";

export const sizeEndpoints = {
  sizeEncodeWord: (
    contentHash: string,
    profile: string,
    fallback?: { original: string; normalized: string; substance: number; perm_index: number },
  ) =>
    request<WorkbenchResponse>("/api/size/encode-word", {
      method: "POST",
      body: JSON.stringify({
        content_hash: contentHash,
        profile,
        fallback: fallback
          ? {
              original: fallback.original,
              normalized: fallback.normalized,
              substance: fallback.substance,
              perm_index: fallback.perm_index,
            }
          : null,
      }),
    }),

  sizeEncodeBatch: (wordHashes: string[], profile: string) =>
    request<WorkbenchResponse>("/api/size/encode-batch", {
      method: "POST",
      body: JSON.stringify({ word_hashes: wordHashes, profile }),
    }),

  sizeDecode: (
    contentHash: string,
    profile: string,
    fallback?: { substance: number; perm_index: number },
  ) =>
    request<WorkbenchResponse>("/api/size/decode", {
      method: "POST",
      body: JSON.stringify({
        content_hash: contentHash,
        profile,
        fallback: fallback
          ? { substance: fallback.substance, perm_index: fallback.perm_index }
          : null,
      }),
    }),
};
