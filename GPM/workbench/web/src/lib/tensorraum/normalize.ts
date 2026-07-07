import type { CommentStyle } from "./types";

export function stripCommentsAware(code: string, commentStyle: CommentStyle): string {
  if (commentStyle === "none") return code;
  let commentPattern: string;
  if (commentStyle === "hash") commentPattern = "#.*";
  else if (commentStyle === "sql") commentPattern = "--.*|\\/\\*[\\s\\S]*?\\*\\/";
  else commentPattern = "\\/\\/.*|\\/\\*[\\s\\S]*?\\*\\/";
  const regex = new RegExp(
    '"(?:\\\\[\\s\\S]|[^"\\\\])*"|' +
      "'(?:\\\\[\\s\\S]|[^'\\\\])*'|" +
      "`(?:\\\\[\\s\\S]|[^`\\\\])*`|" +
      commentPattern,
    "g",
  );
  return code.replace(regex, (m) => (/^["'`]/.test(m) ? m : ""));
}

export function normalizeSourceCode(code: string): string {
  const clean = code;
  return clean
    .replace(/ß/g, "ẞ")
    .toUpperCase()
    .replace(/Ä/g, "AE")
    .replace(/Ö/g, "OE")
    .replace(/Ü/g, "UE")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}
