from . import conn
from bson.objectid import ObjectId

db = conn.db

def create_exam(exam: dict, collection_name: str):
    """
    Inserts an exam document into the given collection

    Args:
        exam (dict): document in dictionary format to be inserted
        collection_name (str): name of the collection

    Returns:
        (int) Inserted id of the document
    """

    coll = db[collection_name]

    return coll.insert_one(exam).inserted_id

def retrieve_exam(id: str, collection_name: str):
    """
    Retrieves the document from the given collection and id

    Args:
        id (str): id of the document
        collection_name (str): collection where the document is stored

    Returns:
        (dicc) Document with the exam data
    """

    objInstance = ObjectId(id)
    coll = db[collection_name]

    return coll.find_one(objInstance)

def compare_exams(exam1: dict, exam2: dict):
    """
    Given two exams, compares their answers

    Args:
        exam1 (dict): first exam to compare
        exam2 (dict): second exam to compare

    Returns:
        (str) Number of matching answers and total questions
    """

    correct = 0
    total = 0

    for questions1, questions2 in zip(exam1['lista_preguntas'], exam2['lista_preguntas']):
        if questions1['respuesta_correcta'] == questions2['respuesta_correcta']:
            correct += 1
        total += 1

    return [correct, total]

def add_exam_data(exam: dict, departament: str, course: str, professor: str, date: str):
    """
    Add complemetary information to the exam document

    Args:
        exam (dict): document where the data will be added
        department (str): department that applied the exam
        course (str): course that applied the exam
        professor (str): professor that applied the exam
        date (str): date of the exam

    Returns:
        (str) Number of matching answers and total questions
    """

    if departament != "":
        exam['departamento'] = departament

    if course != "":
        exam['materia'] = course

    if professor != "":
        exam['profesor'] = professor
    
    if date != "":
        exam['fecha'] = date



