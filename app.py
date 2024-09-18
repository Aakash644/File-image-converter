from flask import Flask, render_template, request, send_file,url_for,redirect
import os
import PyPDF2
import tinify
from PIL import Image
from docx2pdf import convert
import pdfkit
import pandas as pd
from docx import Document
from pdf2docx import Converter


tinify.key = "api_key"

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

# Set upload and download folder paths
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def get_image_size(image_path):
    try:
        # Get the size of the image file in bytes
        size = os.path.getsize(image_path)
        return size
    except Exception as e:
        print(f"Error getting image size: {e}")


def resize_image(input_path, output_path, width, height):
    try:
        img = Image.open(input_path)
        resized_img = img.resize((width, height))
        resized_img.save(output_path)
        print(f"Image resized successfully to {width}x{height} pixels.")
    except Exception as e:
        print(f"Error resizing image: {e}")


def compress_image(input_path, output_path):
    try:
        # Compress the image using TinyPNG API
        source = tinify.from_file(input_path)
        source.to_file(output_path)

        print("Image compressed successfully.")
    except Exception as e:
        print(f"Error compressing image: {e}")


def convert_image(input_path, output_path, output_format):
    """
    Convert an image from one format to another using PIL.

    Args:
    - input_path (str): Path to the input image file.
    - output_path (str): Path to save the converted image file.
    - output_format (str): Desired output format (e.g., 'JPEG', 'PNG', 'GIF', etc.).
    """
    try:
        # Open the input image
        img = Image.open(input_path)

        # Save the image in the specified format
        img.save(output_path, format=output_format)

        print(f"Image converted successfully to {output_format} format.")
    except Exception as e:
        print(f"Error converting image: {e}")


def convert_to_pdf(docx_file_path, pdf_file_path):
    # Convert DOCX to PDF
    convert(docx_file_path, pdf_file_path)


def pdf_to_docx(pdf_path, docx_path):
   cv = Converter(pdf_path)
   cv.convert(docx_path)
   cv.close()

def convert_to_csv(excel_file_path, csv_file_path):
    # Read Excel file into DataFrame
    df = pd.read_excel(excel_file_path)

    # Write DataFrame to CSV file
    df.to_csv(csv_file_path, index=False)

def convert_to_excel(csv_file_path, excel_file_path):
    # Read CSV file into DataFrame
    df = pd.read_csv(csv_file_path)

   # Write DataFrame to Excel file
    df.to_excel(excel_file_path, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fileconverter', methods=['GET', 'POST'])
def fileconverter():
    return render_template("fileconverter.html")

@app.route('/uploadfiles', methods=['GET', 'POST'])
def uploadfiles():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file:
        # Save uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file_format=file.filename.split(".")[1]
        file.save(file_path)

        # Determine file type and convert accordingly
        conversion_from = file_format
        conversion_to = request.form['conversionTo']

        if conversion_from == 'docx' and conversion_to == 'pdf':
            pdf_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file.filename.replace('.docx', '.pdf'))
            pythoncom.CoInitialize()
            convert_to_pdf(file_path, pdf_file_path)
            return render_template('fileconverter.html', download_link=f'/download/{os.path.basename(pdf_file_path)}')

        elif conversion_from == 'pdf' and conversion_to == 'docx':
            docx_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file.filename.replace('.pdf', '.docx'))
            pdf_to_docx(file_path, docx_file_path)
            return render_template('fileconverter.html', download_link=f'/download/{os.path.basename(docx_file_path)}')

        elif conversion_from == 'txt' and conversion_to == 'pdf':
            pdf_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file.filename.replace('.txt', '.pdf'))
            # Convert text to PDF
            # Your code for converting text to PDF goes here
            return render_template('fileconverter.html', download_link=f'/download/{os.path.basename(pdf_file_path)}')

        elif conversion_from == 'csv' and conversion_to == 'xlsx':
            excel_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file.filename.replace('.csv', '.xlsx'))
            convert_to_excel(file_path, excel_file_path)
            return render_template('fileconverter.html', download_link=f'/download/{os.path.basename(excel_file_path)}')

        elif conversion_from == 'xlsx' and conversion_to == 'csv':
            csv_file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file.filename.replace('.xlsx', '.csv'))
            convert_to_csv(file_path, csv_file_path)
            return render_template('fileconverter.html', download_link=f'/download/{os.path.basename(csv_file_path)}')

        else:
            return 'Unsupported conversion'
  


@app.route('/imageconverter', methods=['GET', 'POST'])
def imageconverter():
    return render_template('imageconverter.html')

@app.route('/uploadimages', methods=['GET', 'POST'])
def uploadimages():
    if request.method == "POST":
        file = request.files["image"]
        format = request.form.get("conversionTo")
        outputimage, x = file.filename.split('.')
        format = format.lower()
        outputimage = outputimage + "." + format
        with Image.open(file) as image:
            image.convert('RGB').save( outputimage)
            path = 'static/images/' + outputimage 
            os.rename(outputimage, path )
            filepath = 'images/' + outputimage
            image_url = url_for('static', filename=filepath)
        return render_template("imageconverter.html", download_link=image_url,image_name=file.filename)
    return redirect("/imageconverter")

@app.route('/imageresizer',methods=['GET','POST'])
def imageresizer():
    return render_template('imageresizer.html')

@app.route('/uploadimageresizer', methods=['POST'])
def uploadimageresizer():
    if request.method == "POST":
        file = request.files["image"]
        width = int(request.form.get("width"))
        height = int(request.form.get("height"))
        
        if file and width and height:
            filename, ext = os.path.splitext(file.filename)
            output_filename = f"{filename}_resized{ext}"
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], output_filename)
            filepath = 'images/' + output_path
            
            file.save(input_path)
            resize_image(input_path, output_path, width, height)
            
            return render_template("imageresizer.html",download_link=f'/download/{os.path.basename(output_path)}')

    
    return redirect("/imageresizer")

@app.route('/imagecompressor',methods=['GET','POST'])
def imagecompressor():
    return render_template("imagecompressor.html")

@app.route('/uploadimagecompressor',methods=['GET','POST'])
def uploadimagecompressor():
    if request.method == "POST":
        file = request.files["image"]
        

        if file:
            filename = file.filename
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)

            # Save uploaded image
            file.save(input_path)

            #  compress image
            compress_image(input_path, output_path)

            # Provide download link to the resized and compressed image
            return render_template('imagecompressor.html',download_link=f'/downloads/{os.path.basename(output_path)}')

    return redirect("/imagecompressor")

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
