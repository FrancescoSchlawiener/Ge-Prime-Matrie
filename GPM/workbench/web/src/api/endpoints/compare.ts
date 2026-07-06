import type { WorkbenchResponse } from "../gpm-api";
import { type RedundancyScanOptions, request } from "../request";

export const compareEndpoints = {
  wordPair: (a: string, b: string, profile: string, mode = "compare") =>
    request<WorkbenchResponse>("/api/compare/word-pair", {
      method: "POST",
      body: JSON.stringify({ a, b, profile, mode }),
    }),

  anagramSearch: (word: string, profile: string, limit = 100) =>
    request<WorkbenchResponse>("/api/compare/anagram-search", {
      method: "POST",
      body: JSON.stringify({ word, profile, limit }),
    }),

  compareDocuments: (docARef: string, docBRef: string, tier: number) =>
    request<WorkbenchResponse>("/api/compare/documents", {
      method: "POST",
      body: JSON.stringify({ doc_a_ref: docARef, doc_b_ref: docBRef, tier }),
    }),

  iCurve: (docARef: string, docBRef: string) =>
    request<WorkbenchResponse>("/api/compare/i-curve", {
      method: "POST",
      body: JSON.stringify({ doc_a_ref: docARef, doc_b_ref: docBRef }),
    }),

  corpusIndex: (documentRefs: string[], profile: string, extendIndexId?: string) =>
    request<WorkbenchResponse>("/api/compare/corpus/index", {
      method: "POST",
      body: JSON.stringify({
        document_refs: documentRefs,
        profile,
        extend_index_id: extendIndexId ?? null,
      }),
    }),

  corpusQuery: (indexId: string, queryRef: string, topK: number, tier: number) =>
    request<WorkbenchResponse>("/api/compare/corpus/query", {
      method: "POST",
      body: JSON.stringify({ index_id: indexId, query_ref: queryRef, top_k: topK, tier }),
    }),

  redundancyScan: (documentRef: string, opts: RedundancyScanOptions = {}) =>
    request<WorkbenchResponse>("/api/compare/redundancy/scan", {
      method: "POST",
      body: JSON.stringify({ document_ref: documentRef, ...opts }),
    }),
};
