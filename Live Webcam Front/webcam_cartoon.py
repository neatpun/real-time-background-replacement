


import numpy as np
import tensorflow as tf
import imutils
import os
import cv2
from stuff.helper import FPS2, WebcamVideoStream
from skimage import measure
from random import randint


def render( img_rgb):
    numDownSamples = 2       # number of downscaling steps
    numBilateralFilters = 7  # number of bilateral filtering steps

    # -- STEP 1 --
    # downsample image using Gaussian pyramid
    img_color = img_rgb
    for _ in range(numDownSamples):
        img_color = cv2.pyrDown(img_color)

    # repeatedly apply small bilateral filter instead of applying
    # one large filter
    for _ in range(numBilateralFilters):
        img_color = cv2.bilateralFilter(img_color, 9, 9, 7)

    # upsample image to original size
    for _ in range(numDownSamples):
        img_color = cv2.pyrUp(img_color)

    # make sure resulting image has the same dims as original
    img_color = cv2.resize(img_color, img_rgb.shape[:2])

    # -- STEPS 2 and 3 --
    # convert to grayscale and apply median blur
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)

    # -- STEP 4 --
    # detect and enhance edges
    img_edge = cv2.adaptiveThreshold(img_blur, 255,
                                     cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY, 9, 2)

    # -- STEP 5 --
    # convert back to color so that it can be bit-ANDed with color image
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)


    return cv2.bitwise_and(img_color, img_edge)


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
    vs = WebcamVideoStream(0, 1280, 720).start()
    resize_ratio = 1.0 * 513 / max(vs.real_width, vs.real_height)
    target_size = (int(resize_ratio * vs.real_width),
                   int(resize_ratio * vs.real_height))
    config = tf.ConfigProto(allow_soft_placement=True)
    config.gpu_options.allow_growth = True
    fps = FPS2(5).start()

    # background_image = cv2.imread('b.jpg')
    # resized_background_image = cv2.resize(background_image, target_size)  # (384,513)

    print("Starting...")
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            while vs.isActive():
                image = cv2.resize(vs.read(), target_size)
                batch_seg_map = sess.run('SemanticPredictions:0',
                                         feed_dict={'ImageTensor:0': [cv2.cvtColor(image, cv2.COLOR_BGR2RGB)]})
                # visualization
                seg_map = batch_seg_map[0]
                seg_map[seg_map != 15] = 0

                # bg_copy = resized_background_image.copy()
                mask = (seg_map == 15)
                # car=render(image)
                # car = cv2.stylization(image, sigma_s=60, sigma_r=0.07)

                gray0 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray0 = cv2.medianBlur(gray0, 5)
                edges = cv2.adaptiveThreshold(gray0, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
                
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

                # ir=cv2.resize(car,(vs.real_width,vs.real_height))
                ir = cartoon
                cv2.imshow('segmentation', ir)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                fps.update()
    fps.stop()
    vs.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':

    graph = load_model()
    segmentation(graph)
