#!/usr/bin/env bun
/**
 * Slide image generator using Google Gemini/Imagen APIs
 * This script is specifically for ppt-generate to ensure consistent image generation
 *
 * Usage:
 *   npx -y bun generate-slide-image.ts --prompt "prompt text" --image output.png
 *   npx -y bun generate-slide-image.ts --promptfile prompt.md --image output.png --ar 16:9
 */

import path from "node:path";
import { homedir } from "node:os";
import { mkdir, readFile, writeFile } from "node:fs/promises";

// =============================================================================
// Types
// =============================================================================

type Quality = "normal" | "2k";

type CliArgs = {
  prompt: string | null;
  promptFile: string | null;
  imagePath: string | null;
  model: string | null;
  aspectRatio: string | null;
  quality: Quality;
  imageSize: string | null;
  referenceImages: string[];
  help: boolean;
};

// =============================================================================
// Google API Implementation
// =============================================================================

const GOOGLE_MULTIMODAL_MODELS = ["gemini-3-pro-image-preview", "gemini-3-flash-preview"];
const GOOGLE_IMAGEN_MODELS = ["imagen-3.0-generate-002", "imagen-3.0-generate-001"];

function getDefaultModel(): string {
  return process.env.GOOGLE_IMAGE_MODEL || "gemini-3-pro-image-preview";
}

function normalizeGoogleModelId(model: string): string {
  return model.startsWith("models/") ? model.slice("models/".length) : model;
}

function isGoogleMultimodal(model: string): boolean {
  const normalized = normalizeGoogleModelId(model);
  return GOOGLE_MULTIMODAL_MODELS.some((m) => normalized.includes(m));
}

function isGoogleImagen(model: string): boolean {
  const normalized = normalizeGoogleModelId(model);
  return GOOGLE_IMAGEN_MODELS.some((m) => normalized.includes(m));
}

function getGoogleApiKey(): string | null {
  return process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY || null;
}

function getGoogleImageSize(args: CliArgs): "1K" | "2K" | "4K" {
  if (args.imageSize) return args.imageSize as "1K" | "2K" | "4K";
  return args.quality === "2k" ? "2K" : "1K";
}

function getGoogleBaseUrl(): string {
  const base = process.env.GOOGLE_BASE_URL || "https://generativelanguage.googleapis.com";
  return base.replace(/\/+$/g, "");
}

function buildGoogleUrl(pathname: string): string {
  const base = getGoogleBaseUrl();
  const cleanedPath = pathname.replace(/^\/+/g, "");
  if (base.endsWith("/v1beta")) return `${base}/${cleanedPath}`;
  return `${base}/v1beta/${cleanedPath}`;
}

function toModelPath(model: string): string {
  const modelId = normalizeGoogleModelId(model);
  return `models/${modelId}`;
}

async function postGoogleJson<T>(pathname: string, body: unknown): Promise<T> {
  const apiKey = getGoogleApiKey();
  if (!apiKey) throw new Error("GOOGLE_API_KEY or GEMINI_API_KEY is required");

  const res = await fetch(buildGoogleUrl(pathname), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-goog-api-key": apiKey,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Google API error (${res.status}): ${err}`);
  }

  return (await res.json()) as T;
}

function buildPromptWithAspect(prompt: string, ar: string | null, quality: Quality): string {
  let result = prompt;
  if (ar) {
    result += ` Aspect ratio: ${ar}.`;
  }
  if (quality === "2k") {
    result += " High resolution 2048px.";
  }
  return result;
}

function addAspectRatioToPrompt(prompt: string, ar: string | null): string {
  if (!ar) return prompt;
  return `${prompt} Aspect ratio: ${ar}.`;
}

async function readImageAsBase64(p: string): Promise<{ data: string; mimeType: string }> {
  const buf = await readFile(p);
  const ext = path.extname(p).toLowerCase();
  let mimeType = "image/png";
  if (ext === ".jpg" || ext === ".jpeg") mimeType = "image/jpeg";
  else if (ext === ".gif") mimeType = "image/gif";
  else if (ext === ".webp") mimeType = "image/webp";
  return { data: buf.toString("base64"), mimeType };
}

function extractInlineImageData(response: {
  candidates?: Array<{ content?: { parts?: Array<{ inlineData?: { data?: string } }> } }>;
}): string | null {
  for (const candidate of response.candidates || []) {
    for (const part of candidate.content?.parts || []) {
      const data = part.inlineData?.data;
      if (typeof data === "string" && data.length > 0) return data;
    }
  }
  return null;
}

function extractPredictedImageData(response: {
  predictions?: Array<any>;
  generatedImages?: Array<any>;
}): string | null {
  const candidates = [...(response.predictions || []), ...(response.generatedImages || [])];
  for (const candidate of candidates) {
    if (!candidate || typeof candidate !== "object") continue;
    if (typeof candidate.imageBytes === "string") return candidate.imageBytes;
    if (typeof candidate.bytesBase64Encoded === "string") return candidate.bytesBase64Encoded;
    if (typeof candidate.data === "string") return candidate.data;
    const image = candidate.image;
    if (image && typeof image === "object") {
      if (typeof image.imageBytes === "string") return image.imageBytes;
      if (typeof image.bytesBase64Encoded === "string") return image.bytesBase64Encoded;
      if (typeof image.data === "string") return image.data;
    }
  }
  return null;
}

async function generateWithGemini(prompt: string, model: string, args: CliArgs): Promise<Uint8Array> {
  const promptWithAspect = addAspectRatioToPrompt(prompt, args.aspectRatio);
  const parts: Array<{ text?: string; inlineData?: { data: string; mimeType: string } }> = [];

  for (const refPath of args.referenceImages) {
    const { data, mimeType } = await readImageAsBase64(refPath);
    parts.push({ inlineData: { data, mimeType } });
  }
  parts.push({ text: promptWithAspect });

  const imageConfig: { imageSize: "1K" | "2K" | "4K" } = {
    imageSize: getGoogleImageSize(args),
  };

  console.log("Generating image with Gemini...", imageConfig);
  const response = await postGoogleJson<{
    candidates?: Array<{ content?: { parts?: Array<{ inlineData?: { data?: string } }> } }>;
  }>(`${toModelPath(model)}:generateContent`, {
    contents: [
      {
        role: "user",
        parts,
      },
    ],
    generationConfig: {
      responseModalities: ["IMAGE"],
      imageConfig,
    },
  });
  console.log("Generation completed.");

  const imageData = extractInlineImageData(response);
  if (imageData) return Uint8Array.from(Buffer.from(imageData, "base64"));

  throw new Error("No image in response");
}

async function generateWithImagen(prompt: string, model: string, args: CliArgs): Promise<Uint8Array> {
  const fullPrompt = buildPromptWithAspect(prompt, args.aspectRatio, args.quality);
  const imageSize = getGoogleImageSize(args);
  if (imageSize === "4K") {
    console.error("Warning: Imagen models do not support 4K imageSize, using 2K instead.");
  }

  const parameters: Record<string, unknown> = {
    sampleCount: 1,
  };
  if (args.aspectRatio) {
    parameters.aspectRatio = args.aspectRatio;
  }
  if (imageSize === "1K" || imageSize === "2K") {
    parameters.imageSize = imageSize;
  } else {
    parameters.imageSize = "2K";
  }

  const response = await postGoogleJson<{
    predictions?: Array<any>;
    generatedImages?: Array<any>;
  }>(`${toModelPath(model)}:predict`, {
    instances: [
      {
        prompt: fullPrompt,
      },
    ],
    parameters,
  });

  const imageData = extractPredictedImageData(response);
  if (imageData) return Uint8Array.from(Buffer.from(imageData, "base64"));

  throw new Error("No image in response");
}

async function generateImage(prompt: string, model: string, args: CliArgs): Promise<Uint8Array> {
  if (isGoogleImagen(model)) {
    if (args.referenceImages.length > 0) {
      console.error("Warning: Reference images not supported with Imagen models, ignoring.");
    }
    return generateWithImagen(prompt, model, args);
  }

  if (!isGoogleMultimodal(model) && args.referenceImages.length > 0) {
    console.error("Warning: Reference images are only supported with Gemini multimodal models.");
  }

  return generateWithGemini(prompt, model, args);
}

// =============================================================================
// CLI Implementation
// =============================================================================

function printUsage(): void {
  console.log(`Usage:
  npx -y bun generate-slide-image.ts --prompt "A slide about..." --image slide.png
  npx -y bun generate-slide-image.ts --promptfile prompt.md --image slide.png --ar 16:9

Options:
  -p, --prompt <text>       Prompt text
  --promptfile <file>       Read prompt from file
  --image <path>            Output image path (required)
  -m, --model <id>          Model ID (default: gemini-3-pro-image-preview)
  --ar <ratio>              Aspect ratio (e.g., 16:9, 1:1, 4:3)
  --quality normal|2k       Quality preset (default: 2k)
  --imageSize 1K|2K|4K      Image size (default: from quality)
  --ref <files...>          Reference images (Gemini multimodal only)
  -h, --help                Show help

Environment variables:
  GOOGLE_API_KEY            Google API key
  GEMINI_API_KEY            Gemini API key (alias for GOOGLE_API_KEY)
  GOOGLE_IMAGE_MODEL        Default Google model (gemini-3-pro-image-preview)
  GOOGLE_BASE_URL           Custom Google endpoint

Env file load order: CLI args > process.env > <cwd>/.baoyu-skills/.env > ~/.baoyu-skills/.env`);
}

function parseArgs(argv: string[]): CliArgs {
  const out: CliArgs = {
    prompt: null,
    promptFile: null,
    imagePath: null,
    model: null,
    aspectRatio: null,
    quality: "2k",
    imageSize: null,
    referenceImages: [],
    help: false,
  };

  const takeMany = (i: number): { items: string[]; next: number } => {
    const items: string[] = [];
    let j = i + 1;
    while (j < argv.length) {
      const v = argv[j]!;
      if (v.startsWith("-")) break;
      items.push(v);
      j++;
    }
    return { items, next: j - 1 };
  };

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]!;

    if (a === "--help" || a === "-h") {
      out.help = true;
      continue;
    }

    if (a === "--prompt" || a === "-p") {
      const v = argv[++i];
      if (!v) throw new Error(`Missing value for ${a}`);
      out.prompt = v;
      continue;
    }

    if (a === "--promptfile") {
      const v = argv[++i];
      if (!v) throw new Error("Missing file for --promptfile");
      out.promptFile = v;
      continue;
    }

    if (a === "--image") {
      const v = argv[++i];
      if (!v) throw new Error("Missing value for --image");
      out.imagePath = v;
      continue;
    }

    if (a === "--model" || a === "-m") {
      const v = argv[++i];
      if (!v) throw new Error(`Missing value for ${a}`);
      out.model = v;
      continue;
    }

    if (a === "--ar") {
      const v = argv[++i];
      if (!v) throw new Error("Missing value for --ar");
      out.aspectRatio = v;
      continue;
    }

    if (a === "--quality") {
      const v = argv[++i];
      if (v !== "normal" && v !== "2k") throw new Error(`Invalid quality: ${v}`);
      out.quality = v;
      continue;
    }

    if (a === "--imageSize") {
      const v = argv[++i]?.toUpperCase();
      if (v !== "1K" && v !== "2K" && v !== "4K") throw new Error(`Invalid imageSize: ${v}`);
      out.imageSize = v;
      continue;
    }

    if (a === "--ref" || a === "--reference") {
      const { items, next } = takeMany(i);
      if (items.length === 0) throw new Error(`Missing files for ${a}`);
      out.referenceImages.push(...items);
      i = next;
      continue;
    }

    if (a.startsWith("-")) {
      throw new Error(`Unknown option: ${a}`);
    }
  }

  return out;
}

async function loadEnvFile(p: string): Promise<Record<string, string>> {
  try {
    const content = await readFile(p, "utf8");
    const env: Record<string, string> = {};
    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const idx = trimmed.indexOf("=");
      if (idx === -1) continue;
      const key = trimmed.slice(0, idx).trim();
      let val = trimmed.slice(idx + 1).trim();
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      env[key] = val;
    }
    return env;
  } catch {
    return {};
  }
}

async function loadEnv(): Promise<void> {
  const home = homedir();
  const cwd = process.cwd();

  const homeEnv = await loadEnvFile(path.join(home, ".baoyu-skills", ".env"));
  const cwdEnv = await loadEnvFile(path.join(cwd, ".baoyu-skills", ".env"));

  for (const [k, v] of Object.entries(homeEnv)) {
    if (!process.env[k]) process.env[k] = v;
  }
  for (const [k, v] of Object.entries(cwdEnv)) {
    if (!process.env[k]) process.env[k] = v;
  }
}

function normalizeOutputImagePath(p: string): string {
  const full = path.resolve(p);
  const ext = path.extname(full);
  if (ext) return full;
  return `${full}.png`;
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    printUsage();
    return;
  }

  await loadEnv();

  let prompt: string | null = args.prompt;
  if (!prompt && args.promptFile) {
    prompt = await readFile(args.promptFile, "utf8");
  }

  if (!prompt) {
    console.error("Error: Prompt is required (--prompt or --promptfile)");
    printUsage();
    process.exitCode = 1;
    return;
  }

  if (!args.imagePath) {
    console.error("Error: --image is required");
    printUsage();
    process.exitCode = 1;
    return;
  }

  const apiKey = getGoogleApiKey();
  if (!apiKey) {
    console.error("Error: GOOGLE_API_KEY or GEMINI_API_KEY is required");
    console.error("Set the environment variable or create ~/.baoyu-skills/.env");
    process.exitCode = 1;
    return;
  }

  const model = args.model || getDefaultModel();
  const outputPath = normalizeOutputImagePath(args.imagePath);

  let imageData: Uint8Array;
  let retried = false;

  while (true) {
    try {
      imageData = await generateImage(prompt, model, args);
      break;
    } catch (e) {
      if (!retried) {
        retried = true;
        console.error("Generation failed, retrying...");
        continue;
      }
      throw e;
    }
  }

  const dir = path.dirname(outputPath);
  await mkdir(dir, { recursive: true });
  await writeFile(outputPath, imageData);

  console.log(`Saved: ${outputPath}`);
}

main().catch((e) => {
  const msg = e instanceof Error ? e.message : String(e);
  console.error(msg);
  process.exit(1);
});
