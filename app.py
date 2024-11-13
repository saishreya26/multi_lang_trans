from flask import Flask, render_template, request, jsonify
from googletrans import LANGUAGES, Translator
from translator_module import translate_text, translate_file, translate_text_multiple_languages, \
    extract_text_from_pdf, extract_text_from_doc, detect_language_from_image, summarize_text

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', languages=LANGUAGES)

@app.route('/text_translate', methods=['GET', 'POST'])
def text_translate():
    if request.method == 'POST':
        text = request.form['text']
        target_language = request.form['language']
        translated_text = translate_text(text, target_language)
        return render_template('text_trans.html', translated_text=translated_text, languages=LANGUAGES)
    return render_template('text_trans.html', languages=LANGUAGES)

@app.route('/file_translate', methods=['GET', 'POST'])
def file_translate():
    translated_text = None
    if request.method == 'POST':
        file = request.files['file']
        target_language = request.form['language']
        translated_text = translate_file(file, target_language)
    return render_template('file_trans.html', translated_text=translated_text, languages=LANGUAGES)

@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    target_language = request.form['language']
    translated_text = translate_file(file, target_language)
    return jsonify({'translated_text': translated_text})

@app.route('/img_detect', methods=['GET', 'POST'])
def img_detect():
    detected_language = None
    language_name = None
    extracted_text = None
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({'error': 'No image part'}), 400
        image = request.files['image']
        if image.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        detected_language, language_name, extracted_text = detect_language_from_image(image)
    return render_template('img_detect.html', detected_language=detected_language, language_name=language_name, extracted_text=extracted_text)

@app.route('/multi', methods=['GET', 'POST'])
def multi():
    if request.method == 'POST':
        text = request.form['text']
        target_languages = request.form.getlist('languages')
        if not target_languages:
            return render_template('multi.html', error="Please select at least one language.", languages=LANGUAGES)
        translations = translate_text_multiple_languages(text, target_languages)
        return render_template('multi.html', translations=translations, original_text=text, languages=LANGUAGES)
    return render_template('multi.html', languages=LANGUAGES)

@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    if request.method == 'POST':
        input_text = request.form.get('input_text')
        target_lang = request.form.get('target_lang')
        if input_text and target_lang:
            summary = summarize_text(input_text)
            translated_summary = translate_text(summary, target_lang)
            return render_template('summ_trans.html', summary=summary, translated_summary=translated_summary, input_text=input_text, target_lang=target_lang, languages=LANGUAGES)
        else:
            return render_template('summ_trans.html', error="Please enter some text to summarize and translate.", languages=LANGUAGES)
    return render_template('summ_trans.html', languages=LANGUAGES)

if __name__ == '__main__':
    app.run(debug=True)
