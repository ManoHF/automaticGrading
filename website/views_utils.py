import logging
import os
from werkzeug.utils import secure_filename

from .exceptions import (
    UserInputError,
    UnsupportedFileError,
    ProcessingError,
    ExternalServiceError,
)

log = logging.getLogger(__name__)
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

def _extract_extension(name: str) -> str:
    """
    Extracts the extension from a filename

    Args:
        name (str): filename

    Returns:
        extension (str): the file extension
    """
    return os.path.splitext(name)[1].lower()

def get_uploaded_file(req, field: str = "fileUpload"):
    """
    Extracts and validates a file uploaded through a Flask request.

    This function ensures that the expected file field exists in the request,
    checks that the filename is not empty, sanitizes the filename for safe
    filesystem use, and validates that the file extension is allowed.

    Args:
        req (flask.Request): the current Flask request containing uploaded files
        field (str): the name of the file field in the request (default: "fileUpload")

    Returns:
        tuple:
            file (werkzeug.datastructures.FileStorage): the uploaded file object, which can be saved or read.  
            filename (str): the sanitized filename safe for storage.  
            extension (str): the normalized file extension (e.g., ".pdf" or ".docx").  
    """
    if field not in req.files:
        raise UserInputError("No se encontró el archivo en la petición.")
    file = req.files[field]
    if not file or not file.filename.strip():
        raise UserInputError("No seleccionaste un archivo.")
    filename = secure_filename(file.filename)
    ext = _extract_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileError(f"Tipo de archivo no soportado: {ext}. Usa .pdf o .docx.")
    log.info("File successfully retrieved from field")
    return file, filename, ext

def save_upload(file_to_store, filename: str, folder: str) -> str:
    """
    Saves retrieved file into a temporary location

    Args:
        file_to_store: file to be saved
        filename (str): the name of the file
        folder (str): location to save the file

    Returns:
        str: path where file was saved
    """
    path = os.path.join(folder, filename)
    file_to_store.save(path)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise ProcessingError("No se pudo guardar el archivo subido.")
    log.info(f"File successfully saved in: {path}")
    return path

def docx_to_pdf(docx_path: str, pdf_path: str) -> str:
    """
    Converts docx document to pdf

    Args:
        docx_path (str): docx file path
        pdf_path (str): pdf file path

    Returns:
        str: path where pdf file was saved
    """
    from docx2pdf import convert 
    try:
        convert(docx_path, pdf_path)
    except Exception as e:
        raise ExternalServiceError(f"Fallo al convertir .docx a PDF: {e}") from e
    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
        raise ProcessingError("La conversión a PDF produjo un archivo vacío.")
    return pdf_path