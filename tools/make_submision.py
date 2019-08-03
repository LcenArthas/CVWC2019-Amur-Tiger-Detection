#--------------------------------------------
#提交之前的最后一步，根据txt文件生成coco提交形式
#同时根据原始的图片切分出来老虎的图片
#同时制作了为了 wide reid的json文件
#-------------------------------------------

import os
import os.path as apt
import shutil
import sys
import json
import xml

# -*- coding=utf-8 -*-
#!/usr/bin/python

import os
import json
from tqdm import tqdm
from PIL import Image

# 检测框的ID起始值
START_BOUNDING_BOX_ID = 0
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

# 得到图片的长和宽
def get_pic_size(filename):
    img = Image.open(os.path.join('../test/', filename))          #目录是测试目录
    return img.size

#根据结果切割图片
def crop_pic(filename, ann, id):
    img = Image.open(os.path.join('../test/', filename))
    img = img.crop(ann)
    img.save('../reid_test/' + str(id).zfill(6) + '.jpg')

#传进来是标签列表名字，标签根目录，要保存的文件名字
def convert(txt_list, txt_dir, json_file):
    '''
    :param xml_list: 需要转换的XML文件列表
    :param xml_dir: XML的存储文件夹
    :param json_file: 导出json文件的路径
    :return: None
    '''
    #--------制作json为了WILD REID----------------------------------------------
    wide_boxlist = []
    result_list = []

    list_fp = txt_list

    categories = PRE_DEFINE_CATEGORIES
    bnd_id = START_BOUNDING_BOX_ID
    for line in tqdm(list_fp):                                        #循环标签列表
        line = line.strip()
        # 解析TXT
        txt_f = os.path.join(txt_dir, line)
        f = open(txt_f)
        ann = f.readlines()
        f.close()

        #取出图片名字
        filename = line.split('.')[0] + '.jpg'

        ## The filename must be a number
        image_id = get_filename_as_int(filename)  # 图片ID

        # 处理每个标注的检测框
        for obj in ann:
            wide_dic = {}
            json_dic = {}
            obj = obj.split(' ')

            #筛选出低分的框
            if float(obj[-1]) < 0.90:
                continue

            # 取出检测框类别名称
            category = 'Tiger'
            # 更新类别ID字典
            if category not in categories:
                new_id = len(categories)
                categories[category] = new_id
            category_id = categories[category]

            xmin = int(float(obj[1]))
            ymin = int(float(obj[2]))
            xmax = int(float(obj[3]))
            ymax = int(float(obj[4]))

            assert(xmax > xmin)
            assert(ymax > ymin)
            o_width = abs(xmax - xmin)
            o_height = abs(ymax - ymin)

            #-------制作wide reid json---------------------------------------------
            wide_dic['bbox_id'] = bnd_id
            wide_dic['image_id'] = image_id
            wide_dic['pos'] = [xmin, ymin, o_width, o_height]

            #-------制作检测结果----------------------------------------------------
            json_dic['image_id'] = image_id
            json_dic['category_id'] = category_id
            json_dic['bbox'] = [xmin, ymin, o_width, o_height]
            json_dic['score'] = 0.99999

            bnd_id = bnd_id + 1

            #切割每个图片出来并且保存
            crop_pic(filename, (xmin, ymin, xmax, ymax), bnd_id-1)
            #放入wide—reid json
            wide_boxlist.append(wide_dic)
            result_list.append(json_dic)

    with open(json_file, 'w') as j:
        json.dump(result_list, j)

    # 导出wide reid json
    with open('../wide_bbox.json', 'w') as j:
        json.dump(wide_boxlist, j)

def make_submission():
    root_path = '../output'
    result_list = os.listdir(root_path)
    json_file = '../det_submission.json'
    convert(result_list, root_path, json_file)                                  #转换
