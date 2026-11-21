import Image from "next/image";
import { cn } from "@/lib/utils";

/** The files and their viewBox sizes (Req 21.3, 21.6). `unoptimized`: Next.js does not optimize SVG. */
const FILES = {
  mark: { src: "/brand/logo-revo.svg", width: 480, height: 480, max: "max-w-logo-mark" },
  full: { src: "/brand/logo-text-revo.svg", width: 540, height: 165, max: "max-w-logo-full" },
} as const;

const HEIGHT = { sm: "h-logo-sm", md: "h-logo-md", lg: "h-logo-lg" } as const;

interface BrandLogoProps {
  /** `mark` is the symbol alone; `full` is the symbol with the wordmark. */
  variant: keyof typeof FILES;
  size?: keyof typeof HEIGHT;
  /** Next to visible RevoTask text, or inside a control that has its own name: empty alt text. */
  decorative?: boolean;
  className?: string;
}

/** The only place the RevoTask logo is drawn. A Server Component: no state, no handlers. */
export function BrandLogo({ variant, size = "md", decorative = false, className }: BrandLogoProps) {
  const file = FILES[variant];
  return (
    <Image
      src={file.src}
      width={file.width}
      height={file.height}
      alt={decorative ? "" : "RevoTask"}
      unoptimized
      loading="eager"
      className={cn("w-auto shrink-0", HEIGHT[size], file.max, className)}
    />
  );
}
