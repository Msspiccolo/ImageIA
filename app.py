from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

app = Flask (__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ENHANCED_FOLDER'] = 'static/enhanced/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit ('.', 1)[1].lower () in app.config['ALLOWED_EXTENSIONS']


def enhance_image(input_path, output_path, width=None, height=None):
    try:
        with Image.open (input_path) as img:
            img = img.convert ("RGB")

            img = ImageOps.autocontrast (img)
            brightness_enhancer = ImageEnhance.Brightness (img)
            img = brightness_enhancer.enhance (1.1)

            img = img.filter (ImageFilter.DETAIL)


            sharpness_enhancer = ImageEnhance.Sharpness (img)
            img = sharpness_enhancer.enhance (3.0)


            contrast_enhancer = ImageEnhance.Contrast (img)
            img = contrast_enhancer.enhance (1.5)


            if width and not height:

                aspect_ratio = img.height / img.width
                height = int (width * aspect_ratio)
            elif height and not width:

                aspect_ratio = img.width / img.height
                width = int (height * aspect_ratio)

            if width and height:
                img = img.resize ((width, height), Image.LANCZOS)

            img.save (output_path)
    except Exception as e:
        print (f"Erro ao aprimorar a imagem: {e}")
        raise ValueError ("Erro ao carregar a imagem.") from e


@app.route ('/')
def index():
    return render_template ('index.html')


@app.route ('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        print ("Nenhum arquivo enviado.")
        return redirect (request.url)

    file = request.files['file']
    width = request.form.get ('width')
    height = request.form.get ('height')

    if file and allowed_file (file.filename):
        filename = secure_filename (file.filename)
        input_path = os.path.join (app.config['UPLOAD_FOLDER'], filename)


        if not os.path.exists (app.config['UPLOAD_FOLDER']):
            os.makedirs (app.config['UPLOAD_FOLDER'])

        file.save (input_path)

        enhanced_filename = f"imagem_renderizada_{filename}"
        output_path = os.path.join (app.config['ENHANCED_FOLDER'], enhanced_filename)


        if not os.path.exists (app.config['ENHANCED_FOLDER']):
            os.makedirs (app.config['ENHANCED_FOLDER'])

        try:

            width = int (width) if width else None
            height = int (height) if height else None
            enhance_image (input_path, output_path, width, height)
        except ValueError as e:
            return str (e)

        return redirect (url_for ('show_image', filename=enhanced_filename))
    else:
        print ("Tipo de arquivo inválido.")
        return 'Erro no upload da imagem.'


@app.route ('/show_image/<filename>')
def show_image(filename):
    return render_template ('show_image.html', filename=filename)


@app.route ('/download/<filename>')
def download(filename):
    try:
        image_path = os.path.join (app.config['ENHANCED_FOLDER'], filename)
        return send_file (image_path, as_attachment=True)
    except FileNotFoundError:
        return 'Arquivo não encontrado', 404


if __name__ == '__main__':
    app.run (debug=True)
