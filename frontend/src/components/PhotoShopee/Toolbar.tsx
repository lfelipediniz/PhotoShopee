import {
  Upload,
  Download,
  RotateCcw,
  Move,
  Maximize,
  Crop,
  Sun,
  Zap,
} from "lucide-react";

interface ToolbarProps {
  onUpload: () => void;
  onDownload: () => void;
  onReset: () => void;
  hasImage: boolean;
  activeTool: string;
  onToolSelect: (tool: string) => void;
}

const tools = [
  { id: "translate", icon: Move, label: "Translação" },
  { id: "rotate", icon: RotateCcw, label: "Rotação" },
  { id: "scale", icon: Maximize, label: "Escala" },
  { id: "intensity", icon: Sun, label: "Intensidade" },
  { id: "effects", icon: Zap, label: "Efeitos" },
];

export function Toolbar({
  onUpload,
  onDownload,
  onReset,
  hasImage,
  activeTool,
  onToolSelect,
}: ToolbarProps) {
  return (
    <div className="flex flex-col w-12 bg-card border-r border-border items-center py-2 gap-1 shrink-0">
      {/* Upload */}
      <button
        onClick={onUpload}
        className="flex items-center justify-center w-9 h-9 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground transition-colors"
        title="Upload imagem"
      >
        <Upload size={18} />
      </button>

      {/* Download */}
      <button
        onClick={onDownload}
        disabled={!hasImage}
        className="flex items-center justify-center w-9 h-9 rounded-md hover:bg-accent text-muted-foreground hover:text-foreground transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        title="Download imagem"
      >
        <Download size={18} />
      </button>

      <div className="w-6 h-px bg-border my-1" />

      {/* Tools */}
      {tools.map((tool) => (
        <button
          key={tool.id}
          onClick={() => onToolSelect(tool.id)}
          disabled={!hasImage}
          className={`flex items-center justify-center w-9 h-9 rounded-md transition-colors disabled:opacity-30 disabled:cursor-not-allowed ${
            activeTool === tool.id
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-accent hover:text-foreground"
          }`}
          title={tool.label}
        >
          <tool.icon size={18} />
        </button>
      ))}

      <div className="flex-1" />

      {/* Reset */}
      <button
        onClick={onReset}
        disabled={!hasImage}
        className="flex items-center justify-center w-9 h-9 rounded-md hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
        title="Resetar tudo"
      >
        <RotateCcw size={16} />
      </button>
    </div>
  );
}
