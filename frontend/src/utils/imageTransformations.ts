export interface TransformSettings {
  translateX: number;
  translateY: number;
  rotation: number;
  scaleX: number;
  scaleY: number;
  negative: boolean;
  logStrength: number;
  gamma: number;
  contrastInMin: number;
  contrastInMax: number;
  contrastOutMin: number;
  contrastOutMax: number;
  neonStrength: number;
}

export const defaultSettings: TransformSettings = {
  translateX: 0,
  translateY: 0,
  rotation: 0,
  scaleX: 1,
  scaleY: 1,
  negative: false,
  logStrength: 0,
  gamma: 1,
  contrastInMin: 0,
  contrastInMax: 255,
  contrastOutMin: 0,
  contrastOutMax: 255,
  neonStrength: 0,
};
