from PIL import Image
import os, fitz


# generate thumbnail for the pdf
def generate_pdf_thumbnail(pdf_path, filename, upload_folder):
    """Generate an image from the first page of a PDF using PyMuPDF."""
    # Ensure the thumbnails directory exists
    thumbnails_dir = os.path.join(upload_folder, 'thumbnails')
    os.makedirs(thumbnails_dir, exist_ok=True) 

    pdf_document = fitz.open(pdf_path)
    
    #select only the first page for the thumbnail
    first_page = pdf_document.load_page(0)
    
    zoom = 2  # Increase for higher resolution
    mat = fitz.Matrix(zoom, zoom)
    pix = first_page.get_pixmap(matrix=mat)
    
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    thumbnail_filename = filename.replace('.pdf', '.jpg')
    thumbnail_path = os.path.join(thumbnails_dir, thumbnail_filename)
    image.save(thumbnail_path, 'JPEG')
    
    return thumbnail_path