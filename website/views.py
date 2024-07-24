from flask import Blueprint, request, render_template, redirect, url_for, Response, render_template_string
from werkzeug.utils import secure_filename
from .models import create_exam_chat, retrieve_exam_chat, create_exam_prof, retrieve_exam_prof, compare_exams
from io import BytesIO
from .services_chat import get_chatgpt_image_response, add_exam_data, create_document
import os
from docx2pdf import convert
import pythoncom

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():   
    return render_template('home.html')

@views.route('/procesar', methods=['POST'])
def procesar():
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
                pythoncom.CoInitialize()
                convert(file_path, pdf_file_path)
                pythoncom.CoUninitialize()
                #file.save(pdf_file_path)
                os.remove(file_path)
                file_path = pdf_file_path
            else:
                file.save(file_path)

            action = request.form.get('action', '')
            exam = {}

            if action == 'checkChat':
                result = get_chatgpt_image_response(file_path)
                exam['lista_preguntas'] = result
                add_exam_data(exam, departamento, materia, profesor, fecha)
                id_obj = create_exam_chat(exam)

            elif action == 'uploadAnswers':
                result = get_chatgpt_image_response(file_path)
                exam['lista_preguntas'] = result
                add_exam_data(exam, departamento, materia, profesor, fecha)
                id_obj = create_exam_prof(exam)

            os.remove(file_path)

            return render_template('home.html', resultado=id_obj, action=action)
    
    return redirect(url_for('views.home'))

@views.route('/validar', methods=['POST'])
def validar():
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
                    #file.save(pdf_file_path)
                    os.remove(file_path)
                    file_path = pdf_file_path
                else:
                    file.save(file_path)

                exam = {}

                if action == 'checkChat':
                    result = get_chatgpt_image_response(file_path)
                    exam['lista_preguntas'] = result
                    #add_exam_data(dict_res, departamento, materia, profesor, fecha)
                    exam['prof_exam_id'] = recent_id
                    id_obj = create_exam_chat(exam)

                elif action == 'uploadAnswers':
                    result = get_chatgpt_image_response(file_path)
                    exam['lista_preguntas'] = result
                    #add_exam_data(dict_res, departamento, materia, profesor, fecha)
                    exam['ai_exam_id'] = recent_id
                    id_obj = create_exam_prof(exam)

                evalua = compare_exams(id_obj, recent_id, action)

                return render_template('home.html', resultado=id_obj, action=action, validar=True, evalua=evalua)
    
    return render_template('home.html')

@views.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    id1 = request.args.get('id')
    action = request.args.get('action')

    if action == 'checkChat':
        dicc = retrieve_exam_chat(id1)
        #if 'prof_exam_id' in dicc:
        #    dicc2 = retrieve_exam_prof(dicc['prof_exam_id'])
    else:
        dicc = retrieve_exam_prof(id1)
        #if 'ai_exam_id' in dicc:
        #    dicc2 = retrieve_exam_chat(dicc['ai_exam_id'])

    buffer = BytesIO()
    create_document('titulo', dicc['lista_preguntas'], buffer)
    buffer.seek(0)
    response = Response(buffer.getvalue(), mimetype='application/pdf')

    #validar = request.args.get('validar')
    #if validar:
    #    correct, total = compare_exams(dicc, dicc2)
    #    return response, [correct, total]

    return response


