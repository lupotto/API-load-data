import numpy as np
import skimage
import skimage.io as io
import io
from io import BytesIO
import matplotlib.pyplot as plt
import sys
import xml.etree.ElementTree as ET
import re
import os
from os.path import isfile
import cv2
import pickle
import pandas
from collections import Counter


DATA_LOCATION = 'resources'



class Object(object):
    def __init__(self, name, xmin, ymin, xmax, ymax):
        self.name = name
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def getArea(self):
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)

    def showDimensions(self):
        difX = self.xmax-self.xmin
        difY = self.ymax - self.ymin

        print("Id: {}".format(self.name))
        print("Xmax: {} Xmin: {} Xmax - Xmin: {}".format(self.xmax,self.xmin,self.xmax-self.xmin))
        print("Ymax: {} Ymin: {} Ymax - Ymin: {}".format(self.ymax, self.ymin, self.ymax - self.ymin))
        print("Area: {}".format(difX*difY))

class Image(object):
    def __init__(self, idFolder, numImg, data, classes):
        self.idFolder = idFolder
        self.numImg = numImg
        self.data = data
        self.classes = classes



def loadDataset(DATA_LOCATION):
    main_path = os.path.join(os.path.expanduser('~'), DATA_LOCATION, 'AutelData')
    out_path = os.path.join(os.path.expanduser('~'),'outAutelData')
    #os.makedirs(out_path)

    main_folders = [f for f in os.listdir(main_path) if not isfile(os.path.join(main_path, f))]

    #stadistics dicts
    areas = {}
    times = {}

    test = 0
    # 1st level  #FOLDER IS 1ST BRANCH
    for folder in main_folders:
        #os.makedirs(os.path.join(out_path,folder))

        folders_1 = os.listdir(os.path.join(main_path, folder))

        for subfolder in folders_1:
            #os.makedirs(os.path.join(out_path, folder,subfolder))

            files = os.listdir(os.path.join(main_path, folder, subfolder))
            files.sort()

            for id in files:

                if (id.endswith('.jpg')):
                    jpg_folder = re.split('[_.]', id)[0]
                    jpg_img = re.split('[_.]', id)[1]
                    data = cv2.imread(os.path.join(main_path, folder, subfolder, id))

                if (id.endswith('.xml')):

                    xml_folder = re.split('[_.]', id)[0]
                    xml_img = re.split('[_.]', id)[1]

                    tree = ET.parse(os.path.join(main_path, folder, subfolder, id))
                    root = tree.getroot()
                    objects = root.findall('object')

                    classes = []

                    for i in range(len(objects)):
                        name = objects[i].find('name').text
                        xmin = int(objects[i].find('bndbox').find('xmin').text)
                        ymin = int(objects[i].find('bndbox').find('ymin').text)
                        xmax = int(objects[i].find('bndbox').find('xmax').text)
                        ymax = int(objects[i].find('bndbox').find('ymax').text)
                        classes.append(Object(name, xmin, ymin, xmax, ymax))

                    if jpg_folder == xml_folder and jpg_img == xml_img:

                        img = Image(jpg_folder, jpg_img, data, classes)
                        count_classes_areas(img,areas,times)

                        new_img = printBoundingBoxes(img)

                        #print(os.path.join(out_path, folder, subfolder, img.idFolder +"_"+ img.numImg + ".jpg"),
                        #   new_img)
                        #cv2.imwrite(os.path.join(out_path, folder, subfolder, img.idFolder+"_"+img.numImg+".jpg"),new_img)

    #createDicts(areas,times)

def createHistogram():

    with open("areas.txt", "rb") as myFile:
        areas = pickle.load(myFile)

    with open("times.txt", "rb") as myFile:
        times = pickle.load(myFile)

    areas.pop('200',None)
    times.pop('200',None)

    

    names = list(areas.keys())
    pixel_values = list(areas.values())
    times_values = list(times.values())

    fig, axs = plt.subplots(1,2 , figsize=(9, 4))

    total = pixel_values/times_values
    axs[0].bar(names, total)
    axs[1].bar(names,times_values)
    axs[0].set_title('Pixels')
    axs[1].set_title('Times')
    plt.savefig('Class stadistics')
    plt.show()

def createDicts(areas,times):

    with open("areas.txt", "wb") as f:
        pickle.dump(areas, f)
    with open("times.txt","wb") as f:
        pickle.dump(times,f)

def count_classes_areas(image,areas,times):

    for i in (range(len(image.classes))):

        if image.classes[i].name in areas:
            areas[image.classes[i].name] += image.classes[i].getArea()
            times[image.classes[i].name] += 1
        else:
            areas[image.classes[i].name] = image.classes[i].getArea()
            times[image.classes[i].name] = 1

def printBoundingBoxes(image):
    font = cv2.FONT_HERSHEY_TRIPLEX
    fontScale = 0.75
    newimg = 0
    lineType = 1
    area = 0
    for i in (range(len(image.classes))):
        font_color = setColor(image.classes[i].name)
        bbox = cv2.rectangle(image.data, (image.classes[i].xmin, image.classes[i].ymin),
                             (image.classes[i].xmax, image.classes[i].ymax), font_color, 2)

        newimg = cv2.putText(bbox, image.classes[i].name, (image.classes[i].xmin - 5, image.classes[i].ymin - 5), font,
                             fontScale, font_color, lineType)


        #print("Num {} {}: Area: {}".format(image.classes[i].name,i,area))

   # print(area)
    cv2.imshow('draw', newimg)

    k = cv2.waitKey(1)

    if k == 27:  # If escape was pressed exit
        cv2.destroyAllWindows()
        sys.exit()

    return newimg

def setColor(name):
    font_color = (0, 0, 0)
    if name == 'Car':
        font_color = (255, 0, 0)
    elif name == 'Person':
        font_color = (0, 0, 255)
    elif name == 'Vehicle':
        font_color = (255, 255, 255)
    elif name == 'Rider':
        font_color = (204, 204, 0)
    elif name == 'Animal':
        font_color = (255, 140, 0)
    elif name == 'Boat':
        font_color = (0, 140, 255)

    else:
        print("class not found")

    return font_color


if __name__ == '__main__':


    #loadDataset('resources')
    createHistogram()