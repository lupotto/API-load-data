import numpy as np
import matplotlib.pyplot as plt
import sys
import xml.etree.ElementTree as ET
import re
import os
from os.path import isfile
import cv2
import pickle
import pandas as pd
from collections import defaultdict

#TODO 2: Create .pkl
#TODO 3: Without .pkl
#TODO 4: Batch size
#TODO 5: Update
#TODO 6: Show stadistics

class Annotation(object):
    def __init__(self, file_name, path_file, width, height, depth, labels):
        """
         Constructor of the XML file for read all the parameters related with the image (Folder, Image associated (.jpg),
         dimensions and classes inside)
         :param folder_name (str)
         :param file_name (str): name of the jpg image
         :param shape_image (int array): shape of the image (width, height, depth)
         :param classes (array of Label): array of classes of the image
         :return:
         """
        self.file_name = file_name
        self.path_file = path_file
        self.width = width
        self.height = height
        self.depth = depth
        self.labels = labels

    def show_annotation(self):
        print(self.file_name)
        print(self.path_file)
        print(self.width)
        print(self.height)
        print(self.depth)
        for i in range(len(self.labels)):
            print(self.labels[i].show_values())

    def get_labels_name(self):
        names_labels = []
        for i in range(len(self.labels)):
            names_labels.append(self.labels[i].name)

        return names_labels

class Label(object):
    def __init__(self, label_name, xmin, ymin, xmax, ymax):
        """
        Constructor of a class of the image.
        :param label_name (str): name of the label
        :param xmin (int): x min bounding box
        :param ymin (int): y min bounding box
        :param xmax (int): x max bounding box
        :param ymax (int): y max bounding box
        :return:
        """
        self.label_name = label_name
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def get_name(self):
        return self.label_name

    def show_values(self):

        print("Label name: {}".format(self.label_name))
        print("Xmax: {} Xmin: {} Xmax - Xmin: {}".format(self.xmax, self.xmin, self.xmax - self.xmin))
        print("Ymax: {} Ymin: {} Ymax - Ymin: {}".format(self.ymax, self.ymin, self.ymax - self.ymin))

class Autel:
    def __init__(self, data_location, read_all_data = False, batch_size = 1):
        """
        Constructor of Autel helper class for reading images and annotations
        :param data_location (str): location of folder data
        :return:
        """
        self.batch_size = batch_size
        self.data_location = data_location
        self.img_dict = dict()
        self.img_wrong = defaultdict(list)

        if read_all_data:
            self.load_data()

            if bool(self.img_wrong):
                df = pd.DataFrame(self.img_wrong,
                                  columns=['image_name', 'path', 'shape', 'labels'])
                df.to_csv(os.path.join(os.path.expanduser('~'), 'outAutelData',
                                            'csv_wrong', 'images_wrong_2.csv'))


    def load_data(self):

        main_path = os.path.join(os.path.expanduser('~'), self.data_location, 'AutelData')


        for root,dirs,files in os.walk(main_path, topdown=False):
            files.sort()
            for name_file in files:
                if name_file.endswith('.jpg'):
                    self.img_dict[name_file] = os.path.join(root, name_file)

                elif name_file.endswith('.xml'):
                    annotation = self.load_annotation(root, name_file)


    def load_annotation(self, root, name_xml):

        tree = ET.parse(os.path.join(root, name_xml))
        root = tree.getroot()
        name_jpg = root.find('filename').text

        aux = 0
        annotation = 0
        if name_jpg in self.img_dict:
            path_file = self.img_dict[name_jpg]
            width = root.find('size').find('width').text
            height = root.find('size').find('height').text
            depth = root.find('size').find('depth').text

            if self.check_sizes(int(width), int(height), int(depth)):
                labels = self.parse_labels(root)
                annotation = Annotation(name_jpg, path_file, width, height, depth, labels)
            else:
                #print("Image {} with incorrect shape: ({},{},{})".format(name_jpg,width,height,depth))
                self.generate_dict_wrong_image(name_jpg, path_file,
                                                int(width), int(height), int(depth), root)

        else:
            #TODO 1: create prompt error

            aux += 1

        return annotation

    def generate_dict_wrong_image(self, name_jpg, path_file, width, height, depth, root):
        self.img_wrong['image_name'].append(name_jpg)
        self.img_wrong['path'].append(path_file)
        self.img_wrong['shape'].append("({},{},{})".format(int(width), int(height), int(depth)))
        labels = self.parse_labels(root)
        names = []
        for i in range(len(labels)):
            names.append(labels[i].get_name())

        labels = "/".join(map(str, names))
        self.img_wrong['labels'].append(labels)

    def check_sizes(self, width, height, depth):
        """
        Function for verifiy the size of the images
        :param width (int):
        :param height (int):
        :param depth (int):
        :return: boolean
        """
        if width == 1280 and height == 720 and depth == 3:
            return True
        return False

    def parse_labels(self, root):
        """
        Function that parse all the labels of the xml file
        :param root:
        :return:
        """
        objects = root.findall('object')
        array_labels = []
        for i in range(len(objects)):
            name = objects[i].find('name').text
            xmin = int(objects[i].find('bndbox').find('xmin').text)
            ymin = int(objects[i].find('bndbox').find('ymin').text)
            xmax = int(objects[i].find('bndbox').find('xmax').text)
            ymax = int(objects[i].find('bndbox').find('ymax').text)
            label = Label(name,xmin,ymin,xmax,ymax)
            array_labels.append(label)

        return array_labels