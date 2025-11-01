# encoding: utf-8
import sys
import os
import random
import shutil
import string
import numpy as np

length_x = 400

def read_1_3(filename_r,filename_w):
    # print filename
    read = open(filename_r, "rb")
    write = open(filename_w, "wb")
    
    count = len(read.readlines())
    read.seek(0)
    
    write.write(read.readline())
    index_read = 1

    indexs = [i for i in range(1,count)]
    random_line_indexs = random.sample(indexs,400)

    for line in read:
        if index_read in random_line_indexs:
            write.write(line)
            pass
        index_read += 1
        pass

    pass

def read_1(filename_r,filename_w,num):
    # print filename
    read = open(filename_r, "rb")
    write = open(filename_w, "wb")
    
    write.write(read.readline())
    index_read = 1

    for line in read:
        for i in range(0,num):
            write.write(line)
            pass
        index_read += num
        pass

    pass
if __name__ == '__main__':
    read_1("plot_data","plot_data_",2)
    read_1_3("plot_data_","plot_data_1-3")