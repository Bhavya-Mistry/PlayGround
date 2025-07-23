from PIL import Image
import pytesseract

# Uncomment this line if you have a custom installation path
# pytesseract.pytesseract.tesseract_cmd = r'C:\path\to\tesseract.exe'

# Open an image file
image = Image.open(r'E:\PlayGround\test-projects\img1.jpg')  # Make sure the image is in the same directory or provide full path

# Extract text from the image
text = pytesseract.image_to_string(image)

# Print the extracted text
print(text)
