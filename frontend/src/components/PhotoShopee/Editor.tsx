import { useState, useCallback, useRef, useEffect } from "react";
import { toast } from "sonner";
import { Toolbar } from "./Toolbar";
import { PropertiesPanel } from "./PropertiesPanel";
import { ImageCanvas } from "./ImageCanvas";
import {
  defaultSettings,
  type TransformSettings,
} from "@/utils/imageTransformations";
import { processImage } from "@/utils/api";

export function Editor() {
  const [originalImageBase64, setOriginalImageBase64] = useState<string | null>(null);
  const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(null);
  const [settings, setSettings] = useState<TransformSettings>(defaultSettings);
  const [activeTool, setActiveTool] = useState("translate");
  const [imageDimensions, setImageDimensions] = useState({ w: 0, h: 0 });
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(0 as unknown as ReturnType<typeof setTimeout>);

  // Envia para o backend quando settings mudam
  useEffect(() => {
    if (!originalImageBase64) return;

    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      // Cancela request anterior em voo
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setIsLoading(true);

      processImage(originalImageBase64, settings, controller.signal)
        .then((resultBase64) => {
          setProcessedImageUrl(`data:image/png;base64,${resultBase64}`);
          setIsLoading(false);
        })
        .catch((err) => {
          if (err instanceof DOMException && err.name === "AbortError") return;
          setIsLoading(false);
          toast.error("Erro ao processar imagem. Verifique se o backend está rodando.");
        });
    }, 400);

    return () => {
      clearTimeout(debounceRef.current);
    };
  }, [originalImageBase64, settings]);

  const handleUpload = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d")!;
        ctx.drawImage(img, 0, 0);

        // Extrai base64 puro (sem o prefixo data:image/png;base64,)
        const dataUrl = canvas.toDataURL("image/png");
        const base64 = dataUrl.split(",")[1];

        setOriginalImageBase64(base64);
        setProcessedImageUrl(dataUrl);
        setImageDimensions({ w: img.width, h: img.height });
        setSettings(defaultSettings);
      };
      img.src = URL.createObjectURL(file);
    },
    []
  );

  const handleDownload = useCallback(() => {
    if (!processedImageUrl) return;
    const link = document.createElement("a");
    link.download = "photoshopee-output.png";
    link.href = processedImageUrl;
    link.click();
  }, [processedImageUrl]);

  const handleReset = useCallback(() => {
    setSettings(defaultSettings);
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Toolbar esquerda */}
      <Toolbar
        onUpload={handleUpload}
        onDownload={handleDownload}
        onReset={handleReset}
        hasImage={!!originalImageBase64}
        activeTool={activeTool}
        onToolSelect={setActiveTool}
      />

      {/* Header + Canvas */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Title bar */}
        <div className="h-9 bg-card border-b border-border flex items-center px-3 shrink-0">
          <span className="text-xs font-bold text-primary tracking-wide">
            PHOTOSHOPEE
          </span>
          <span className="text-[10px] text-muted-foreground ml-2">
            {isLoading ? "Processando..." : "Editor de Imagens"}
          </span>
        </div>

        {/* Canvas */}
        <ImageCanvas imageUrl={processedImageUrl} isLoading={isLoading} />
      </div>

      {/* Painel de propriedades direita */}
      <PropertiesPanel
        settings={settings}
        onChange={setSettings}
        activeTool={activeTool}
        hasImage={!!originalImageBase64}
        imageWidth={imageDimensions.w}
        imageHeight={imageDimensions.h}
      />
    </div>
  );
}
