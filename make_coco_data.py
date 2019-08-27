#---------------------------------------------------
#用于转换原始的数据格式
#---------------------------------------------------

import numpy as np
import json
import xml.etree.ElementTree as ET
import os
import os.path as opt
import shutil

# 检测框的ID起始值
START_BOUNDING_BOX_ID = 1
# 类别列表无必要预先创建，程序中会根据所有图像中包含的ID来创建并更新
PRE_DEFINE_CATEGORIES = {"Tiger":1}

def get(root, name):
    vars = root.findall(name)
    return vars

def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise NotImplementedError('Can not find %s in %s.'%(name, root.tag))
    if length > 0 and len(vars) != length:
        raise NotImplementedError('The size of %s is supposed to be %d, but is %d.'%(name, length, len(vars)))
    if length == 1:
        vars = vars[0]
    return vars

# 得到图片唯一标识号
def get_filename_as_int(filename):
    try:
        filename = os.path.splitext(filename)[0]
        return int(filename)
    except:
        raise NotImplementedError('Filename %s is supposed to be an integer.'%(filename))

#传进来是标签列表名字，标签根目录，要保存的文件名字
def convert(xml_list, xml_dir, json_file):
    '''
    :param xml_list: 需要转换的XML文件列表
    :param xml_dir: XML的存储文件夹
    :param json_file: 导出json文件的路径
    :return: None
    '''
    list_fp = xml_list
    # 标注基本结构
    json_dict = {"images":[],
                 "type": "instances",
                 "annotations": [],
                 "categories": []}
    categories = PRE_DEFINE_CATEGORIES
    bnd_id = START_BOUNDING_BOX_ID
    for line in list_fp:                                        #循环标签列表
        line = line.strip()
        print("buddy~ Processing {}".format(line))
        # 解析XML
        xml_f = os.path.join(xml_dir, line)
        tree = ET.parse(xml_f)
        root = tree.getroot()
        # path = get(root, 'path')
        # # 取出图片名字
        # if len(path) == 1:
        #     filename = os.path.basename(path[0].text)
        # elif len(path) == 0:
        #     filename = get_and_check(root, 'filename', 1).text
        # else:
        #     raise NotImplementedError('%d paths found in %s'%(len(path), line))

        #取出图片名字
        # filename = get(root, 'filename')[0].text
        filename = line.split('.')[0] + '.jpg'
        print(filename)
        ## The filename must be a number
        image_id = get_filename_as_int(filename)                # 图片ID

        size = get_and_check(root, 'size', 1)
        # 图片的基本信息
        width = int(get_and_check(size, 'width', 1).text)
        height = int(get_and_check(size, 'height', 1).text)
        image = {'file_name': filename,
                 'height': height,
                 'width': width,
                 'id':image_id}
        json_dict['images'].append(image)
        ## Cruuently we do not support segmentation
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        # 处理每个标注的检测框
        for obj in get(root, 'object'):
            # 取出检测框类别名称
            category = get_and_check(obj, 'name', 1).text
            # 更新类别ID字典
            if category not in categories:
                new_id = len(categories)
                categories[category] = new_id
            category_id = categories[category]
            bndbox = get_and_check(obj, 'bndbox', 1)
            xmin = int(get_and_check(bndbox, 'xmin', 1).text) - 1
            ymin = int(get_and_check(bndbox, 'ymin', 1).text) - 1
            xmax = int(get_and_check(bndbox, 'xmax', 1).text)
            ymax = int(get_and_check(bndbox, 'ymax', 1).text)
            assert(xmax > xmin)
            assert(ymax > ymin)
            o_width = abs(xmax - xmin)
            o_height = abs(ymax - ymin)
            annotation = dict()
            annotation['area'] = o_width*o_height
            annotation['iscrowd'] = 0
            annotation['image_id'] = image_id
            annotation['bbox'] = [xmin, ymin, o_width, o_height]
            annotation['category_id'] = category_id
            annotation['id'] = bnd_id
            annotation['ignore'] = 0
            # 设置分割数据，点的顺序为逆时针方向
            annotation['segmentation'] = [[xmin,ymin,xmin,ymax,xmax,ymax,xmax,ymin]]

            json_dict['annotations'].append(annotation)
            bnd_id = bnd_id + 1

    # 写入类别ID字典
    for cate, cid in categories.items():
        cat = {'supercategory': 'none', 'id': cid, 'name': cate}
        json_dict['categories'].append(cat)
    # 导出到json
    json_fp = open(json_file, 'w')
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()


if __name__ == '__main__':
    # -----------------------------------------------
    # 用于创建正规的VOC格式数据集
    # ----------------------------------------------
    root = './data/Original_train/'

    # creat folder
    if not opt.exists(root + 'data/'):
        os.makedirs(root + 'data/')
        os.makedirs(root + 'data/VOCdevkit/')
        os.makedirs(root + 'data/VOCdevkit/' + 'VOC2007/')

    # copy and rename
    shutil.copytree(root + 'atrw_anno_detection_train/Annotations/',
                    root + 'data/VOCdevkit/' + 'VOC2007/' + 'Annotations/')
    shutil.copytree(root + 'atrw_detection_train/trainval/',
                    root + 'data/VOCdevkit/' + 'VOC2007/' + 'JPEGImages/')
    shutil.copytree(root + 'atrw_anno_detection_train/ImageSets/Main/',
                    root + 'data/VOCdevkit/' + 'VOC2007/' + 'Main')
    #-------------------------------------------------------------
    # 创建COCO数据集
    #-------------------------------------------------------------

    print('Start transform to coco style.....')
    if not opt.exists('./data/coco/'):
        os.makedirs('./data/coco/')
        os.makedirs('./data/coco/' + 'annotations/')
        os.makedirs('./data/coco/' + 'images/')

    root_path = './data/Original_train/data/VOCdevkit/VOC2007/'
    xml_dir = os.path.join(root_path, 'Annotations')                        #标签根目录

    xml_labels = os.listdir(os.path.join(root_path, 'Annotations'))         #标签列表
    np.random.shuffle(xml_labels)
    # split_point = int(len(xml_labels)/10)                                 #划分验证集

    # validation data
    # xml_list = xml_labels[0:split_point]
    # json_file = './instances_val2014.json'
    # convert(xml_list, xml_dir, json_file)
    # for xml_file in xml_list:
    #     img_name = xml_file[:-4] + '.jpg'
    #     shutil.copy(os.path.join(root_path, 'JPEGImages', img_name),
    #                 os.path.join(root_path, 'val2014', img_name))
    # train data
    xml_list = xml_labels[:]
    json_file = './data/coco/annotations/instances_train2017.json'
    convert(xml_list, xml_dir, json_file)                                  #转换

    #复制图片文件夹
    print('Start copy images.....')
    shutil.copytree('./data/Original_train/data/VOCdevkit/VOC2007/JPEGImages',
                    './data/coco/images/train2017')

    print('Success!')