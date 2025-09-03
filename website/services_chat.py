from openai import OpenAI
import base64
import os
import json
import fitz
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('AISERVICE_KEY'))
modes_of_operation = ["examAI", "examProf"]

def get_openAI_response(file_path: str, action: str, chosen_model = "o4-mini"):
    """
    Given the path to a file, calls the OpenAI Api to solve or validate a given exam. Default model
    can be changed. Be aware they do not have all the same capabilities.

    Args:
        file_path (str): path where the file is stored
        action (str): helps determine with which instructions complete the prompt
        chosen_model (str): model to be called in the OpenAI API

    Returns:
        (list) List with dictionaries containing the responses using the format given by the prompt
    """
    file = client.files.create(
        file=open(file_path, "rb"),
        purpose="user_data",)

    response = client.responses.create(
        model=chosen_model,
        input=[
            {
                "role": "system",
                "content": [
                    { "type": "input_text", "text": _action_preamble(action) + _common_exam_instructions() }
                ]
            },
            {
                "role": "user",
                "content": [
                    {"type": "input_file", "file_id": file.id}
                ]
            }
        ]
    )

    output_text = getattr(response, "output_text", None)
    if output_text is None:
        pieces = []
        for item in getattr(response, "output", []) or []:
            for c in getattr(item, "content", []) or []:
                if c.get("type") == "output_text" and "text" in c:
                    pieces.append(c["text"])
        output_text = "".join(pieces)

    try:
        return _extract_json_list(output_text)
    except Exception:
        return []

def _action_preamble(action: str):
    if action == "resolver":
        return ("Eres un solucionador de examenes universitarios que tiene que responder ciertas preguntas utilizando las imagenes provistas.")
    else:
        return ("Eres el encargado de guardar de examenes universitarios utilizando las imagenes provistas.")
    
def _common_exam_instructions():
    return """Las preguntas recibidas pueden ser de opcion multiple, completar la oracion, o verdadero y falso. Considera que ciertas preguntas pueden ser abiertas para que tu las completes. Si no tienes opciones, responde con tus conocimientos. 
            Regresa diccionarios de python para cada pregunta presente en la imagen con la siguiente información:
            - 'texto', su 'numero', otra lista con las 4 'opciones' y la 'respuesta_correcta'
            Recuerda que puede haber preguntas que consistan en una oracion que debas completar, por lo que debes dejar las opciones vacias, pero debes de proveer una respuesta.
            Tu respuesta debe ser una lista de python que contenga todos los diccionarios generados por pregunta asegurate que sea un formato JSON valido. Asegurate de usar las llaves
            de la manera como se te indico. Si no hay preguntas en la imagen, devuelve una cadena vacia, pero considera que oraciones incompletas pueden ser preguntas para completar con alguna frase. No incluyas nada extra en tu respuesta,
            inicia y termina la respuesta con los corchetes de apertura o cierre, segun corresponda. En caso de una pregunta abierta, escribe la respuesta de una manera
            breve y deja vacio el campo de opciones del diccionario. Para las respuestas de problemas matematicos usa LATEX. No incluyas la parte donde indicas que es un json.
            """   


def _extract_json_list(text: str):
    if not text or text.strip() == '""':
        return []
    text = text.strip()
    left, right = text.find("["), text.rfind("]")
    if left == -1 or right == -1 or right < left:
        return json.loads(text)
    return json.loads(text[left:right+1])            