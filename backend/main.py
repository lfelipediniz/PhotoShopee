"""
main.py

Nome: Luiz Felipe Diniz Costa
USP: 13782032
Curso: SCC0251 - Processamento de Imagens
Semestre: 2025/1
Título: PhotoShopee - Servidor de Processamento de Imagens

Servidor FastAPI que recebe imagens em base64 do frontend,
processa com numpy/scipy e retorna o resultado.
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


@app.post("/process", response_model=ProcessResponse)
async def process_image(req: ProcessRequest):
    # Decode base64 -> bytes -> numpy array
    img_bytes = base64.b64decode(req.image)
    image = iio.imread(io.BytesIO(img_bytes))

    # Normalizar para RGBA uint8
    if image.ndim == 2:
        # Grayscale -> RGBA
        rgba = np.stack([image, image, image, np.full_like(image, 255)], axis=-1)
        image = rgba
    elif image.shape[2] == 3:
        # RGB -> RGBA
        alpha = np.full((*image.shape[:2], 1), 255, dtype=np.uint8)
        image = np.concatenate([image, alpha], axis=-1)

    image = image.astype(np.uint8)

    # Parsear settings e aplicar transformações
    settings = TransformSettings.from_dict(req.settings)
    result = apply_all_transformations(image, settings)

    # Encode resultado -> PNG -> base64
    buf = io.BytesIO()
    iio.imwrite(buf, result, extension=".png")
    result_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return ProcessResponse(image=result_b64)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
