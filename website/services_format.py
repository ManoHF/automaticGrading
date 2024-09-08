from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable, ListItem
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

from io import BytesIO


def create_document(title: str, questions: list, buffer: BytesIO, department='', date=''):
    """
    Defines the more general characteristics of the document such as pagesize and margins. Then it adds
    all the questions with the correct answers formatted.

    Args:
        title (str): title of the document
        questions (list): list of questions present in the document
        buffer (BytesIO): buffer where the information will be retrieved
        department (str): department that made the exam, default=''
        date (str): date, default=''
    """

    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=1.9*cm, leftMargin=1.9*cm, 
                      topMargin=1.9*cm, bottomMargin=1.9*cm)
    
    # General information of the document
    document = []
    add_initial_info(document, [department, date])
    add_title(document, title)

    # Body of the document
    for question in questions:
        add_paragraph(document, question['texto'])
        correcta = question["respuesta_correcta"]
        add_bullets(document, question['opciones'], correcta)

    doc.build(document)


def add_initial_info(doc: list,  info: list, font = 'Helvetica', font_size=20, align= TA_RIGHT):
    """
    Add relevant information at the top right of given document that is given as a list. It can format alignment and
    font size. Alignment options include: TA_LEFT, TA_CENTER or TA_CENTRE, TA_RIGHT and TA_JUSTIFY

    Args:
        doc (list): document that will receive the title
        title (str): title of the document
        font (str): font for the title, default='Helvetica'
        font_size (int): size for the title, default=20
        align (enum): alignment, default=TA_RIGHT
    """

    for txt in info:
        if txt != '':
            doc.append(Paragraph(txt, ParagraphStyle(name=f'info {txt}', fontFamily=font, fontSize=font_size, alignment=align)))
            doc.append(Spacer(1, 1*cm))

    doc.append(Spacer(1, 1*cm))

def add_title(doc: list, title: str, font = 'Helvetica', font_size=36, align= TA_CENTER):
    """
    Add a title to the given document that is given as a list. It can format alignment and
    font size. Alignment options include: TA_LEFT, TA_CENTER or TA_CENTRE, TA_RIGHT and TA_JUSTIFY

    Args:
        doc (list): document that will receive the title
        title (str): title of the document
        font (str): font for the title, default='Helvetica'
        font_size (int): size for the title, default=36
        align (enum): alignment, default=TA_CENTER
    """

    doc.append(Paragraph(title, ParagraphStyle(name='title', fontFamily=font, fontSize=font_size, alignment=align)))
    doc.append(Spacer(1, 1*cm))

def add_paragraph(doc: list, text: str):
    """
    Appends paragraphs to the new document using the newline character as a separator

    Args:
        doc (str): document where the lines will be appended
        text (str): paragraphs of the exam
    """

    for line in text.split('\n'):
        doc.append(Paragraph(line))
        doc.append(Spacer(1, 0.5*cm))

def add_bullets(doc: list, options_list: list, correct_ans: str):
    """
    Appends the questions options as bullet points with the correct one highlighted

    Args:
        doc (list): document where the lines will be appended
        options_list (str): list containing the options for the question
        correct_ans (str): correct answer for the question
    """

    items = []
    for option in options_list:
        if option == correct_ans:
            highlight_line(doc, option, items)
        else:
            items.append(ListItem(Paragraph(option)))

    # If the list is empty, then the question must be open
    if not items:
        highlight_line(doc, correct_ans)
    else:
        lista_items = ListFlowable(items, bulletType='bullet', start='bulletchar', bulletFontSize=10)
        doc.append(lista_items)

    doc.append(Spacer(1, 0.5*cm))

def highlight_line(doc: list, option: str, items = []):
    """
    Highlights the corresponding line to be added to the document

    Args:
        doc (list): document where the lines will be appended
        option (str): piece of text to be highlighted
        items (list): list containing different options for the question
    """

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']

    highlighted_style = normal_style.clone('highlighted')
    highlighted_style.backColor = colors.yellow

    if not items:
        doc.append(Paragraph(option, highlighted_style))
    else:
        items.append(ListItem(Paragraph(option, highlighted_style)))