# Overview, V11 changes

V11 adds Decision X and Requirement 21 (branding). It changes no API, data model, or permission. Everything else in `specs/v10/00-OVERVIEW.md` stands, including Decisions K to W (the V10 round 3 snapshot is applied separately).

## Decisions Log (added)

| ID | Decision | Rationale | Where applied |
|----|----------|-----------|---------------|
| X | **RevoTask logo and favicon (V11; changes Decision I wording only).** The favicon is `app/favicon.ico` (Next.js file convention, no manual `<link>`); the two logos live in `public/brand/` and are shown only through the shared `BrandLogo` component using `next/image` with `unoptimized` (Next.js does not optimize SVG and rejects it by default). Display sizes never exceed the `viewBox` (480 and 540 CSS pixels wide), so the Embedded_Raster is not enlarged. Only `favicon.ico` is supplied: no `icon`, `apple-icon`, or web manifest in V11 (Open Question 20). The Sidebar toggle shows Logo_Full when expanded and Logo_Mark when collapsed. | The owner replaced the placeholder mark; one component keeps size, alt text, and file paths in one place. | Req 21, Req 14.16, 14.19, Req 15.28 |

## Glossary (added)

- **Brand_Assets**: The three files the product owner supplied in V11: `favicon.ico`, `logo-revo.svg`, and `logo-text-revo.svg`. After the move: `frontend/app/favicon.ico`, `frontend/public/brand/logo-revo.svg`, and `frontend/public/brand/logo-text-revo.svg`.
- **Logo_Mark**: `logo-revo.svg`, the square mark, `viewBox` 480 by 480.
- **Logo_Full**: `logo-text-revo.svg`, the mark with the "RevoTask" wordmark, `viewBox` 540 by 165.
- **BrandLogo**: The only Frontend component that renders a Logo_Mark or Logo_Full (`components/shared/BrandLogo.tsx`), with the variants `mark` and `full`. Feature code uses it and never writes its own `<img>` or `next/image` for the logo.
- **Embedded_Raster**: The base64 PNG that each Brand_Assets SVG file wraps inside an `<svg>` element. Measured in V11: 640 by 640 pixels in `logo-revo.svg` and 720 by 220 pixels in `logo-text-revo.svg`, 8-bit RGB with no alpha channel and no transparency chunk, so each logo has an opaque background. The `viewBox` (480 and 540 wide) is the size at which the raster is shown at about 1.33 device pixels per CSS pixel.
- **Favicon_File**: `frontend/app/favicon.ico`, a Windows icon file with three images (16, 32, and 48 pixels square, 32 bits per pixel), served by the Next.js file convention.

## Open Questions (added)

19. **Logo files are raster, not vector (V11, open):** both SVG files wrap a PNG (Glossary: Embedded_Raster), so they cannot be recoloured with CSS, will look soft above their `viewBox` size and on screens above 1.33 device pixels per CSS pixel, and ignore the dark-mode and design-token rules. Recommendation: ask the owner for true vector SVGs with a transparent background; the files can be replaced in place with the same names and `viewBox` and no code change (Req 21, criterion 16).
20. **Other icon sizes (V11, open):** only `favicon.ico` is provided. No `icon.png`, `apple-icon.png` (180 by 180, `jpg` or `png` only in Next.js), or web app manifest icons (192 and 512) exist. A 180 pixel icon could be cut from the Embedded_Raster, but that would be a derived, opaque image the owner has not approved. Recommendation: ask the owner for a square 512 pixel PNG and add `app/icon.png`, `app/apple-icon.png`, and `app/manifest.ts` in a follow-up.
21. **Opaque logo background on the brand panel (V11, open):** the Embedded_Raster has no alpha, so on the navy gradient of the login and register brand panel the logo appears as a rectangle. V11 places it on a `bg-surface-raised` tile (Req 21, criterion 9). Recommendation: ask for a transparent (or white-on-transparent) variant for dark backgrounds.
