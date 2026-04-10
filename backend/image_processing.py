"""
Nome: Luiz Felipe Diniz Costa
USP: 13782032
Curso: SCC0251 - Processamento de Imagens
Semestre: 2025/1
Título: PhotoShopee - Módulo de Processamento de Imagens

Módulo contendo TODAS as funções de manipulação de pixels para o PhotoShopee.
Cada função recebe um array numpy RGBA e retorna um novo array transformado.
"""

import numpy as np
from scipy.ndimage import map_coordinates
from dataclasses import dataclass


@dataclass
class TransformSettings:
    """Parseia o dict de settings enviado pelo frontend."""
    translateX: float = 0
    translateY: float = 0
    rotation: float = 0
    scaleX: float = 1
    scaleY: float = 1
    negative: bool = False
    logStrength: float = 0
    gamma: float = 1
    contrastInMin: float = 0
    contrastInMax: float = 255
    contrastOutMin: float = 0
    contrastOutMax: float = 255
    neonStrength: float = 0

    @classmethod
    def from_dict(cls, d: dict) -> "TransformSettings":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ============================================================================
# 1. TRANSFORMAÇÕES GEOMÉTRICAS
# ============================================================================


def apply_translation(image: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """
    Translação com wrap-around toroidal usando np.roll.
    Move a imagem dx pixels no eixo X e dy pixels no eixo Y.
    """
    shift_x = int(round(dx))
    shift_y = int(round(dy))
    result = np.roll(image, shift_y, axis=0)
    result = np.roll(result, shift_x, axis=1)
    return result


def apply_rotation(image: np.ndarray, angle_degrees: float) -> np.ndarray:
    """
    Rotação em torno do centro usando backward mapping com scipy.ndimage.map_coordinates.
    Edge clamping para pixels fora dos limites.
    """
    h, w = image.shape[:2]
    angle_rad = np.radians(angle_degrees)
    cos_a = np.cos(-angle_rad)
    sin_a = np.sin(-angle_rad)

    cx, cy = w / 2.0, h / 2.0

    # Coordenadas de destino
    yy, xx = np.mgrid[0:h, 0:w]

    # Translada para centro como origem
    dx = xx - cx
    dy = yy - cy

    # Rotação inversa para encontrar pixel fonte
    src_x = dx * cos_a - dy * sin_a + cx
    src_y = dx * sin_a + dy * cos_a + cy

    # Edge clamping
    src_x = np.clip(src_x, 0, w - 1)
    src_y = np.clip(src_y, 0, h - 1)

    # Aplica para cada canal
    output = np.empty_like(image)
    for c in range(image.shape[2]):
        output[..., c] = map_coordinates(
            image[..., c],
            [src_y, src_x],
            order=0,
            mode="nearest",
        )

    return output


def apply_scale(image: np.ndarray, scale_x: float, scale_y: float) -> np.ndarray:
    """
    Escala usando nearest-neighbor com indexação numpy.
    """
    h, w = image.shape[:2]
    new_w = max(1, int(round(w * scale_x)))
    new_h = max(1, int(round(h * scale_y)))

    # Mapeamento inverso
    col_indices = np.clip(np.round(np.arange(new_w) / scale_x).astype(int), 0, w - 1)
    row_indices = np.clip(np.round(np.arange(new_h) / scale_y).astype(int), 0, h - 1)

    return image[np.ix_(row_indices, col_indices)]


def apply_crop(
    image: np.ndarray,
    crop_x: int,
    crop_y: int,
    crop_w: int,
    crop_h: int,
) -> np.ndarray:
    """
    Crop (recorte) de uma região retangular usando slicing numpy.
    """
    return image[crop_y : crop_y + crop_h, crop_x : crop_x + crop_w].copy()


# ============================================================================
# 2. FUNÇÕES DE TRANSFORMAÇÃO DE INTENSIDADE
# ============================================================================


def apply_negative(image: np.ndarray) -> np.ndarray:
    """
    Negativo: inverte os canais RGB preservando alpha.
    f(x) = 255 - x
    """
    result = image.copy()
    result[..., :3] = 255 - image[..., :3]
    return result


def apply_log(image: np.ndarray, strength: float) -> np.ndarray:
    """
    Transformação logarítmica com controle de intensidade.
    f(x) = c * log(1 + x), onde c = 255 / log(256)
    O strength interpola entre original e transformado.
    """
    c = 255.0 / np.log(256)
    rgb = image[..., :3].astype(np.float64)
    log_val = c * np.log1p(rgb)
    blended = rgb * (1 - strength) + log_val * strength
    result = image.copy()
    result[..., :3] = np.clip(np.round(blended), 0, 255).astype(np.uint8)
    return result


def apply_gamma(image: np.ndarray, gamma: float) -> np.ndarray:
    """
    Correção gamma com LUT de 256 entradas.
    f(x) = 255 * (x/255)^gamma
    """
    lut = np.clip(
        np.round(255.0 * np.power(np.arange(256) / 255.0, gamma)), 0, 255
    ).astype(np.uint8)

    result = image.copy()
    result[..., :3] = lut[image[..., :3]]
    return result


def apply_contrast_modulation(
    image: np.ndarray,
    in_min: float,
    in_max: float,
    out_min: float = 0,
    out_max: float = 255,
) -> np.ndarray:
    """
    Modulação de contraste (contrast stretching) com LUT.
    Mapeia [inMin, inMax] -> [outMin, outMax] linearmente.
    """
    in_range = max(in_max - in_min, 1)
    out_range = out_max - out_min

    lut = np.empty(256, dtype=np.uint8)
    for i in range(256):
        clamped = np.clip(i, in_min, in_max)
        lut[i] = np.clip(
            round(out_min + (clamped - in_min) * out_range / in_range), 0, 255
        )

    result = image.copy()
    result[..., :3] = lut[image[..., :3]]
    return result


def apply_neon_matrix(image: np.ndarray, strength: float) -> np.ndarray:
    """
    Efeito Neon Matrix - 3 LUTs por canal.
    Canal R: atenuação + seno
    Canal G: sigmoid + onda
    Canal B: log + cosseno
    """
    c_log = 255.0 / np.log(1 + 1.5 * 255)
    i_vals = np.arange(256, dtype=np.float64)

    # Canal R: atenuação + modulação sutil
    r_base = 0.2 * i_vals + 0.05 * i_vals * np.sin(i_vals * np.pi / 32)
    lut_r = np.clip(np.round(r_base), 0, 255).astype(np.uint8)

    # Canal G: sigmoide + ondulação senoidal
    g_norm = i_vals / 255.0
    g_sigmoid = 1.0 / (1.0 + np.exp(-6.0 * (g_norm - 0.5)))
    g_wave = 0.8 + 0.2 * np.sin(i_vals * np.pi / 20)
    lut_g = np.clip(np.round(255 * g_sigmoid * g_wave), 0, 255).astype(np.uint8)

    # Canal B: log intensificado + modulação cossenoidal
    b_log = c_log * np.log(1 + 1.5 * i_vals)
    b_wave = 0.7 + 0.3 * np.cos(i_vals * np.pi / 15)
    lut_b = np.clip(np.round(b_log * b_wave), 0, 255).astype(np.uint8)

    rgb = image[..., :3].astype(np.float64)
    neon = np.empty_like(rgb)
    neon[..., 0] = lut_r[image[..., 0]]
    neon[..., 1] = lut_g[image[..., 1]]
    neon[..., 2] = lut_b[image[..., 2]]

    blended = rgb * (1 - strength) + neon * strength

    result = image.copy()
    result[..., :3] = np.clip(np.round(blended), 0, 255).astype(np.uint8)
    return result


# ============================================================================
# PIPELINE
# ============================================================================


def apply_all_transformations(
    image: np.ndarray, settings: TransformSettings
) -> np.ndarray:
    """
    Aplica todas as transformações configuradas em sequência.
    Ordem: geométricas primeiro, depois intensidade.
    """
    result = image

    # 1. Transformações Geométricas
    if settings.translateX != 0 or settings.translateY != 0:
        result = apply_translation(result, settings.translateX, settings.translateY)

    if settings.rotation != 0:
        result = apply_rotation(result, settings.rotation)

    if settings.scaleX != 1 or settings.scaleY != 1:
        result = apply_scale(result, settings.scaleX, settings.scaleY)

    # 2. Transformações de Intensidade
    if settings.negative:
        result = apply_negative(result)

    if settings.logStrength > 0:
        result = apply_log(result, settings.logStrength)

    if settings.gamma != 1:
        result = apply_gamma(result, settings.gamma)

    if (
        settings.contrastInMin != 0
        or settings.contrastInMax != 255
        or settings.contrastOutMin != 0
        or settings.contrastOutMax != 255
    ):
        result = apply_contrast_modulation(
            result,
            settings.contrastInMin,
            settings.contrastInMax,
            settings.contrastOutMin,
            settings.contrastOutMax,
        )

    if settings.neonStrength > 0:
        result = apply_neon_matrix(result, settings.neonStrength)

    return result
