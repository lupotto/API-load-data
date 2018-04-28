import numpy as np
import skimage
import skimage.io as io
import io
from io import BytesIO
# from lxml import etree
import sys
import xml.etree.ElementTree as ET
import re
import os
from os.path import isfile
import cv2


DATA_LOCATION = 'resources'


class Object(object):
    def __init__(self, name, xmin, ymin, xmax, ymax):
        self.name = name
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax

    def bbox_area(self):
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)


class Image(object):
    def __init__(self, idFolder, numImg, data, classes):
        self.idFolder = idFolder
        self.numImg = numImg
        self.data = data
        self.classes = classes


def loadDataset(DATA_LOCATION):
    main_path = os.path.join(os.path.expanduser('~'), DATA_LOCATION, 'AutelData')
    out_path = os.path.join(os.path.expanduser('~'),'outAutelData')

    main_folders = [f for f in os.listdir(main_path) if not isfile(os.path.join(main_path, f))]

    #os.makedirs(out_path)

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
                    # tree = ET.parse('/home/alupotto/resources/AutelData/Set3/MB0013/MB0013_000297.xml')
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



                        print(os.path.join(main_path, folder, subfolder, id))
                        new_img = printBoundingBoxes(img)

                        #print(os.path.join(out_path, folder, subfolder, img.idFolder +"_"+ img.numImg + ".jpg"),
                                   #new_img)
                        #cv2.imwrite(os.path.join(out_path, folder, subfolder, img.idFolder+"_"+img.numImg+".jpg"),new_img)

def printBoundingBoxes(image):
    font = cv2.FONT_HERSHEY_TRIPLEX
    fontScale = 0.75
    newimg = 0
    lineType = 1

    for i in (range(len(image.classes))):
        font_color = setColor(image.classes[i].name)
        bbox = cv2.rectangle(image.data, (image.classes[i].xmin, image.classes[i].ymin),
                             (image.classes[i].xmax, image.classes[i].ymax), font_color, 2)

        newimg = cv2.putText(bbox, image.classes[i].name, (image.classes[i].xmin - 5, image.classes[i].ymin - 5), font,
                             fontScale, font_color, lineType)

        #image.classes[i]
    # bbox = cv2.rectangle(image.data, (image.classes[0].xmin,image.classes[0].ymin),(image.classes[0].xmax,image.classes[0].ymax),(0,255,0),2)
    # newimg = cv2.putText(bbox,image.classes[0].name,(image.classes[0].xmin - 5 ,image.classes[0].ymin - 5 ),font,fontScale,font_color,lineType)

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
    loadDataset('resources')
