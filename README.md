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
