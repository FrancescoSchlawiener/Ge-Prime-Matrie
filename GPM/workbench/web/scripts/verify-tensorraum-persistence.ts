import {
  formatRegistryRow,
  resolvePointer,
  resolveSequencePreview,
  shortPointerId,
} from "../src/lib/tensorraum/registryDisplay";
import { registerSubstrate, createEmptyRoot } from "../src/lib/tensorraum/registry";
import {
  parseSaveJson,
  saveToJson,
  serializeProject,
  validateSave,
} from "../src/lib/tensorraum/persistence";
import { createProject } from "../src/lib/tensorraum/project";
import type { GpmProjectSave } from "../src/lib/tensorraum/persistence";

function assert(cond: unknown, msg: string): asserts cond {
  if (!cond) throw new Error(msg);
}

const project = createProject("Serialize_Test");
const root = project.root;
const ptrFn = registerSubstrate(root, "S", "function");
const ptrH = registerSubstrate(root, "H", "abc123");
root.header.hSegments?.set(ptrH, [
  { tag: "S", value: "abc" },
  { tag: "N", value: "123" },
]);

const save = serializeProject(project, "fixed", 14);
assert(validateSave(save), "serializeProject output must validate");
assert(save.settings.windowSize === 14, "window size preserved");

const roundJson = saveToJson(save);
const reparsed = parseSaveJson(roundJson);
assert(reparsed.saveId === save.saveId, "saveId roundtrip");

const manualSave: GpmProjectSave = {
  gpmSaveFormat: 1,
  saveId: "save_manual",
  projectName: "Manual",
  savedAt: new Date().toISOString(),
  settings: {
    crossLanguageAnalysis: false,
    structuralOnly: false,
    activeLanguageIds: ["js"],
    windowMode: "fixed",
    windowSize: 12,
  },
  files: [{ filename: "t.js", languageId: "js", rawCode: "var x = 1;" }],
};
assert(validateSave(manualSave), "manual save validates");
assert(!validateSave({ gpmSaveFormat: 2 }), "reject wrong format");
assert(!validateSave(null), "reject null");

const reg = root.header.registry;
assert(shortPointerId(ptrFn).startsWith("S"), "short pointer");
assert(formatRegistryRow("S", ptrFn, "function").label === "function", "format row label");
assert(resolvePointer(reg, "S", ptrFn) === "function", "resolve pointer");

const emptyRoot = createEmptyRoot("x");
const seq = [
  { t: "S" as const, p: ptrFn, nl: 0 },
  { t: "H" as const, p: ptrH, nl: 0 },
];
const preview = resolveSequencePreview(seq, reg, 8);
assert(preview.length === 2, "sequence preview includes H");
assert(preview.some((t) => t.type === "H"), "H in preview");

console.log("verify-tensorraum-persistence OK");
