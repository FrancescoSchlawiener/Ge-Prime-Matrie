import { type JobRecord, type RedundancyScanOptions, pollJob, request } from "../request";

export const jobEndpoints = {
  jobCompile: (mode: string, text: string, profile: string, languageId?: string, contentKey?: string) =>
    request<{ job_id: string }>("/api/jobs/compile", {
      method: "POST",
      body: JSON.stringify({
        mode,
        text,
        profile,
        language_id: languageId,
        content_key: contentKey,
      }),
    }),

  jobRedundancyScan: (documentRef: string, opts: RedundancyScanOptions = {}) =>
    request<{ job_id: string }>("/api/jobs/redundancy/scan", {
      method: "POST",
      body: JSON.stringify({ document_ref: documentRef, ...opts }),
    }),

  jobCorpusIndex: (documentRefs: string[], profile: string, extendIndexId?: string) =>
    request<{ job_id: string }>("/api/jobs/corpus/index", {
      method: "POST",
      body: JSON.stringify({
        document_refs: documentRefs,
        profile,
        extend_index_id: extendIndexId ?? null,
      }),
    }),

  getJob: (jobId: string) => request<JobRecord>(`/api/jobs/${jobId}`),
  pollJob,
};
