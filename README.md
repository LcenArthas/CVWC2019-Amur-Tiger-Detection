# CWCV2019-Amur-Tiger-Detection

This source of the code is mainly for the **Tiger Re-ID in the Wild track** [CVWC2019](https://cvwc2019.github.io/challenge.html) @ICCV19 Workshop:

**To generate detected tiger pictures for Tiger Re-ID in the Wild**.

## Getting Started
### Clone the repo:

```
git clone https://github.com/LcenArthas/CWCV2019-Amur-Tiger-Detection.git
```
#### Dependencies

Tested under python3.

- python packages
  - pytorch==0.4.1
  - torchvision>=0.2.0
  - cython
  - matplotlib
  - numpy
  - scipy
  - opencv
  - pyyaml
  - packaging
  - [pycocotools](https://github.com/cocodataset/cocoapi)  — for COCO dataset, also available from pip.
  - tensorboardX  — for logging the losses in Tensorboard
- An NVIDAI GPU and CUDA 8.0 or higher. Some operations only have gpu implementation.

### Compilation

Compile the CUDA code:

```
cd lib  # please change to this directory
sh make.sh
```

It will compile all the modules you need, including NMS, ROI_Pooing, ROI_Crop and ROI_Align. (Actually gpu nms is never used ...)

## Training

**TO DO**

## Inference

### Data Preparation

Put the test images in the `{repo_root}/test/` folder under the repo.

### Download Pretrained Model

I use Faster-rcnn-Resnet50-FPN to train my model.

- [Trained weight](https://pan.baidu.com/s/1q5Wdzcq6aKtM1H_VugCe3w)

Download them and put them into the `{repo_root}/data/pretrained_model`.

And make sure the repo files as the following structure:
  ```
  coco
  ├── annotations
  |   ├── instances_minival2014.json
  │   ├── instances_train2014.json
  │   ├── instances_train2017.json
  │   ├── instances_val2014.json
  │   ├── instances_val2017.json
  │   ├── instances_valminusminival2014.json
  │   ├── ...
  |
  └── images
      ├── train2014
      ├── train2017
      ├── val2014
      ├──val2017
      ├── ...
  ```

