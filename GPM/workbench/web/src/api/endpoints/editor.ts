import type { WorkbenchResponse } from "../gpm-api";
import { request } from "../request";

export const editorEndpoints = {
  compile: (mode: string, text: string, profile: string, languageId?: string, contentKey?: string) =>
    request<WorkbenchResponse>("/api/editor/compile", {
      method: "POST",
      body: JSON.stringify({
        mode,
        text,
        profile,
        language_id: languageId,
        content_key: contentKey,
      }),
    }),

  reconstruct: (documentRef: string, mode: string) =>
    request<WorkbenchResponse<{ text: string }>>("/api/editor/reconstruct", {
      method: "POST",
      body: JSON.stringify({ document_ref: documentRef, mode }),
    }),

  gpmRead: (base64: string, key?: string) =>
    request<WorkbenchResponse>("/api/editor/gpm/read", {
      method: "POST",
      body: JSON.stringify({ base64, key: key ?? null }),
    }),

  gpmSearch: (documentRef: string, query: string, mode: "word" | "gcd" | "lcm", queries?: string[]) =>
    request<WorkbenchResponse>("/api/editor/gpm/search", {
      method: "POST",
      body: JSON.stringify({
        document_ref: documentRef,
        query,
        mode,
        queries: queries ?? [],
      }),
    }),

  gpmWrite: (documentRef: string, profile: string) =>
    request<WorkbenchResponse>("/api/editor/gpm/write", {
      method: "POST",
      body: JSON.stringify({ document_ref: documentRef, profile }),
    }),

  spectroscope: (documentRef: string, tokenStart: number, tokenEnd: number, contentKey?: string) =>
    request<WorkbenchResponse>("/api/editor/spectroscope", {
      method: "POST",
      body: JSON.stringify({
        document_ref: documentRef,
        token_start: tokenStart,
        token_end: tokenEnd,
        content_key: contentKey ?? null,
      }),
    }),
};
