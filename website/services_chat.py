import openai
import base64
import os
from io import BytesIO
import json
import fitz
from dotenv import load_dotenv
from pdf2image import convert_from_path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

load_dotenv()
openai.api_key = os.getenv('OPENAI_KEY')

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        # Read the image file
        image_data = image_file.read()
        
        # Encode the image data to base64
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        return encoded_image

def generate_image_list(file_path):

    doc = fitz.open(file_path)  
    images_list = []

    for i, page in enumerate(doc):
        pix = page.get_pixmap() 
        img = pix.save(f"fileCache/img{i}.png")
        encoded = encode_image(f"fileCache/img{i}.png")
        images_list.append(encoded)
        os.remove(f"fileCache/img{i}.png")

    return images_list

def get_chatgpt_image_response(file_path):
    image_list = generate_image_list(file_path)
    responses = []

    for image in image_list:
        response = openai.chat.completions.create(model = "gpt-4-vision-preview", 
            messages=[{"role": "system", 
                    "content": """Eres un solucionador de examenes universitarios que tiene que responder ciertas preguntas utilizando las imagenes provistas. 
                                  Las preguntas recibidas pueden ser de opcion multiple, completar la oracion, o verdadero y falso. Considera que ciertas preguntas pueden ser abiertas para que tu las completes. Si no tienes opciones, responde con tus conocimientos. 
                                  Regresa diccionarios de python para cada pregunta presente en la imagen con la siguiente información:
                                   - 'texto', su 'numero', otra lista con las 4 'opciones' y la 'respuesta_correcta'
                                  Recuerda que puede haber preguntas que consistan en una iracion que debas completar, por lo que debes dejar las opciones vacias, pero debes de proveer una respuesta.
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

def add_exam_data(doc: dict, departamento: str, materia: str, profesor: str, fecha: str):
    if departamento != "":
        doc['departamento'] = departamento

    if materia != "":
        doc['materia'] = materia

    if profesor != "":
        doc['profesor'] = profesor
    
    if fecha != "":
        doc['fecha'] = fecha

def create_document(titulo: str, preguntas: list, buffer: BytesIO, departmento='', examen='', fecha=''):

    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=1.9*cm, leftMargin=1.9*cm, 
                      topMargin=1.9*cm, bottomMargin=1.9*cm)
    document = []
    add_title(document, titulo)
    for preg in preguntas:
        add_paragraph(document, preg['texto'])
        correcta = preg["respuesta_correcta"]
        add_bullets(document, preg['opciones'], correcta)

    doc.build(document)

def add_title(doc: list, title: str, font = 'Helvetica', font_size=36, align= TA_CENTER):
    doc.append(Paragraph(title, ParagraphStyle(name='title', fontFamily=font, fontSize=font_size, alignment=align)))
    doc.append(Spacer(1, 1*cm))

def add_paragraph(doc: list, text: str):
    for line in text.split('\n'):
        doc.append(Paragraph(line))
        doc.append(Spacer(1, 0.5*cm))

def add_bullets(doc: list, lista: list, correcta: str):
    items = []
    for it in lista:
        items.append(ListItem(Paragraph(it)))

    lista_items = ListFlowable(items, bulletType='bullet', start='bulletchar', bulletFontSize=10)

    doc.append(lista_items)
    doc.append(Spacer(1, 0.5*cm))

