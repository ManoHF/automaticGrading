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



