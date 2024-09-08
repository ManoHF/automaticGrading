from . import conn
from bson.objectid import ObjectId

db = conn.db

def create_exam_chat(exam: dict):
    return db.examChat.insert_one(exam).inserted_id

def create_exam_prof(exam: dict):
    return db.examProf.insert_one(exam).inserted_id

def retrieve_exam_chat(id: str):
    objInstance = ObjectId(id)
    return db.examChat.find_one(objInstance)

def retrieve_exam_prof(id: str):
    objInstance = ObjectId(id)
    return db.examProf.find_one(objInstance)

def compare_exams(id1: str, id2: str, action:str):
    if action == 'checkChat':
        dicc_chat = retrieve_exam_chat(id1)
        dicc_prof = retrieve_exam_prof(id2)
    else:
        dicc_chat = retrieve_exam_chat(id2)
        dicc_prof = retrieve_exam_prof(id1)

    correct = 0
    total = 0

    for questions1, questions2 in zip(dicc_chat['lista_preguntas'], dicc_prof['lista_preguntas']):
        if questions1['respuesta_correcta'] == questions2['respuesta_correcta']:
            correct += 1
        total += 1

    return [correct, total]

def add_exam_data(doc: dict, departamento: str, materia: str, profesor: str, fecha: str):
    if departamento != "":
        doc['departamento'] = departamento

    if materia != "":
        doc['materia'] = materia

    if profesor != "":
        doc['profesor'] = profesor
    
    if fecha != "":
        doc['fecha'] = fecha



