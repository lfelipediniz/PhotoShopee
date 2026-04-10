import type { TransformSettings } from "@/utils/imageTransformations";

interface PropertiesPanelProps {
  settings: TransformSettings;
  onChange: (settings: TransformSettings) => void;
  activeTool: string;
  hasImage: boolean;
  imageWidth: number;
  imageHeight: number;
}

function SliderControl({
  label,
  value,
  min,
  max,
  step,
  onChange,
  unit,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
  unit?: string;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between items-center">
        <span className="text-xs text-muted-foreground">{label}</span>
        <span className="text-xs font-mono text-foreground">
          {step < 1 ? value.toFixed(2) : value}
          {unit ?? ""}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full"
      />
    </div>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-xs font-semibold text-primary uppercase tracking-wider mb-2">
      {children}
    </h3>
  );
}

export function PropertiesPanel({
  settings,
  onChange,
  activeTool,
  hasImage,
  imageWidth,
  imageHeight,
}: PropertiesPanelProps) {
  const update = (partial: Partial<TransformSettings>) => {
    onChange({ ...settings, ...partial });
  };

  if (!hasImage) {
    return (
      <div className="w-64 bg-card border-l border-border p-4 flex items-center justify-center shrink-0">
        <p className="text-xs text-muted-foreground text-center">
          Faça upload de uma imagem para começar
        </p>
      </div>
    );
  }

  return (
    <div className="w-64 bg-card border-l border-border p-3 overflow-y-auto shrink-0">
      <div className="mb-3">
        <h2 className="text-sm font-bold text-foreground">Propriedades</h2>
        <p className="text-[10px] text-muted-foreground mt-0.5">
          {imageWidth} × {imageHeight}px
        </p>
      </div>

      <div className="space-y-4">
        {/* Translate */}
        {activeTool === "translate" && (
          <div>
            <SectionTitle>Translação</SectionTitle>
            <div className="space-y-3">
              <SliderControl
                label="Eixo X"
                value={settings.translateX}
                min={-imageWidth}
                max={imageWidth}
                step={1}
                onChange={(v) => update({ translateX: v })}
                unit="px"
              />
              <SliderControl
                label="Eixo Y"
                value={settings.translateY}
                min={-imageHeight}
                max={imageHeight}
                step={1}
                onChange={(v) => update({ translateY: v })}
                unit="px"
              />
            </div>
          </div>
        )}

        {/* Rotate */}
        {activeTool === "rotate" && (
          <div>
            <SectionTitle>Rotação</SectionTitle>
            <SliderControl
              label="Ângulo"
              value={settings.rotation}
              min={0}
              max={360}
              step={1}
              onChange={(v) => update({ rotation: v })}
              unit="°"
            />
          </div>
        )}

        {/* Scale */}
        {activeTool === "scale" && (
          <div>
            <SectionTitle>Escala</SectionTitle>
            <div className="space-y-3">
              <SliderControl
                label="Escala X"
                value={settings.scaleX}
                min={0.1}
                max={3}
                step={0.05}
                onChange={(v) => update({ scaleX: v })}
                unit="×"
              />
              <SliderControl
                label="Escala Y"
                value={settings.scaleY}
                min={0.1}
                max={3}
                step={0.05}
                onChange={(v) => update({ scaleY: v })}
                unit="×"
              />
            </div>
          </div>
        )}

        {/* Intensity */}
        {activeTool === "intensity" && (
          <div className="space-y-4">
            <div>
              <SectionTitle>Negativo</SectionTitle>
              <button
                onClick={() => update({ negative: !settings.negative })}
                className={`w-full py-1.5 px-3 rounded text-xs font-medium transition-colors ${
                  settings.negative
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-secondary-foreground hover:bg-accent"
                }`}
              >
                {settings.negative ? "Ativado" : "Desativado"}
              </button>
            </div>

            <div>
              <SectionTitle>Transformação Log</SectionTitle>
              <SliderControl
                label="Intensidade"
                value={settings.logStrength}
                min={0}
                max={1}
                step={0.05}
                onChange={(v) => update({ logStrength: v })}
              />
            </div>

            <div>
              <SectionTitle>Correção Gamma</SectionTitle>
              <SliderControl
                label="Gamma"
                value={settings.gamma}
                min={0.1}
                max={5}
                step={0.05}
                onChange={(v) => update({ gamma: v })}
              />
            </div>

            <div>
              <SectionTitle>Modulação de Contraste</SectionTitle>
              <div className="space-y-3">
                <SliderControl
                  label="Min Entrada"
                  value={settings.contrastInMin}
                  min={0}
                  max={254}
                  step={1}
                  onChange={(v) => update({ contrastInMin: v })}
                />
                <SliderControl
                  label="Max Entrada"
                  value={settings.contrastInMax}
                  min={1}
                  max={255}
                  step={1}
                  onChange={(v) => update({ contrastInMax: v })}
                />
                <SliderControl
                  label="Min Saída"
                  value={settings.contrastOutMin}
                  min={0}
                  max={254}
                  step={1}
                  onChange={(v) => update({ contrastOutMin: v })}
                />
                <SliderControl
                  label="Max Saída"
                  value={settings.contrastOutMax}
                  min={1}
                  max={255}
                  step={1}
                  onChange={(v) => update({ contrastOutMax: v })}
                />
              </div>
            </div>
          </div>
        )}

        {/* Effects */}
        {activeTool === "effects" && (
          <div>
            <SectionTitle>Efeito Neon Matrix</SectionTitle>
            <SliderControl
              label="Intensidade"
              value={settings.neonStrength}
              min={0}
              max={1}
              step={0.05}
              onChange={(v) => update({ neonStrength: v })}
            />
            <p className="text-[10px] text-muted-foreground mt-2 leading-relaxed">
              Enfatiza canais verde e azul com mapeamento não-linear e faixas de
              contraste abruptas (estilo cyberpunk).
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
