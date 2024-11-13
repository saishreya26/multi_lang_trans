from googletrans import Translator, LANGUAGES
from PyPDF2 import PdfReader
import pdfplumber
from docx import Document
import pytesseract
from PIL import Image
import os
import io
from transformers import pipeline

translator = Translator()
summarizer = pipeline("summarization")

def translate_text(text, target_language):
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        return None

def translate_file(file, target_language):
    file_extension = os.path.splitext(file.filename)[1].lower()
    try:
        if file_extension == '.txt':
            text = file.read().decode('utf-8')
        elif file_extension == '.pdf':
            text = extract_text_from_pdf(file)
        elif file_extension in ['.doc', '.docx']:
            text = extract_text_from_doc(file)
        else:
            return "Unsupported file format. Please upload a TXT, PDF, DOC, or DOCX file."
        return translate_text(text, target_language)
    except Exception as e:
        return f"Error in file translation: {e}"

def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_doc(file):
    text = ""
    try:
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text
        return text
    except Exception as e:
        return f"Error reading DOC file: {e}"

def translate_text_multiple_languages(text, target_languages):
    translations = {}
    try:
        for lang in target_languages:
            translated = translator.translate(text, src='auto', dest=lang)
            translations[LANGUAGES.get(lang, lang)] = translated.text
        return translations
    except Exception as e:
        return {"error": str(e)}

def detect_language_from_image(image):
    try:
        pil_image = Image.open(io.BytesIO(image.read()))
        extracted_text = pytesseract.image_to_string(pil_image)
        if not extracted_text.strip():
            return "N/A", "No text detected in the image", ""
        detection = translator.detect(extracted_text)
        detected_language = detection.lang
        language_name = LANGUAGES.get(detected_language, "Unknown Language")
        return detected_language, language_name, extracted_text
    except Exception as e:
        return "N/A", f"Error in language detection: {e}", ""

def summarize_text(text):
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['summary_text']
