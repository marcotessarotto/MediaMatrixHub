from pdf2image import convert_from_path
import os


def generate_pdf_preview(pdf_path, output_folder, preview_name="preview.jpg", dpi=200):
    """
    Generate a preview image for the first page of a PDF.

    Args:
    - pdf_path: Path to the PDF file.
    - output_folder: Directory to save the preview image.
    - preview_name: Name of the output preview image file.
    - dpi: Dots per inch for the output image quality.
    """

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Convert the first page of the PDF to an image
    images = convert_from_path(pdf_path, dpi=dpi, first_page=1, last_page=1)

    # Save the image
    for image in images:
        image_path = os.path.join(output_folder, preview_name)
        image.save(image_path, 'JPEG')
        print(f"Preview image saved at {image_path}")
        break  # Since we only want the first page


# Example usage
# pdf_path = '/path/to/your/document.pdf'
# output_folder = '/path/to/output/folder/'
# generate_pdf_preview(pdf_path, output_folder)
