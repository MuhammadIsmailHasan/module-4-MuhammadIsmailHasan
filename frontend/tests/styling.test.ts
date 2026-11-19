import { readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const ROOT = path.resolve(import.meta.dirname, "..");

function files(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const full = path.join(dir, name);
    return statSync(full).isDirectory() ? files(full) : full.endsWith(".tsx") ? [full] : [];
  });
}

const sources = [...files(path.join(ROOT, "components")), ...files(path.join(ROOT, "app"))].map((file) => ({
  file: path.relative(ROOT, file),
  text: readFileSync(file, "utf8"),
}));

describe("styling rules (Decision H)", () => {
  it("has no hex colours in components or pages", () => {
    const bad = sources.filter((s) => /#[0-9a-fA-F]{3,8}\b/.test(s.text.replace(/&#\d+;/g, ""))).map((s) => s.file);
    expect(bad).toEqual([]);
  });

  it("uses no arbitrary-value utilities (state selectors like data-[state=open] are allowed)", () => {
    const stateSelectors = /(?:group-|peer-)?(?:data|aria|has)-\[[^\]]*\]/g;
    const arbitrary = /(?<![\w-])[a-z][a-z0-9-]*-\[[^\]]+\]/;
    const bad = sources.filter((s) => arbitrary.test(s.text.replace(stateSelectors, ""))).map((s) => s.file);
    expect(bad).toEqual([]);
  });

  it("has no magic numbers: z-index, duration, opacity, ring and outline come from named token utilities", () => {
    const magic = /(?<![\w-])(?:z|duration|opacity|ring|outline|border)-(?!0\b|100\b)\d+\b|(?<![\w-])bg-[a-z-]+\/\d+/;
    const bad = sources.filter((s) => magic.test(s.text.replace(/zoom-in-95/g, ""))).map((s) => s.file);
    expect(bad).toEqual([]);
  });

  it("imports the shadcn/ui primitives only from components/shared and components/ui", () => {
    const bad = sources
      .filter((s) => !s.file.startsWith("components/shared") && !s.file.startsWith(path.join("components", "ui")))
      .filter((s) => /from\s+["']@\/components\/ui\//.test(s.text))
      .map((s) => s.file);
    expect(bad).toEqual([]);
  });

  it("uses no raw <button> outside the shadcn/ui primitives and the shared components", () => {
    const bad = sources
      .filter((s) => !s.file.startsWith(path.join("components", "ui")) && !s.file.startsWith(path.join("components", "shared")))
      .filter((s) => /<button[\s>]/.test(s.text))
      .map((s) => s.file);
    expect(bad).toEqual([]);
  });

  it("never strips a layout down with a max-* breakpoint variant", () => {
    const bad = sources.filter((s) => /\bmax-(lg|md|sm|xl):/.test(s.text)).map((s) => s.file);
    expect(bad).toEqual([]);
  });
});
