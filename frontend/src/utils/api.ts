import type { TransformSettings } from "./imageTransformations";

const API_BASE = "/api";

export async function processImage(
  imageBase64: string,
  settings: TransformSettings,
  signal?: AbortSignal,
): Promise<string> {
  const res = await fetch(`${API_BASE}/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: imageBase64, settings }),
    signal,
  });

  if (!res.ok) {
    throw new Error(`Erro no processamento: ${res.status}`);
  }

  const data = await res.json();
  return data.image as string;
}
