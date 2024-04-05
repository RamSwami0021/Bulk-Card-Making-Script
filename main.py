import pandas as pd
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import portrait
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import tempfile

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Register Garamond font
pdfmetrics.registerFont(TTFont('Garamond', 'EB_Garamond/font.ttf'))
pdfmetrics.registerFont(TTFont('Garamond-Bold', 'EB_Garamond/font1.ttf'))
pdfmetrics.registerFont(TTFont('Codecpro', 'EB_Garamond/codec-pro.regular.ttf'))


def create_card(c, data, card_width, card_height, is_front):
    c.setFont("Garamond", 7)  # Use Garamond font
    padding = 10
    border_radius = 20

    if is_front:
        c.setFillColorRGB(1, 1, 1)  # Background color (white)
        c.roundRect(padding, padding, card_width - 2 * padding, card_height - 2 * padding, border_radius, stroke=0, fill=1)  # Removed stroke

        image_path = "ca.png"
        logo_width, logo_height = 180, 90  # Increased logo size
        x_image = (card_width - logo_width) / 2
        y_image = (card_height - logo_height) / 1.2  # Center vertically

        c.drawImage(image_path, x_image, y_image, width=logo_width, height=logo_height)

        name = data["Name"]  # Assuming "CompanyName" contains the company name
        c.setFillColorRGB(0, 0, 0)  # Text color (black)
        c.setFont("Garamond-Bold", 24)  # Set font size for company name and use bold font
        text_width = c.stringWidth(name, "Garamond-Bold", 24)  # Get width of the text
        c.drawCentredString(card_width / 2, y_image - 15, name)  # Position below the logo


    else:
        c.setFillColorRGB(1, 1, 1)  # Background color (white)
        c.roundRect(padding, padding, card_width - 2 * padding, card_height - 2 * padding, border_radius, stroke=0, fill=1)  # Removed stroke

        c.setFillColorRGB(0, 0, 0)  # Text color (black)
        c.setFont("Garamond", 15)  # Set font size for other texts

        # Displaying name, phone, and email on the back side
        name = data["Name"]
        phone = str(data["Phone"])
        email = str(data["Email"])

        # Setting font sizes for different text types
        c.setFont("Garamond-Bold", 15)  # Larger font for name
        c.drawString(padding * 2, card_height - padding * 2 - 10, name)

 # Add icon and space before phone number and email
        image_path_before_contact = "1.png"  # Path to the image file
        image_width, image_height = 10, 10  # Adjust size as needed
        x_image_before_contact = padding * 2  # Adjust x position as needed
        y_image_before_contact = card_height - padding * 4 - 10  # Adjust y position as needed

        # Draw phone icon
        c.drawImage(image_path_before_contact, x_image_before_contact, y_image_before_contact - 2, width=image_width, height=image_height)

        # Add padding between icon and text
        x_text_phone = x_image_before_contact + image_width + 2  # Adjust x position for phone number
        y_text_contact = card_height - padding * 4 - 10  # Common y position for phone and email

        # Draw phone number
        c.setFont("Codecpro", 8)  # Set font size for phone
        c.drawString(x_text_phone, y_text_contact, phone)
        
        # Add icon and space before email
        image_path_before_email = "2.png"  # Path to the image file
        x_image_before_email = x_text_phone  # Same x position as phone icon
        y_image_before_email = y_text_contact - 15  # Adjust y position for email

        # Draw email icon
        c.drawImage(image_path_before_email, x_image_before_email - 12, y_image_before_email - 2, width=image_width, height=image_height)

        # Draw email
                # Draw email
        email_lines = [email[i:i+25] for i in range(0, len(email), 25)]  # Split email into lines of 15 characters
        for i, line in enumerate(email_lines):
            c.drawString(x_text_phone, y_image_before_email - i * 10, line)


        # Generate and add QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data["Link"])  # Assuming "Link" contains the URL
        qr.make(fit=True)

        # Double the size of the QR code
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((120, 120))

        x_qr = card_width - padding * 2 - 80  # Position QR code to the right side with padding
        y_qr = card_height - padding * 2 - 80  # Position QR code to the top with padding
        
        # Save QR code image to a temporary file
        temp_file_qr = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        temp_file_path_qr = temp_file_qr.name
        qr_img.save(temp_file_path_qr)

        c.drawImage(temp_file_path_qr, x_qr, y_qr, width=100, height=100)

        # Close the temporary file
        temp_file_qr.close()

        # Add an image at the bottom right corner
        image_path_bottom_right = "logo.jpg"  # Path to the image file
        x_image_bottom_right = card_width - 2 * padding - 67  # Adjust x position as needed
        y_image_bottom_right = padding + 5  # Adjust y position as needed
        c.drawImage(image_path_bottom_right, x_image_bottom_right, y_image_bottom_right, width=75, height=25)


def generate_cards(csv_file):
    df = pd.read_csv(csv_file)
    card_width, card_height = 85.6 * mm, 53.98 * mm
    page_width, page_height = card_width, card_height  # Each card occupies a single page

    for index, row in df.iterrows():
        output_file = f"card_{index + 1}.pdf"
        c = canvas.Canvas(output_file, pagesize=(page_width, page_height))
        create_card(c, row, card_width, card_height, is_front=True)
        c.showPage()
        create_card(c, row, card_width, card_height, is_front=False)
        c.save()

if __name__ == "__main__":
    csv_file_path = "useList.csv"
    generate_cards(csv_file_path)
