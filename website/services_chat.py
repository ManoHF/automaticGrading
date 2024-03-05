import openai
import base64
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def get_chatgpt_text_response(model: str, content: dict, role: int):
    if role == 0:
        dict_role = {"role": "system", 
                    "content": """Eres un solucionador de examenes que tiene que responder ciertas preguntas. Determina
                                  la respuesta correcta y regresa como respuesta diccionario de python que contenga 
                                  los siguientes tres elementos:
                                  - 'texto': todo el contenido antes de las cuatro opciones de respuesta
                                  - una lista con las 4 'opciones'
                                  - 'respuesta_correcta'
                                  Utiliza las palabras entre comillas como las llaves del diccionario
                               """}
    if role == 1:
        dict_role = {"role": "system", 
                    "content": """Eres un verificador de examenes que tiene que evaluar ciertas preguntas. Regresa una respuesta
                                  formateada como diccionario de python que contenga los siguientes tres elementos:
                                  - 'texto': todo el contenido antes de las cuatro opciones de respuesta
                                  - una lista con las 4 'opciones'
                                  - 'respuesta_correcta': dada en el documento
                                  Utiliza las palabras entre comillas como las llaves del diccionario. No intentes resolver la pregunta
                               """}

    response = openai.chat.completions.create(
        model=model,
        messages=[dict_role, content] )
    
    return response.choices[0].message.content

def get_chatgpt_image_response(content: str, image_path: str):
    base64_image = encode_image(image_path)

    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[ {"role": "system", 
                    "content": """Eres un solucionador de examenes que tiene que responder ciertas preguntas. Determina
                                  la respuesta correcta y regresa como respuesta diccionario de python que contenga 
                                  los siguientes tres elementos:
                                  - 'texto': todo el contenido antes de las cuatro opciones de respuesta, sin contar la imagen
                                  - una lista con las 4 'opciones'
                                  - 'respuesta_correcta'
                                  Utiliza las palabras entre comillas como las llaves del diccionario
                               """},
                   { "role": "user",
                     "content": [ {"type": "text", "text": content},
                                  {"type": "image_url",
                                   "image_url": { "url": f"data:image/jpeg;base64,{base64_image}", },
                                  }, ],
                   }
                  ],
        max_tokens=500,
    )

    return response.choices[0].message.content

pregunta = """
Utilice las gráficas para la siguiente pregunta. 
24. En el contexto del modelo IS-LM suponga una economía cuyo Banco Central tiene el objetivo de mantener 
una tasa de interés. 
La gráfica _ representa una venta de bonos por parte del Banco Central. Como resultado de dicha 
política podemos asegurar que el ahorro privado  _ 
, la inversión _ y el precio de los bonos _
. 
a) 2; disminuye; disminuye; disminuye 
b) 1; disminuye; disminuye; disminuye 
c) 1; disminuye; aumenta; disminuye 
d) 3; aumenta; aumenta; aumenta
"""

path = "website/test_image.png"
print(get_chatgpt_image_response(pregunta, path))

