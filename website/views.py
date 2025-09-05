import shutil
import os
import logging
from docx2pdf import convert
from flask import Blueprint, request, render_template, redirect, url_for, Response
from werkzeug.utils import secure_filename
from .models import compare_exams, create_exam, retrieve_exam
from io import BytesIO
from .services_chat import get_openAI_response, modes_of_operation
from .services_format import create_document
from .models import add_exam_data
from .views_utils import get_uploaded_file, save_upload, docx_to_pdf

views = Blueprint('views', __name__)
log = logging.getLogger(__name__)

@views.route('/', methods=['GET', 'POST'])
def home():  
    """
    Loads the home page template

    Returns:
        Renders the 'home.html' template
    """ 

    return render_template('home.html')

@views.route('/procesar', methods=['POST'])
def procesar():
    """
        Takes the input file and sends it to the OpenAI to be evaluated

        POST: Processes the input file and obtains a result from the OpenAI API to be rendered in the home page

        Parameters:
            request.files['fileUpload']: file to be evaluated

        Returns:
            If POST, render home page with the result and new pdf;
            else, redirects to home page
    """

    UPLOAD_FOLDER = './fileCache'
    os.makedirs("fileCache", exist_ok=True)

    file, filename, extension = get_uploaded_file(request, "fileUpload")
    path = save_upload(file, filename, UPLOAD_FOLDER)

    if extension == ".docx":
        pdf_out = os.path.join(UPLOAD_FOLDER, os.path.splitext(filename)[0] + ".pdf")
        docx_to_pdf(path, pdf_out)
        pdf_for_model = pdf_out
    else:
        pdf_for_model = path

    departamento = request.form.get('departamento', '')
    profesor = request.form.get('profesor', '')
    materia = request.form.get('materia', '')
    fecha = request.form.get('fecha', '')
    action = request.form.get('action', '')
    exam = {}

    if action != '':
        log.info(f"Sending request with: path={pdf_for_model} & action={action}")
        result = get_openAI_response(pdf_for_model, action)
        log.info(f"Document to be stored:\n{result}")
        if isinstance(result, list):
            log.info(f"Registering exam with {len(result)} questions")
        exam['lista_preguntas'] = result
        add_exam_data(exam, departamento, materia, profesor, fecha)
        id_obj = create_exam(exam, action)
        log.info("Exam successfully processed")

    try:
        shutil.rmtree(UPLOAD_FOLDER)
        log.info("Temporary upload folder deleted successfully.")
    except Exception as e:
        log.error(f"Error deleting upload folder: {e}")

    return render_template('home.html', resultado=id_obj, action=action)

@views.route('/validar', methods=['POST'])
def validar():
    """
        Takes the input file and sends it to the OpenAI to be evaluated and then compare it with a previous results

        POST: Processes the input file and obtains a result from comparing the previous document and the current one

        Parameters:
            request.files['fileUpload']: file to be evaluated

        Returns:
            If POST, render home page with the results;
            else, redirects to home page
    """

    UPLOAD_FOLDER = './fileCache'
    os.makedirs("fileCache", exist_ok=True)

    recent_id = request.form.get('recentId', '')
    if recent_id != "Most recent document ID":
        file, filename, extension = get_uploaded_file(request, "fileUpload")
        path = save_upload(file, filename, UPLOAD_FOLDER)

        if extension == ".docx":
            pdf_out = os.path.join(UPLOAD_FOLDER, os.path.splitext(filename)[0] + ".pdf")
            docx_to_pdf(path, pdf_out)
            pdf_for_model = pdf_out
        else:
            pdf_for_model = path

        action = request.form.get('action', '')
        exam = {}

        if action != '':
            log.info(f"Sending request with: path={pdf_for_model} & action={action}")
            result = get_openAI_response(pdf_for_model, action)
            log.info(f"Document to be stored:\n{result}")
            exam['lista_preguntas'] = result
            exam[f'{action}_id'] = recent_id
            id_obj = create_exam(exam, action)

        exam1 = retrieve_exam(id_obj, action)
        action_not_used = [value for value in modes_of_operation if value != action][0]
        exam2 = retrieve_exam(recent_id, action_not_used)

        evalua = compare_exams(exam1, exam2)
        log.info("Exam successfully validated")

        try:
            shutil.rmtree(UPLOAD_FOLDER)
            log.info("Temporary upload folder deleted successfully.")
        except Exception as e:
            log.error(f"Error deleting upload folder: {e}")

        return render_template('home.html', resultado=id_obj, action=action, validar=True, evalua=evalua)
    
    return render_template('home.html')

@views.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    """
        Generates a pdf of the input file with the correct answers formated

        Returns:
            The bytes from a buffer where the pdf is stored
    """

    id1 = request.args.get('id')
    action = request.args.get('action')

    dicc = retrieve_exam(id1, action)
    action_not_used = [value for value in modes_of_operation if value != action][0]

    buffer = BytesIO()
    create_document('titulo', dicc['lista_preguntas'], buffer)
    buffer.seek(0)
    response = Response(buffer.getvalue(), mimetype='application/pdf')

    validar = request.args.get('validar')
    if validar and (action_not_used in dicc):
        dicc2 = retrieve_exam(dicc[action_not_used])
        correct, total = compare_exams(dicc, dicc2)
        return response, [correct, total]

    return response


