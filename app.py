from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import os
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageOps
import zipfile
import io

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
ENHANCED_FOLDER = None

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def enhance_image(input_path, output_path):

    try:
        with Image.open(input_path) as img:
            img = img.convert("RGB")

            img = ImageOps.autocontrast(img, cutoff=3)


            brightness_enhancer = ImageEnhance.Brightness(img)
            img = brightness_enhancer.enhance(1.1)


            contrast_enhancer = ImageEnhance.Contrast(img)
            img = contrast_enhancer.enhance(1.3)
            sharpness_enhancer = ImageEnhance.Sharpness(img)
            img = sharpness_enhancer.enhance(2.0)

            upscale_factor = 2
            width, height = img.size
            img = img.resize((width * upscale_factor, height * upscale_factor), Image.Resampling.LANCZOS)


            img.save(output_path)
    except Exception as e:
        print(f"Erro ao aprimorar a imagem: {e}")
        raise ValueError("Erro ao processar a imagem.") from e

@app.route('/', methods=['GET', 'POST'])
def index():
    global ENHANCED_FOLDER
    if request.method == 'POST':
        enhanced_folder = request.form.get('output_directory')
        if enhanced_folder:
            if not os.path.isdir(enhanced_folder):
                os.makedirs(enhanced_folder, exist_ok=True)
            ENHANCED_FOLDER = enhanced_folder
            flash(f"Diretório configurado: {ENHANCED_FOLDER}")
        else:
            flash("Por favor, insira um diretório válido.")
    return render_template('index.html', enhanced_folder=ENHANCED_FOLDER)

@app.route('/upload', methods=['POST'])
def upload():
    if ENHANCED_FOLDER is None:
        flash("Por favor, configure o diretório de saída antes de fazer o upload.")
        return redirect(url_for('index'))

    if 'file' not in request.files:
        flash("Nenhum arquivo enviado.")
        return redirect(request.url)

    files = request.files.getlist('file')

    enhanced_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(input_path)

            enhanced_filename = f"imagem_aprimorada_{filename}"
            output_path = os.path.join(ENHANCED_FOLDER, enhanced_filename)

            try:
                enhance_image(input_path, output_path)
                enhanced_files.append(enhanced_filename)
            except ValueError as e:
                flash(str(e))
                return redirect(url_for('index'))

    if not enhanced_files:
        flash('Nenhuma imagem válida foi processada.')
        return redirect(url_for('index'))

    return redirect(url_for('show_images', filenames=",".join(enhanced_files)))

@app.route('/show_images/<filenames>')
def show_images(filenames):
    filenames = filenames.split(",")
    return render_template('show_image.html', filenames=filenames)

@app.route('/download/<filename>')
def download(filename):
    try:
        image_path = os.path.join(ENHANCED_FOLDER, filename)
        return send_file(image_path, as_attachment=True)
    except FileNotFoundError:
        return 'Arquivo não encontrado', 404

@app.route('/download_all')
def download_all():
    if ENHANCED_FOLDER is None:
        return 'Diretório de saída não configurado', 400

    try:
        # Criar um arquivo ZIP na memória
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zf:
            for filename in os.listdir(ENHANCED_FOLDER):
                file_path = os.path.join(ENHANCED_FOLDER, filename)
                zf.write(file_path, arcname=filename)

        memory_file.seek(0)
        return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='imagens_processadas.zip')
    except Exception as e:
        return f"Erro ao criar arquivo ZIP: {e}", 500


app.run(host="0.0.0.0", port=5000)

