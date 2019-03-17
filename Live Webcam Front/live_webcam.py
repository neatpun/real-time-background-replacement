import numpy as np
import tensorflow as tf
import imutils
import os
import cv2
from stuff.helper import FPS2, WebcamVideoStream
from skimage import measure
from random import randint

img_num=0
mike_flag=True

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


def next_bg(event, x, y, flags, param):
    global mike_flag,img_num
    if event == cv2.EVENT_LBUTTONUP:
        mike_flag=not mike_flag
    elif event == cv2.EVENT_RBUTTONUP:
        img_num+=1





def segmentation(detection_graph):

    vs = WebcamVideoStream(0, 640, 480).start()

    resize_ratio = 1.0 * 513 / max(vs.real_width, vs.real_height)
    target_size = (int(resize_ratio * vs.real_width),
                   int(resize_ratio * vs.real_height))
    config = tf.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True
    fps = FPS2(5).start()

    filelist = [file for file in os.listdir(
        'backgrounds') if file.endswith('.jpg')]

    num_files=len(filelist)

    background_image = []
    resized_background_image=[]
    for x in filelist:
        background_image.append(cv2.imread(x))
        resized_background_image.append(cv2.resize(
            background_image[-1], target_size))
        

    # fff = 0

    # background_image = cv2.imread('b.jpg')
    # resized_background_image = cv2.resize(
    #     background_image, target_size)  # (384,513)

    # background_image2 = cv2.imread('b2.jpg')
    # resized_background_image2 = cv2.resize(
    #     background_image2, target_size)  # (384,513)

    # background_image3 = cv2.imread('b3.jpg')
    # resized_background_image3 = cv2.resize(
    #     background_image3, target_size)  # (384,513)

    mike_background_image = cv2.imread('mike.png')
    mike_background_image = cv2.resize(mike_background_image, (int(
        resize_ratio * vs.real_width/3), int(resize_ratio * vs.real_height*3/4)))  # (384,513)

    # Uncomment to save output
    # out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc(
    # 'M', 'J', 'P', 'G'), 1, (vs.real_height, vs.real_width))#CHANGE

    print("Starting...")

    cv2.namedWindow('segmentation',16)# 16 means WINDOW_GUI_NORMAL, to disable right click context menu

    cv2.setMouseCallback('segmentation', next_bg)

    global img_num,mike_flag
    img_num=0
    mike_flag=False



    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            while vs.isActive():
                image = cv2.resize(vs.read(), target_size)
                batch_seg_map = sess.run('SemanticPredictions:0',
                                         feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
                # visualization
                seg_map = batch_seg_map[0]
                seg_map[seg_map != 15] = 0

                bg_copy=resized_background_image[img_num%num_files].copy()

                # if fff == 0:
                #     bg_copy = resized_background_image.copy()
                # elif fff == 1:
                #     bg_copy = resized_background_image2.copy()
                # elif fff == 2:
                #     bg_copy = resized_background_image3.copy()

                mask = (seg_map == 15)
                bg_copy[mask] = image[mask]

                # create_colormap(seg_map).astype(np.uint8)
                seg_image = np.stack(
                    (seg_map, seg_map, seg_map), axis=-1).astype(np.uint8)
                gray = cv2.cvtColor(seg_image, cv2.COLOR_BGR2GRAY)

                thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)[1]
                _, cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                   cv2.CHAIN_APPROX_SIMPLE)

                try:
                    cv2.drawContours(
                        bg_copy, cnts, -1, (randint(0, 255), randint(0, 255), randint(0, 255)), 2)
                except:
                    pass

                if mike_flag:
                    x_offset = 150
                    y_offset = 95
                    bg_copy[y_offset:y_offset+mike_background_image.shape[0], x_offset:x_offset+mike_background_image.shape[1]
                            ][mike_background_image != 0] = mike_background_image[mike_background_image != 0]

                ir = cv2.resize(bg_copy, (vs.real_width, vs.real_height))
                cv2.imshow('segmentation', ir)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                elif cv2.waitKey(1) & 0xFF == ord('a'):
                    fff = 0
                elif cv2.waitKey(1) & 0xFF == ord('b'):
                    fff = 1
                elif cv2.waitKey(1) & 0xFF == ord('c'):
                    fff = 2
                fps.update()

                # out.write(ir)
    fps.stop()
    vs.stop()
    # out.release()

    cv2.destroyAllWindows()


if __name__ == '__main__':

    graph = load_model()
    segmentation(graph)
