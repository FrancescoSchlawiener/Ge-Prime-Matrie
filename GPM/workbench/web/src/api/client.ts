import { codecEndpoints } from "./endpoints/codec";
import { cipherEndpoints } from "./endpoints/cipher";
import { compareEndpoints } from "./endpoints/compare";
import { editorEndpoints } from "./endpoints/editor";
import { jobEndpoints } from "./endpoints/jobs";
import { sizeEndpoints } from "./endpoints/size";
import { systemEndpoints } from "./endpoints/system";

export { WorkbenchError, pollJob } from "./request";
export type { JobRecord, RedundancyScanOptions } from "./request";

export const api = {
  ...systemEndpoints,
  ...codecEndpoints,
  ...editorEndpoints,
  ...jobEndpoints,
  ...compareEndpoints,
  ...cipherEndpoints,
  ...sizeEndpoints,
};
