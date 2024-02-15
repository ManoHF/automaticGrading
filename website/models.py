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

def compare_exams(dicc1: dict, dicc2: dict):
    correct = 0
    total = 0

    for questions1, questions2 in zip(dicc1['lista_preguntas'], dicc2['lista_preguntas']):
        if questions1['respuesta_correcta'] == questions2['respuesta_correcta']:
            correct += 1
        total += 1

    return correct, total



