"""
image_processing.py - todas as manipulações de pixel do PhotoShopee

nome: Luiz Felipe Diniz Costa
usp: 13782032
curso: SCC0251 - Processamento de Imagens
ano/semestre: 2026/1
título: PhotoShopee - Módulo de Processamento de Imagens

ideia geral: cada função abaixo faz UMA coisa (translação, gamma, etc.) e recebe/devolve
numpy RGBA. no final o apply_all_transformations junta tudo na ordem certa.
"""

import numpy as np
from scipy.ndimage import map_coordinates
from dataclasses import dataclass


@dataclass
class TransformSettings:
    """espelha os sliders/campos do frontend; from_dict ignora chave que não existe aqui."""
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


# --- parte 1: geometria (move, gira, escala, recorte) ---

def apply_translation(image: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """
    desloca a imagem; uso np.roll com wrap - o que “sai” de um lado entra do outro
    (tipo cilindro/toro, não fica borda preta).
    """
    shift_x = int(round(dx))
    shift_y = int(round(dy))
    result = np.roll(image, shift_y, axis=0)
    result = np.roll(result, shift_x, axis=1)
    return result


def apply_rotation(image: np.ndarray, angle_degrees: float) -> np.ndarray:
    """
    rotação no centro. backward mapping: pra cada pixel de saída eu pergunto de onde
    viria no original (map_coordinates). ângulo em graus, convertido pra rad.
    """
    h, w = image.shape[:2]
    angle_rad = np.radians(angle_degrees)
    cos_a = np.cos(-angle_rad)
    sin_a = np.sin(-angle_rad)

    cx, cy = w / 2.0, h / 2.0

    yy, xx = np.mgrid[0:h, 0:w]
    dx = xx - cx
    dy = yy - cy

    # inversa da rotação → posição na imagem fonte
    src_x = dx * cos_a - dy * sin_a + cx
    src_y = dx * sin_a + dy * cos_a + cy

    src_x = np.clip(src_x, 0, w - 1)
    src_y = np.clip(src_y, 0, h - 1)

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
    """redimensiona por vizinho mais próximo (índices arredondados, bem direto)."""
    h, w = image.shape[:2]
    new_w = max(1, int(round(w * scale_x)))
    new_h = max(1, int(round(h * scale_y)))

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
    """recorte retangular; .copy() pra não compartilhar memória com o array maior."""
    return image[crop_y : crop_y + crop_h, crop_x : crop_x + crop_w].copy()


# --- parte 2: intensidade (negativo, log, gamma, contraste, neon) ---


def apply_negative(image: np.ndarray) -> np.ndarray:
    """inverte RGB: 255 - R,G,B; alpha fica como tá."""
    result = image.copy()
    result[..., :3] = 255 - image[..., :3]
    return result


def apply_log(image: np.ndarray, strength: float) -> np.ndarray:
    """
    compressão log nos tons (útil pra esticar sombras). strength mistura original × resultado
    (0 = não muda, 1 = só o log).
    """
    c = 255.0 / np.log(256)
    rgb = image[..., :3].astype(np.float64)
    log_val = c * np.log1p(rgb)
    blended = rgb * (1 - strength) + log_val * strength
    result = image.copy()
    result[..., :3] = np.clip(np.round(blended), 0, 255).astype(np.uint8)
    return result


def apply_gamma(image: np.ndarray, gamma: float) -> np.ndarray:
    """lut 0..255 - mais rápido que aplicar potência pixel a pixel."""
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
    estica/comprime contraste: entrada [in_min, in_max] mapeia linear pra [out_min, out_max].
    também vira LUT pra ficar uniforme em todos os pixels.
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
    efeito “neon matrix”: cada canal tem uma curva diferente (R/G/B com fórmulas próprias),
    depois mistura com a imagem original conforme strength.
    """
    c_log = 255.0 / np.log(1 + 1.5 * 255)
    i_vals = np.arange(256, dtype=np.float64)

    r_base = 0.2 * i_vals + 0.05 * i_vals * np.sin(i_vals * np.pi / 32)
    lut_r = np.clip(np.round(r_base), 0, 255).astype(np.uint8)

    g_norm = i_vals / 255.0
    g_sigmoid = 1.0 / (1.0 + np.exp(-6.0 * (g_norm - 0.5)))
    g_wave = 0.8 + 0.2 * np.sin(i_vals * np.pi / 20)
    lut_g = np.clip(np.round(255 * g_sigmoid * g_wave), 0, 255).astype(np.uint8)

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


# --- pipeline: ordem importa (geometria antes, intensidade depois) ---


def apply_all_transformations(
    image: np.ndarray, settings: TransformSettings
) -> np.ndarray:
    """
    chama as funções de cima conforme os valores em settings. se quiser achar cada efeito,
    é só seguir os nomes: apply_translation, apply_rotation, etc.
    """
    result = image

    if settings.translateX != 0 or settings.translateY != 0:
        result = apply_translation(result, settings.translateX, settings.translateY)

    if settings.rotation != 0:
        result = apply_rotation(result, settings.rotation)

    if settings.scaleX != 1 or settings.scaleY != 1:
        result = apply_scale(result, settings.scaleX, settings.scaleY)

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
