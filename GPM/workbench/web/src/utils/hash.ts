/** SHA-256 content key matching server `content_hash_key` (json sort_keys). */

export async function contentHashKey(
  mode: string,
  profile: string,
  text: string,
  languageId?: string | null,
): Promise<string> {
  const payload = JSON.stringify({
    language_id: languageId ?? null,
    mode,
    profile,
    text,
  });
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(payload));
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function debounce<T extends (...args: never[]) => void>(fn: T, ms: number): T {
  let timer: ReturnType<typeof setTimeout> | null = null;
  return ((...args: Parameters<T>) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  }) as T;
}
