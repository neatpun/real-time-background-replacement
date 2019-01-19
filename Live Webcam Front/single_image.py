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


def segmentation(detection_graph):
    vs = cv2.imread('a.jpg')
    resize_ratio = 1.0 * 513 / max(vs.shape)
    target_size = (int(resize_ratio * vs.shape[1]), int(resize_ratio * vs.shape[0]))
    config = tf.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True
    fps = FPS2(5).start()

    background_image = cv2.imread('b.jpg')
    resized_background_image = cv2.resize(
        background_image, target_size)  # (384,513)

    print("Starting...")

    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:

            image = cv2.resize(vs, target_size)

            batch_seg_map = sess.run('SemanticPredictions:0',
                                     feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
            # visualization
            seg_map = batch_seg_map[0]
            seg_map[seg_map != 15] = 0

            bg_copy = resized_background_image.copy()
            mask = (seg_map == 15)
            bg_copy[mask] = image[mask]

            # create_colormap(seg_map).astype(np.uint8)
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

            # ir=cv2.resize(bg_copy,(960,720))
            # cv2.imshow('segmentation', bg_copy)

            fps.update()

            combo_resized=cv2.resize(bg_copy,( vs.shape[1], vs.shape[0]))

            cv2.imwrite("out.jpg", combo_resized)

    fps.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':

    graph = load_model()
    segmentation(graph)
