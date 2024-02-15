from flask import Blueprint, request, render_template, redirect, url_for, Response, render_template_string
from werkzeug.utils import secure_filename
from .services import get_chatGPT_response, extract_text_from_file, create_document, add_exam_data
from .models import create_exam_chat, retrieve_exam_chat, create_exam_prof, retrieve_exam_prof, compare_exams
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
def validar():
    if request.method == 'POST':
       
        action = request.form.get('action', '')
        recent_id = request.form.get('recentId', '')
        if recent_id != "":
            if action == 'checkChat':
                dicc2 = retrieve_exam_chat(recent_id)
            else:
                dicc2 = retrieve_exam_prof(recent_id)
            

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
                    dict_res['prof_exam_id'] = recent_id
                    id_obj = create_exam_chat(dict_res)

                elif action == 'uploadAnswers':
                    result = get_chatGPT_response(file_text, True)
                    dict_res = eval(result)
                    #add_exam_data(dict_res, departamento, materia, profesor, fecha)
                    dict_res['ai_exam_id'] = recent_id
                    id_obj = create_exam_prof(dict_res)

                return render_template('home.html', resultado=id_obj, action=action, validar=True)
    
    return render_template('home.html')

@views.route('/generate_pdf', methods=['GET'])
def generate_pdf():
    id1 = request.args.get('id')
    action = request.args.get('action')

    if action == 'checkChat':
        dicc = retrieve_exam_chat(id1)
        if 'prof_exam_id' in dicc:
            dicc2 = retrieve_exam_prof(dicc['prof_exam_id'])
    else:
        dicc = retrieve_exam_prof(id1)
        if 'ai_exam_id' in dicc:
            dicc2 = retrieve_exam_chat(dicc['ai_exam_id'])

    validar = request.args.get('validar')
    if validar:
        correct, total = compare_exams(dicc, dicc2)
        return f"Evaluacion: {correct}/{total}"


    buffer = BytesIO()
    create_document(dicc['titulo'], dicc['lista_preguntas'], buffer)
    buffer.seek(0)

    return Response(buffer.getvalue(), mimetype='application/pdf')


