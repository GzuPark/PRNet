import cv2
import numpy as np
import os
from skimage.transform import rescale, resize
import argparse
import ast
from time import time

from api import PRN

from utils.cv_plot import plot_kpt, plot_vertices, plot_pose_box
from utils.estimate_pose import estimate_pose


def main(args):
    # ---- init PRN
    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu # GPU number, -1 for CPU
    prn = PRN(is_dlib = args.isDlib)

    # read image
    cap = cv2.VideoCapture(0)

    if (cap.isOpened() == False):
        print "Error opening video stream or file"
    
    while(cap.isOpened()):
        ret, image = cap.read()

        if ret == True:
            [h, w, c] = image.shape
            if c>3:
                image = image[:,:,:3]

            # the core: regress position map
            s_time = time()
            if args.isDlib:
                max_size = max(image.shape[0], image.shape[1])
                if max_size> 1000:
                    image = rescale(image, 1000./max_size)
                    image = (image*255).astype(np.uint8)
                print "debug1 {}".format(time() - s_time)
                pos = prn.process(image) # use dlib to detect face
                print "debug2 {}".format(time() - s_time)
            else:
                if image.shape[0] == image.shape[1]:
                    image = resize(image, (256,256))
                    pos = prn.net_forward(image/255.) # input image has been cropped to 256x256
                else:
                    box = np.array([0, image.shape[1]-1, 0, image.shape[0]-1]) # cropped with bounding box
                    pos = prn.process(image, box)
            
            image = image/255.

            # 3D vertices
            vertices = prn.get_vertices(pos)
            save_vertices = vertices.copy()
            save_vertices[:,1] = h - 1 - save_vertices[:,1]

            # corresponding colors
            colors = prn.get_colors(image, vertices)

            # get landmarks
            kpt = prn.get_landmarks(pos)

            # estimate pose
            camera_matrix, pose = estimate_pose(vertices)

            # ---------- Plot
            # cv2.imshow('sparse alignment', plot_kpt(image, kpt))
            cv2.imshow('dense alignment', plot_vertices(image, vertices))
            # cv2.imshow('pose', plot_pose_box(image, camera_matrix, kpt))
            
            if cv2.waitKey(1) == 27:
                break
        else:
            break
    cap.release()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Joint 3D Face Reconstruction and Dense Alignment with Position Map Regression Network')

    parser.add_argument('--gpu', default='0', type=str,
                        help='set gpu id, -1 for CPU')
    parser.add_argument('--isDlib', default=True, type=ast.literal_eval,
                        help='whether to use dlib for detecting face, default is True, if False, the input image should be cropped in advance')
    main(parser.parse_args())
