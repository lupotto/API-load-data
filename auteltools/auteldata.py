import numpy as np
import matplotlib.pyplot as plt
import sys
import xml.etree.ElementTree as ET
import re
import os
from os.path import isfile
import cv2
import pickle


#TODO:


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

    def show_values(self):

        print("Label name: {}".format(self.label_name))
        print("Xmax: {} Xmin: {} Xmax - Xmin: {}".format(self.xmax, self.xmin, self.xmax - self.xmin))
        print("Ymax: {} Ymin: {} Ymax - Ymin: {}".format(self.ymax, self.ymin, self.ymax - self.ymin))

class Autel:
    def __init__(self, data_location, read_all_data = False):
        """
        Constructor of Autel helper class for reading images and annotations
        :param data_location (str): location of folder data
        :return:
        """
        self.data_location = data_location
        self.img_dict = dict()

        if read_all_data:
            self.load_data()


    def load_data(self):

        main_path = os.path.join(os.path.expanduser('~'), self.data_location, 'AutelData')

        self.boolean = 0
        for root,dirs,files in os.walk(main_path, topdown=False):
            files.sort()
            for name_file in files:
                if name_file.endswith('.jpg'):
                    self.img_dict[name_file] = os.path.join(root, name_file)

                elif name_file.endswith('.xml'):
                    annotation = self.load_annotation(root, name_file, self.boolean)
                    annotation.show_annotation()

    def load_annotation(self, root, name_xml, boolean):

        tree = ET.parse(os.path.join(root, name_xml))
        root = tree.getroot()
        name_jpg = root.find('filename').text

        if name_jpg in self.img_dict:
            path_file = self.img_dict[name_jpg]
            width = root.find('size').find('width').text
            height = root.find('size').find('height').text
            depth = root.find('size').find('depth').text

            if self.check_sizes(int(width), int(height), int(depth)):
                labels = self.parse_labels(root)
                annotation = Annotation(name_jpg,path_file,width,height,depth,labels)
                return annotation
            #TODO: else create csv with incorrect weights and prompt error
        else:
            #TODO: create prompt error
            self.boolean += 1




    def check_sizes(self, width, height, depth):
        if width == 1280 and height == 720 and depth == 3:
            return True
        return False

    def parse_labels(self, root):

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