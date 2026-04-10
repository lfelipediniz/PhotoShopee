interface ImageCanvasProps {
  imageUrl: string | null;
  isLoading: boolean;
}

export function ImageCanvas({ imageUrl, isLoading }: ImageCanvasProps) {
  if (!imageUrl) {
    return (
      <div className="flex-1 flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-20 h-20 mx-auto mb-4 rounded-xl bg-secondary flex items-center justify-center">
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              className="text-muted-foreground"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground">
            Clique em{" "}
            <span className="text-primary font-medium">Upload</span> para
            carregar uma imagem
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="flex-1 flex items-center justify-center bg-background overflow-auto p-4 relative"
      style={{
        backgroundImage:
          "linear-gradient(45deg, oklch(0.18 0.005 260) 25%, transparent 25%), " +
          "linear-gradient(-45deg, oklch(0.18 0.005 260) 25%, transparent 25%), " +
          "linear-gradient(45deg, transparent 75%, oklch(0.18 0.005 260) 75%), " +
          "linear-gradient(-45deg, transparent 75%, oklch(0.18 0.005 260) 75%)",
        backgroundSize: "20px 20px",
        backgroundPosition: "0 0, 0 10px, 10px -10px, -10px 0px",
      }}
    >
      <img
        src={imageUrl}
        alt="Imagem processada"
        className="max-w-full max-h-full"
        style={{ imageRendering: "auto" }}
      />

      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/50">
          <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}
