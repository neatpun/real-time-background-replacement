
# FLASK_APP=index.py flask run
# then open localhost:5000


from scipy.interpolate import interp1d
from scipy import interpolate
import base64
import io
import matplotlib.pyplot as plt
from flask import render_template
from flask import send_from_directory
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, send_file
import numpy as np
import tensorflow as tf
import imutils
import os
import cv2
from stuff.helper import FPS2, WebcamVideoStream
from skimage import measure
from random import randint


def load_model():
    print('Loading model...')
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        seg_graph_def = tf.GraphDef()
        with tf.gfile.GFile('models/deeplabv3_mnv2_pascal_train_aug/frozen_inference_graph.pb', 'rb') as fid:
            serialized_graph = fid.read()
            seg_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(seg_graph_def, name='')
    return detection_graph


graph = load_model()


def segmentation(filename_fg, cv_type, filename_bg=None):
    detection_graph = graph
    print(filename_fg)
    print(cv_type)
    print(filename_bg)

    if cv_type == "fg_video":
        vs = cv2.VideoCapture('uploads/' + filename_fg)
        width = int(vs.get(3))
        height = int(vs.get(4))
        fps_v = int(vs.get(5))

        resize_ratio = 1.0 * 513 / max(width, height)
        target_size = (int(resize_ratio * height),
                       int(resize_ratio * width))  # reversed

        background_image = cv2.imread('uploads/' + filename_bg)
        resized_background_image = cv2.resize(
            background_image, target_size)  # (384,513)

    elif cv_type == "fg_image":
        vs = cv2.imread('uploads/'+filename_fg)
        width = vs.shape[0]
        height = vs.shape[1]

        resize_ratio = 1.0 * 513 / max(width, height)
        target_size = (int(resize_ratio * height),
                       int(resize_ratio * width))  # reversed

        background_image = cv2.imread('uploads/' + filename_bg)
        resized_background_image = cv2.resize(
            background_image, target_size)  # (384,513)

    elif cv_type == "bg_video":
        vs = cv2.VideoCapture('uploads/' + filename_fg)
        width = int(vs.get(3))
        height = int(vs.get(4))
        fps_v = int(vs.get(5))

        bgv = cv2.VideoCapture('uploads/' + filename_bg)
        print("in")

        resize_ratio = 1.0 * 513 / max(width, height)
        target_size = (int(resize_ratio * height),
                       int(resize_ratio * width))  # reversed

    elif cv_type == "bw" or cv_type == "crayon" or cv_type == "cartoon":
        vs = cv2.VideoCapture('uploads/' + filename_fg)
        width = int(vs.get(3))
        height = int(vs.get(4))
        fps_v = int(vs.get(5))

        resize_ratio = 1.0 * 513 / max(width, height)
        target_size = (int(resize_ratio * height),
                       int(resize_ratio * width))  # reversed

    config = tf.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True
    fps = FPS2(5).start()

    if cv_type != "fg_image":
        out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc(
            'M', 'J', 'P', 'G'), fps_v, (height, width))

    print("Starting...")

    ret = True
    counting = 0
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:

            if cv_type == "fg_image":
                image = cv2.resize(vs, target_size)

                batch_seg_map = sess.run('SemanticPredictions:0',
                                         feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
                seg_map = batch_seg_map[0]
                seg_map[seg_map != 15] = 0

                bg_copy = resized_background_image.copy()
                mask = (seg_map == 15)
                bg_copy[mask] = image[mask]

                seg_image = np.stack((seg_map, seg_map, seg_map),
                                     axis=-1).astype(np.uint8)
                gray = cv2.cvtColor(seg_image, cv2.COLOR_BGR2GRAY)

                thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]
                cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)

                try:

                    cv2.drawContours(
                        bg_copy, cnts, -1, (randint(0, 255), randint(0, 255), randint(0, 255)), 2)
                except:
                    pass

                fps.update()

                combo_resized = cv2.resize(bg_copy, (vs.shape[1], vs.shape[0]))

                cv2.imwrite("out.jpg", combo_resized)

                fps.stop()
                cv2.destroyAllWindows()

                return

            elif cv_type == "fg_video":

                while (True):

                    counting += 1

                    ret, frame = vs.read()
                    if(not ret):
                        break

                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    image = cv2.resize(frame, target_size)

                    bg_copy = resized_background_image.copy()

                    batch_seg_map = sess.run('SemanticPredictions:0',
                                             feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
                    seg_map = batch_seg_map[0]
                    seg_map[seg_map != 15] = 0

                    mask = (seg_map == 15)
                    bg_copy[mask] = image[mask]

                    seg_image = np.stack(
                        (seg_map, seg_map, seg_map), axis=-1).astype(np.uint8)
                    gray = cv2.cvtColor(seg_image, cv2.COLOR_BGR2GRAY)

                    thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]
                    cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                       cv2.CHAIN_APPROX_SIMPLE)

                    try:

                        cv2.drawContours(
                            bg_copy, cnts, -1, (randint(0, 255), randint(0, 255), randint(0, 255)), 2)
                    except:
                        pass

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    fps.update()

                    combo_resized = cv2.resize(bg_copy, (height, width))

                    out.write(combo_resized)

                fps.stop()
                out.release()
                vs.release()
                cv2.destroyAllWindows()
                return

            elif cv_type == "bg_video":

                while (True):
                    ret, frame = vs.read()

                    if(not ret):
                        break

                    ret, bg_frame = bgv.read()
                    if(not ret):
                        break

                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    image = cv2.resize(frame, target_size)

                    bg_copy = cv2.resize(bg_frame, target_size)

                    batch_seg_map = sess.run('SemanticPredictions:0',
                                             feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
                    seg_map = batch_seg_map[0]
                    seg_map[seg_map != 15] = 0

                    mask = (seg_map == 15)
                    bg_copy[mask] = image[mask]

                    seg_image = np.stack(
                        (seg_map, seg_map, seg_map), axis=-1).astype(np.uint8)
                    gray = cv2.cvtColor(seg_image, cv2.COLOR_BGR2GRAY)

                    thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]
                    cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                       cv2.CHAIN_APPROX_SIMPLE)

                    try:

                        cv2.drawContours(
                            bg_copy, cnts, -1, (randint(0, 255), randint(0, 255), randint(0, 255)), 2)
                    except:
                        pass

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    fps.update()

                    combo_resized = cv2.resize(bg_copy, (height, width))

                    out.write(combo_resized)
                    counting += 1

                fps.stop()
                out.release()
                vs.release()
                bgv.release()
                cv2.destroyAllWindows()

                return

            elif cv_type == "bw":

                while (True):

                    counting += 1

                    ret, frame = vs.read()
                    if(not ret):
                        break

                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    image = cv2.resize(frame, target_size)

                    batch_seg_map = sess.run('SemanticPredictions:0',
                                             feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
                    seg_map = batch_seg_map[0]
                    seg_map[seg_map != 15] = 0

                    mask = (seg_map == 15)
                    gray0 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    gray0 = cv2.cvtColor(gray0, cv2.COLOR_GRAY2BGR)

                    print(gray0.shape)
                    gray0[mask] = image[mask]

                    seg_image = np.stack(
                        (seg_map, seg_map, seg_map), axis=-1).astype(np.uint8)
                    gray = cv2.cvtColor(seg_image, cv2.COLOR_BGR2GRAY)

                    thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]
                    cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                       cv2.CHAIN_APPROX_SIMPLE)

                    try:

                        cv2.drawContours(
                            gray0, cnts, -1, (randint(0, 255), randint(0, 255), randint(0, 255)), 2)
                    except:
                        pass

                    ir = gray0
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    fps.update()

                    ir = cv2.resize(ir, (height, width))

                    out.write(ir)

                fps.stop()
                out.release()
                vs.release()
                cv2.destroyAllWindows()
                return

            elif cv_type == "crayon":

                while (True):

                    counting += 1

                    ret, frame = vs.read()
                    if(not ret):
                        break

                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    image = cv2.resize(frame, target_size)

                    batch_seg_map = sess.run('SemanticPredictions:0',
                                             feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
                    seg_map = batch_seg_map[0]
                    seg_map[seg_map != 15] = 0

                    mask = (seg_map == 15)

                    car = cv2.stylization(image, sigma_s=60, sigma_r=0.07)

                    car[mask] = image[mask]

                    seg_image = np.stack(
                        (seg_map, seg_map, seg_map), axis=-1).astype(np.uint8)
                    gray = cv2.cvtColor(seg_image, cv2.COLOR_BGR2GRAY)

                    thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]
                    cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                       cv2.CHAIN_APPROX_SIMPLE)

                    try:

                        cv2.drawContours(
                            car, cnts, -1, (randint(0, 255), randint(0, 255), randint(0, 255)), 2)
                    except:
                        pass

                    ir = car
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    fps.update()

                    ir = cv2.resize(ir, (height, width))

                    out.write(ir)

                fps.stop()
                out.release()
                vs.release()
                cv2.destroyAllWindows()
                return

            elif cv_type == "cartoon":

                while (True):

                    counting += 1

                    ret, frame = vs.read()
                    if(not ret):
                        break

                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    image = cv2.resize(frame, target_size)

                    batch_seg_map = sess.run('SemanticPredictions:0',
                                             feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
                    seg_map = batch_seg_map[0]
                    seg_map[seg_map != 15] = 0

                    mask = (seg_map == 15)

                    gray0 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    gray0 = cv2.medianBlur(gray0, 5)
                    edges = cv2.adaptiveThreshold(
                        gray0, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

                    # 2) Color
                    color = cv2.bilateralFilter(image, 9, 300, 300)

                    # 3) Cartoon
                    cartoon = cv2.bitwise_and(color, color, mask=edges)

                    # gray0 = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                    # gray0 = cv2.cvtColor(gray0, cv2.COLOR_GRAY2RGB)

                    print(cartoon.shape)
                    cartoon[mask] = image[mask]

                    # create_colormap(seg_map).astype(np.uint8)
                    seg_image = np.stack(
                        (seg_map, seg_map, seg_map), axis=-1).astype(np.uint8)
                    gray = cv2.cvtColor(seg_image, cv2.COLOR_BGR2GRAY)

                    thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]
                    cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                       cv2.CHAIN_APPROX_SIMPLE)

                    try:

                        cv2.drawContours(
                            cartoon, cnts, -1, (randint(0, 255), randint(0, 255), randint(0, 255)), 2)
                    except:
                        pass

                    ir = cartoon
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    fps.update()

                    ir = cv2.resize(ir, (height, width))

                    out.write(ir)

                fps.stop()
                out.release()
                vs.release()
                cv2.destroyAllWindows()
                return


UPLOAD_FOLDER = './uploads'
# ALLOWED_EXTENSIONS = set(['mp4','jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024
app.secret_key = "super secret key"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])  # methods=['GET', 'POST'])
def hi():

    return """<html>
  <body>
    <form action="/segment" method="POST" enctype="multipart/form-data">
      <label for="file_fg">Choose foreground video/image to upload</label>
      <input type="file" name="file_fg"/><br/>
      <label for="file_bg">Choose background video/image to upload ( for first 3 types)</label>

      <input type="file" name="file_bg"/><br/>

      <label for="cv_type">What would you like to see?</label>

      
      <select name="cv_type">
        <option value="fg_video" selected="selected">fg-video and bg-image</option>
        <option value="fg_image">fg-image and bg-image</option>
        <option value="bg_video">fg-video and bg-video</option>
        <option value="bw">bw</option>
        <option value="cartoon">cartoon</option>
        <option value="crayon">crayon</option>
      </select> <br/>
      <input type="submit"/>
    
    </form>
  </body>
</html>"""


@app.route('/segment', methods=['POST'])
def plot():
    print(1)
    if 'file_fg' not in request.files:
        flash('No file part')
        return redirect(request.url)
    print(1.5)

    file_fg = request.files['file_fg']

    try:
        cv_type = request.form.get('cv_type')
    except:
        cv_type='fg_video'
    
    if cv_type is None:
        cv_type='fg_video'
    

    print(cv_type)



    print(2)

    if file_fg.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file_fg:
        filename_fg = secure_filename(file_fg.filename)
        file_fg.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_fg))
        print(filename_fg)

    print(3)

    try:
        file_bg = request.files['file_bg']

        if file_bg.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file_bg:
            filename_bg = secure_filename(file_bg.filename)
            file_bg.save(os.path.join(
                app.config['UPLOAD_FOLDER'], filename_bg))
            print(filename_bg)

        print("about to...")

        segmentation(filename_fg, cv_type, filename_bg)

        if cv_type == "fg_image":
            return send_file('out.jpg')

        return send_file('outpy.avi')

    except:
        print("about to...")
        filename_bg='assets/background.jpg'

        segmentation(filename_fg, cv_type,filename_bg)

        return send_file('outpy.avi')
