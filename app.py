from flask import Flask, render_template, request, redirect, url_for, send_file
import os
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ENHANCED_FOLDER'] = 'static/enhanced'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Criar diretórios, se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ENHANCED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def enhance_image(input_path, output_path):
    try:
        with Image.open(input_path) as img:
            img = img.convert("RGB")

            # Aplicar aprimoramentos
            img = ImageOps.autocontrast(img)
            brightness_enhancer = ImageEnhance.Brightness(img)
            img = brightness_enhancer.enhance(1.1)
            img = img.filter(ImageFilter.DETAIL)
            sharpness_enhancer = ImageEnhance.Sharpness(img)
            img = sharpness_enhancer.enhance(3.0)
            contrast_enhancer = ImageEnhance.Contrast(img)
            img = contrast_enhancer.enhance(1.5)

            # Salvar imagem aprimorada
            img.save(output_path)
    except Exception as e:
        print(f"Erro ao aprimorar a imagem: {e}")
        raise ValueError("Erro ao carregar a imagem.") from e

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        print("Nenhum arquivo enviado.")
        return redirect(request.url)

    files = request.files.getlist('file')  # Obter lista de arquivos

    enhanced_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(input_path)

            enhanced_filename = f"imagem_renderizada_{filename}"
            output_path = os.path.join(app.config['ENHANCED_FOLDER'], enhanced_filename)

            try:
                enhance_image(input_path, output_path)
                enhanced_files.append(enhanced_filename)  # Adicionar nome à lista
            except ValueError as e:
                return str(e)

    if not enhanced_files:
        return 'Nenhuma imagem válida foi processada.'

    return redirect(url_for('show_images', filenames=",".join(enhanced_files)))

@app.route('/show_images/<filenames>')
def show_images(filenames):
    filenames = filenames.split(",")
    return render_template('show_image.html', filenames=filenames)

@app.route('/download/<filename>')
def download(filename):
    try:
        image_path = os.path.join(app.config['ENHANCED_FOLDER'], filename)
        return send_file(image_path, as_attachment=True)
    except FileNotFoundError:
        return 'Arquivo não encontrado', 404

if __name__ == '__main__':
    app.run(debug=True)
