from flask import Blueprint, request, render_template, redirect, url_for, Response, render_template_string
from werkzeug.utils import secure_filename
from .services import get_chatGPT_response, extract_text_from_file, create_document, add_exam_data
from .models import create_exam_chat, retrieve_exam_chat, create_exam_prof, retrieve_exam_prof
from io import BytesIO

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():   
    return render_template('home.html')

@views.route('/procesar', methods=['POST'])
def procesar():
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
            content = file.read()
            file_text = extract_text_from_file(content, filename)

            action = request.form.get('action', '')

            if action == 'checkChat':
                result = get_chatGPT_response(file_text)
                dict_res = eval(result)
                add_exam_data(dict_res, departamento, materia, profesor, fecha)
                id_obj = create_exam_chat(dict_res)

            elif action == 'uploadAnswers':
                result = get_chatGPT_response(file_text, True)
                dict_res = eval(result)
                add_exam_data(dict_res, departamento, materia, profesor, fecha)
                id_obj = create_exam_prof(dict_res)

            return render_template('home.html', resultado=id_obj, action=action)
    
    return render_template('home.html')

@views.route('/validar', methods=['POST'])
def procesar():
    if request.method == 'POST':
       
        action = request.form.get('action', '')
        if action == 'checkChat':
            dicc = retrieve_exam_chat(id)
        else:
            dicc = retrieve_exam_prof(id)
        

        if 'fileUpload' not in request.files:
            return redirect(request.url)

        file = request.files['fileUpload']
        if file.filename == '':
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            content = file.read()
            file_text = extract_text_from_file(content, filename)

            if action == 'checkChat':
                result = get_chatGPT_response(file_text)
                dict_res = eval(result)
                #add_exam_data(dict_res, departamento, materia, profesor, fecha)
                id_obj = create_exam_chat(dict_res)

            elif action == 'uploadAnswers':
                result = get_chatGPT_response(file_text, True)
                dict_res = eval(result)
                #add_exam_data(dict_res, departamento, materia, profesor, fecha)
                id_obj = create_exam_prof(dict_res)

            return render_template('home.html', resultado=id_obj, action=action)
    
    return render_template('home.html')

@views.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    id = request.args.get('id')
    action = request.args.get('action')

    if action == 'checkChat':
        dicc = retrieve_exam_chat(id)
    else:
        dicc = retrieve_exam_prof(id)

    buffer = BytesIO()
    create_document(dicc['titulo'], dicc['lista_preguntas'], buffer)
    buffer.seek(0)

    return Response(buffer.getvalue(), mimetype='application/pdf')


