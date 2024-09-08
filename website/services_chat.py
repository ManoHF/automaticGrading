import openai
import base64
import os
import json
import fitz
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')

def encode_image(image_path):
    """
    Reads an image from a given path and encodes it using base64 to then decoded
    with utf-8.

    Args:
        image_path (str): path where the image is stored

    Returns:
        (str) Regular string representation of the image
    """

    with open(image_path, "rb") as image_file:
        # Read the image file
        image_data = image_file.read()
        
        # Encode the image data to base64
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        return encoded_image

def generate_image_list(file_path):
    """
    Given the path to a file, turns each page into an image, formats it and appends
    it to a list

    Args:
        file_path (str): path where the file is stored

    Returns:
        (list) List with images representing each page of the document
    """

    doc = fitz.open(file_path)  
    images_list = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap() 
        img = pix.save(f"fileCache/img{i}.png")
        encoded = encode_image(f"fileCache/img{i}.png")
        images_list.append(encoded)
        os.remove(f"fileCache/img{i}.png")

    return images_list

def get_chatgpt_image_response(file_path, chosen_model = "gpt-4-vision-preview"):
    """
    Given the path to a file, calls the OpenAI Api to solve or validate a given exam. Default model
    can be changed. Be aware they do not have all the same capabilities.

    Args:
        file_path (str): path where the file is stored
        chosen_model (str): model to be called in the OpenAI API

    Returns:
        (list) List with dictionaries containing the responses using the format given by the prompt
    """

    image_list = generate_image_list(file_path)
    responses = []

    for image in image_list:
        response = openai.chat.completions.create(model = chosen_model, 
            messages=[{"role": "system", 
                    "content": """Eres un solucionador de examenes universitarios que tiene que responder ciertas preguntas utilizando las imagenes provistas. 
                                  Las preguntas recibidas pueden ser de opcion multiple, completar la oracion, o verdadero y falso. Considera que ciertas preguntas pueden ser abiertas para que tu las completes. Si no tienes opciones, responde con tus conocimientos. 
                                  Regresa diccionarios de python para cada pregunta presente en la imagen con la siguiente información:
                                   - 'texto', su 'numero', otra lista con las 4 'opciones' y la 'respuesta_correcta'
                                  Recuerda que puede haber preguntas que consistan en una oracion que debas completar, por lo que debes dejar las opciones vacias, pero debes de proveer una respuesta.
                                  Tu respuesta debe ser una lista de python que contenga todos los diccionarios generados por pregunta asegurate que sea un formato JSON valido. Asegurate de usar las llaves
                                  de la manera como se te indico. Si no hay preguntas en la imagen, devuelve una cadena vacia, pero considera que oraciones incompletas pueden ser preguntas para completar con alguna frase. No incluyas nada extra en tu respuesta,
                                  inicia y termina la respuesta con los corchetes de apertura o cierre, segun corresponda. En caso de una pregunta abierta, escribe la respuesta de una manera
                                  breve y deja vacio el campo de opciones del diccionario. Para las respuestas de problemas matematicos usa LATEX. No incluyas la parte donde indicas que es un json.
                               """               
                    },
                    { "role": "user",
                     "content": [
                                  {"type": "image_url",
                                   "image_url": { "url": f"data:image/jpeg;base64,{image}", },
                                  }, ],
                   }
            ], max_tokens=4000
        )

        resp = response.choices[0].message.content
        left, right = 0, len(resp)-1

        if resp != '""':
            while resp[left] != "[":
                left = left + 1
            while resp[right] != "]":
                right = right - 1

            currList = json.loads(resp[left:right+1])
            responses.extend(currList)

    return responses