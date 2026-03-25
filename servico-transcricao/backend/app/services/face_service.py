# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Face recognition service.

Uses DeepFace with the ArcFace model and MTCNN detector for identity
verification and face image validation.
"""

import glob
import logging
import os

from deepface import DeepFace

from app.config import IMAGE_FOLDER

logger = logging.getLogger(__name__)


def authenticate_face_multi(
    captura_path: str,
    image_folder: str = IMAGE_FOLDER,
) -> bool:
    """Verify *captura_path* against all registered face images.

    Searches *image_folder* for files matching ``registered_*.jpg`` and
    runs ArcFace verification against each one.  Returns ``True`` as soon
    as any registered image matches.

    Args:
        captura_path: Path to the captured face image to verify.
        image_folder: Directory containing registered face images.

    Returns:
        ``True`` if the face matches at least one registered image,
        ``False`` if no match is found or no images are registered.
    """
    pattern = os.path.join(image_folder, "registered_*.jpg")
    refs = glob.glob(pattern)
    if not refs:
        return False

    for ref in refs:
        try:
            res = DeepFace.verify(
                ref,
                captura_path,
                enforce_detection=True,
                model_name="ArcFace",
                detector_backend="mtcnn",
            )
            if res.get("verified"):
                return True
        except Exception:
            continue

    return False


def validate_single_face(image_path: str) -> bool:
    """Check that *image_path* contains exactly one detectable face.

    Uses MTCNN for face detection.  The image file is expected to already
    exist at *image_path* when this function is called.

    Args:
        image_path: Path to the image file to validate.

    Returns:
        ``True`` if exactly one face is detected, ``False`` otherwise
        (zero faces, multiple faces, or detection failure).
    """
    try:
        faces = DeepFace.extract_faces(img_path=image_path, detector_backend="mtcnn")
        return len(faces) == 1
    except Exception:
        return False
