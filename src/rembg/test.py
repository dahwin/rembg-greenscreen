import argparse
import glob
import io
import os
from distutils.util import strtobool
from PIL import Image
import filetype
from skimage import transform
from tqdm import tqdm

from .multiprocessing import parallel_greenscreen
from .u2net.detect import predict
from .bg import remove_many
from itertools import islice, chain
import moviepy.editor as mpy
import numpy as np
import time

if __name__ == '__main__':
    parallel_greenscreen("C:\\Users\\tim\\Videos\\test\\2021-01-31 14-05-36.mp4", 
                worker_nodes = 10, 
                cpu_batchsize = 50, 
                gpu_batchsize = 25)