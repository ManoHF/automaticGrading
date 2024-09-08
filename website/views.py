from flask import Blueprint, request, render_template, redirect, url_for, Response
from werkzeug.utils import secure_filename
from .models import compare_exams, create_exam, retrieve_exam
from io import BytesIO
from .services_chat import get_chatgpt_image_response
from .services_format import create_document
from .models import add_exam_data
import os
from docx2pdf import convert

views = Blueprint('views', __name__)
modes_of_operation = ["examAI", "examProf"]

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

    if request.method == 'POST':
        departamento = request.form.get('departamento', '')
        profesor = request.form.get('profesor', '')
        materia = request.form.get('materia', '')
        fecha = request.form.get('fecha', '')

        if 'fileUpload' not in request.files:
            return redirect(request.url)

        file = request.files['fileUpload']

        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            if filename.lower().endswith('.docx'):
                pdf_file_path = file_path[:-5] + '.pdf'
                file.save(file_path)
                print(file_path)
                convert(file_path, pdf_file_path)
                os.remove(file_path)
                file_path = pdf_file_path
            else:
                file.save(file_path)

            action = request.form.get('action', '')
            exam = {}

            if action != '':
                result = get_chatgpt_image_response(file_path)
                exam['lista_preguntas'] = result
                add_exam_data(exam, departamento, materia, profesor, fecha)
                id_obj = create_exam(exam, action)

            os.remove(file_path)

            return render_template('home.html', resultado=id_obj, action=action)
    
    return redirect(url_for('views.home'))

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

    if request.method == 'POST':
       
        action = request.form.get('action', '')
        recent_id = request.form.get('recentId', '')
        if recent_id != "Most recent document ID":          

            if 'fileUpload' not in request.files:
                return redirect(request.url)

            file = request.files['fileUpload']
            if file.filename == '':
                return redirect(request.url)

            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)

                if filename.lower().endswith('.docx'):
                    pdf_file_path = file_path[:-5] + '.pdf'
                    file.save(file_path)
                    convert(file_path, pdf_file_path)
                    os.remove(file_path)
                    file_path = pdf_file_path
                else:
                    file.save(file_path)

                exam = {}

                if action != '':
                    result = get_chatgpt_image_response(file_path)
                    exam['lista_preguntas'] = result
                    exam[f'{action}_id'] = recent_id
                    id_obj = create_exam(exam, action)

                exam1 = retrieve_exam(id_obj, action)
                action_not_used = [value for value in modes_of_operation if value != action][0]
                exam2 = retrieve_exam(recent_id, action_not_used)

                evalua = compare_exams(exam1, exam2)

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


