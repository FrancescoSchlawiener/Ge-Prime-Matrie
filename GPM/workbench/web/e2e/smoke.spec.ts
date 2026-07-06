import { test, expect } from "@playwright/test";

test("smoke: OG tabs codec → vergleichen → gpm compile", async ({ page }) => {
  await page.goto("/#/codec/encodieren");
  await expect(page.getByTestId("nav-codec")).toBeVisible();

  await page.getByRole("button", { name: /Encodieren/i }).click();
  await expect(page.getByText("HALLO")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText("WELT")).toBeVisible();
  await expect(page.getByText("Original")).toBeVisible();
  await expect(page.getByRole("button", { name: /S & I zum Decodieren/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /Speichergröße vergleichen/i }).first()).toBeVisible();
  await expect(page.getByRole("button", { name: /Speichergröße aller Wörter vergleichen/i })).toBeVisible();
  await expect(page.getByText(/Normalisierung|Substanz S/i).first()).toBeVisible();

  await page.goto("/#/codec/decodieren");
  await page.getByLabel(/Substanz S/i).fill("372945");
  await page.getByLabel(/Index I/i).fill("13");
  await page.getByRole("button", { name: /^Decodieren$/i }).click();
  await expect(page.getByText("HALLO")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByTestId("size-decode-btn")).toBeVisible();

  await page.goto("/#/vergleichen/wortpaar");
  await expect(page.getByText(/Wortpaar/i)).toBeVisible();
  await page.getByRole("button", { name: /Vergleichen \(ggT\/kgV\)/i }).click();
  await page.getByRole("button", { name: /^Vergleichen$/i }).click();
  await expect(page.getByText(/LISTEN/i)).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText(/SILENT/i)).toBeVisible();
  await expect(page.getByRole("button", { name: /Speichergröße beider Wörter vergleichen/i })).toBeVisible();
  await expect(page.getByRole("button", { name: /S & I zum Decodieren/i }).first()).toBeVisible();

  await page.getByRole("button", { name: /^Anagramm$/i }).click();
  await page.getByRole("button", { name: /Anagramme suchen/i }).click();
  await expect(page.getByText(/Anagramm-Treffer|Keine weiteren Anagramme/i)).toBeVisible({ timeout: 15_000 });

  await page.goto("/#/gpm");
  await expect(page.getByTestId("compile")).toBeVisible({ timeout: 20_000 });
  await page.getByTestId("compile").click();

  await page.goto("/#/vergleichen/ikurve");
  await expect(page.getByText(/Index-Vektoren|I-Kurve/i)).toBeVisible();
  const textareas = page.locator("textarea");
  await textareas.nth(0).fill("HALLO WELT");
  await textareas.nth(1).fill("WELT HALLO");
  await page.getByRole("button", { name: /^Analysieren$/i }).click();
  await expect(
    page.getByText(/Struktur-Kreuzvalidierung|Wort-Geometrie/i).first(),
  ).toBeVisible({ timeout: 30_000 });
  await expect(page.getByText(/Geometrische Matrix/i)).toBeVisible();
});
