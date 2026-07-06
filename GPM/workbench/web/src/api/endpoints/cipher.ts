import type { WorkbenchResponse } from "../gpm-api";
import { request } from "../request";

export const cipherEndpoints = {
  cipherEncrypt: (text: string, key: string, mode = "word") =>
    request<WorkbenchResponse>("/api/cipher/encrypt", {
      method: "POST",
      body: JSON.stringify({ text, key, mode }),
    }),

  cipherDecrypt: (base64Gpm: string, key: string) =>
    request<WorkbenchResponse>("/api/cipher/decrypt", {
      method: "POST",
      body: JSON.stringify({ base64_gpm: base64Gpm, key }),
    }),
};
