import os
import csv
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
import qrcode
import PyPDF2

def generate_pdf(data_csv, front_template, back_template, output_path):
    # Read data from CSV file
    with open(data_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Load Jinja2 environment
            env = Environment(loader=FileSystemLoader('templates'))  # Adjust the path to your templates directory
            
            # Load front and back page templates
            front_page_template = env.get_template(front_template)
            back_page_template = env.get_template(back_template)

            # Render back page with data
            rendered_back_page = back_page_template.render(row)

            # Generate QR code
            qr_code = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L)
            qr_code.add_data(row['link'])
            qr_code.make(fit=True)
            qr_img = qr_code.make_image(fill_color="black", back_color="white")

            # Convert QR code image to base64 encoded string
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_base64 = qr_buffer.getvalue().encode('base64').decode()

            # Embed QR code image in front page HTML (replace with your placeholder in HTML)
            with open(front_template, 'r') as f:
                front_page_html = f.read()
            front_page_html = front_page_html.replace('{{ qr_code }}', f'<img src="data:image/png;base64,{qr_base64}">')

            # Convert HTML to PDF pages
            pdf_data = pisa.CreatePDF(rendered_back_page, path=f"{output_path}/{row['name']}-back.pdf")
            pdf_data = pisa.CreatePDF(front_page_html, path=f"{output_path}/{row['name']}-front.pdf")

            # Merge front and back pages
            pdf_merger = PyPDF2.PdfMerger()
            pdf_merger.append(f"{output_path}/{row['name']}-front.pdf")
            pdf_merger.append(f"{output_path}/{row['name']}-back.pdf")
            with open(f"{output_path}/{row['name']}.pdf", 'wb') as output_file:
                pdf_merger.write(output_file)

            # Clean up temporary PDF files
            os.remove(f"{output_path}/{row['name']}-front.pdf")
            os.remove(f"{output_path}/{row['name']}-back.pdf")

# Replace with your CSV file path containing name, email, phone, and link
data_csv = "useList.csv"

# Replace with your front and back page HTML template file paths
front_template = "card.html"
back_template = "back_page.html"

# Replace with your desired output folder path
output_path = "/"

generate_pdf(data_csv, front_template, back_template, output_path)
