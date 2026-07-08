from PIL import Image, ImageEnhance
import pytesseract  # <-- así se escribe
import os

def preprocess(path):
    img = Image.open(path).convert('L')
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(2.0)

def extract_text(path):
    processed_img = preprocess(path)
    text = pytesseract.image_to_string(processed_img, lang='spa')
    return text.strip()

if __name__ == "__main__":
    # Cambia a una de tus imágenes reales
    test_image = "data/imagenes_prueba/farmacia_1.jpg"
    if os.path.exists(test_image):
        resultado = extract_text(test_image)
        print("=== TEXTO EXTRAÍDO POR TESSERACT ===\n")
        print(resultado)
    else:
        print(f"No se encontró la imagen: {test_image}")