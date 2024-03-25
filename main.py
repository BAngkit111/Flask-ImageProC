from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import cv2
import os

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'webp', 'jpg', 'jpeg', 'gif','ccrop','blur'}

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processImage(filename, operation):
    print(f"the operation is {operation} and filename is {filename}")
    img = cv2.imread(f"uploads/{filename}")
    newFilename = f"static/{filename}"

    if operation == "cgray":
        imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(newFilename, imgProcessed)
    elif operation == "cwebp":
        newFilename = f"static/{filename.split('.')[0]}.webp"
        cv2.imwrite(newFilename, img)
    elif operation == "cjpg":
        newFilename = f"static/{filename.split('.')[0]}.jpg"
        cv2.imwrite(newFilename, img)
    elif operation == "cpng":
        newFilename = f"static/{filename.split('.')[0]}.png"
        cv2.imwrite(newFilename, img)
    elif operation == "cblur":
        imgProcessed = cv2.GaussianBlur(img, (55, 55), 0)
        cv2.imwrite(newFilename, imgProcessed)
    elif operation == "ccrop":
        img_height, img_width = img.shape[:2]
        crop_width, crop_height = 2000, 3000
        x = (img_width - crop_width) // 2
        y = (img_height - crop_height) // 6
        imgProcessed = img[y:y+crop_height, x:x+crop_width]
        cv2.imwrite(newFilename, imgProcessed)
    else:
        flash("Invalid operation")
        return None

    return newFilename

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST": 
        operation = request.form.get("operation")
        
        if 'file' not in request.files:
            flash('No file part')
            return "error"
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return "error no selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new = processImage(filename, operation)
            if new:
                flash(f"Your image has been processed and is available <a href='/{new}' target='_blank'>here</a>")
            return render_template("index.html")

    return render_template("index.html")

app.run(debug=True, port=5001)
