import type { WorkbenchResponse } from "../gpm-api";
import { request } from "../request";

export const codecEndpoints = {
  encodeWord: (word: string, profile: string, includeSteps = false) =>
    request<WorkbenchResponse>("/api/calc/encode-word", {
      method: "POST",
      body: JSON.stringify({ word, profile, include_steps: includeSteps }),
    }),

  encodeBatch: (text: string, profile: string, includeSteps = true) =>
    request<WorkbenchResponse>("/api/calc/encode-batch", {
      method: "POST",
      body: JSON.stringify({ text, profile, include_steps: includeSteps }),
    }),

  decodeWord: (substance: number, index: number, profile: string, includeSteps = false) =>
    request<WorkbenchResponse>("/api/calc/decode-word", {
      method: "POST",
      body: JSON.stringify({ substance, index, profile, include_steps: includeSteps }),
    }),

  compareWords: (a: string, b: string, profile: string, includeSteps = false) =>
    request<WorkbenchResponse>("/api/calc/compare-words", {
      method: "POST",
      body: JSON.stringify({ a, b, profile, include_steps: includeSteps }),
    }),
};
