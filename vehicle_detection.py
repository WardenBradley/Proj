# %%
import os
import cv2
import cv2 as cv
import numpy as np
from flask import Flask, render_template, request
import time

#%%
app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('upload.html')

ALLOWED_EXTENSIONS = ['mp4']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return "No video file found"
    video = request.files['video']
    if video.filename == "":
        return 'No video file selected'
    if video and allowed_file(video.filename):
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        video.save(video_path)
        # After saving, process the video using OpenCV
        process_video(video_path)
        return "Video processed successfully"
    return "invalid file type"

# %%
def process_video(video_path):
    min_contour_width = 40  
    min_contour_height = 40  
    offset = 10  
    line_height = 550  
    matches = []
    vehicles = 0
    
    
    



# %%
    def get_centrolid(x, y, w, h):
        x1 = int(w / 2)
        y1 = int(h / 2)
        
        cx = x + x1
        cy = y + y1
        return cx, cy

# %%
    cap = cv2.VideoCapture(video_path)

# %%
    cap.set(3, 1920)
    cap.set(4, 1080)
 
    if cap.isOpened():
        ret, frame1 = cap.read()
    else:
        ret = False
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()

# %%
    alert_displayed = False  
    start_time = None  
    text_duration = 10  
    alert_reset = False
    
    while ret:
        d = cv2.absdiff(frame1, frame2)
        grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)
        
        blur = cv2.GaussianBlur(grey, (5, 5), 0)
 
        ret, th = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(th, np.ones((3, 3)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        
        
        closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
        contours, h = cv2.findContours(
            closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for(i, c) in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(c)
            contour_valid = (w >= min_contour_width) and (
                h >= min_contour_height)
 
            if not contour_valid:
                continue
            cv2.rectangle(frame1, (x-10, y-10), (x+w+10, y+h+10), (255, 0, 0), 2)
 
            cv2.line(frame1, (0, line_height), (1900, line_height), (0, 255, 0), 2)
            centrolid = get_centrolid(x, y, w, h)
            matches.append(centrolid)
            cv2.circle(frame1, centrolid, 5, (0, 255, 0), -1)
            cx, cy = get_centrolid(x, y, w, h)
            for (x, y) in matches:
                if y < (line_height+offset) and y > (line_height-offset):
                    vehicles = vehicles +1
                    matches.remove((x, y))
 
        cv2.putText(frame1, "Total Vehicle Detected: " + str(vehicles), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1,
            (0, 170, 0), 2)

        
        if vehicles > 100 and not alert_displayed and not alert_reset:
            start_time = time.time()
            alert_displayed = True

        if alert_displayed:
            current_time = time.time()
            if current_time - start_time < text_duration:
                red = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)
                cv2.putText(frame1, "Vehicle Overload Alert!", (410, 390), cv2.FONT_HERSHEY_SIMPLEX, 2,
                        (0, 0, 255), 4)
            else:
                alert_displayed = False
                alert_reset = True
            
 
        cv2.imshow("Vehicle Detection", frame1)
        if cv2.waitKey(1) == 27:
            break
        frame1 = frame2
        ret, frame2 = cap.read()
 
    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    app.run(debug=True)