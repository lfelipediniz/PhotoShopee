"""
main.py - servidor HTTP do PhotoShopee

nome: Luiz Felipe Diniz Costa
usp: 13782032
curso: SCC0251 - Processamento de Imagens
ano/semestre: 2026/1
título: PhotoShopee - Servidor de Processamento de Imagens

o que isso faz: expõe um POST /process que recebe imagem em base64 + parâmetros,
manda pro módulo image_processing e devolve a imagem processada de novo em base64.
"""

import base64
import io
import imageio.v3 as iio
import numpy as np
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from image_processing import TransformSettings, apply_all_transformations

app = FastAPI(title="PhotoShopee Backend")


class ProcessRequest(BaseModel):
    image: str
    settings: dict


class ProcessResponse(BaseModel):
    image: str


def decode_base64_to_numpy(image_b64: str) -> np.ndarray:
    """decodifica a string base64 que o front manda e vira array numpy (formato que o imageio entende)."""
    img_bytes = base64.b64decode(image_b64)
    return iio.imread(io.BytesIO(img_bytes))


def ensure_rgba_uint8(image: np.ndarray) -> np.ndarray:
    """
    permite com que o RGBA uint8: cinza vira RGB copiando o canal, RGB ganha alpha 255.
    assim o resto do pipeline sempre trabalha no mesmo formato.
    """
    if image.ndim == 2:
        rgba = np.stack([image, image, image, np.full_like(image, 255)], axis=-1)
        return rgba.astype(np.uint8)
    if image.shape[2] == 3:
        alpha = np.full((*image.shape[:2], 1), 255, dtype=np.uint8)
        return np.concatenate([image, alpha], axis=-1).astype(np.uint8)
    return image.astype(np.uint8)


def encode_numpy_png_to_base64(image: np.ndarray) -> str:
    """empacota o array final em PNG na memória e volta pra base64 (o front espera isso)."""
    buf = io.BytesIO()
    iio.imwrite(buf, image, extension=".png")
    return base64.b64encode(buf.getvalue()).decode("ascii")


@app.post("/process", response_model=ProcessResponse)
async def process_image(req: ProcessRequest):
    """rota principal: decodifica → normaliza → aplica transformações → codifica de volta."""
    image = decode_base64_to_numpy(req.image)
    image = ensure_rgba_uint8(image)

    settings = TransformSettings.from_dict(req.settings)
    result = apply_all_transformations(image, settings)

    return ProcessResponse(image=encode_numpy_png_to_base64(result))


@app.get("/health")
async def health():
    """só pra saber se o servidor tá no ar (útil em deploy / debug)."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
