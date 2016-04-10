# -*- encoding: UTF-8 -*-
# 此脚本的作用是以“zm_deleting.txt"为参照，删除词库中的一些不常用词组，以让词库更加高效，不会出现一些无谓的词条。
# usage：delete_redundant_words.py filename (脚本和zm_deleting.txt要在同一目录下）
# "zm_deleting.txt"我放在gsealine的gist上以便随时更新：https://gist.github.com/gsealine/d4e566441a9948c7b0f49fd44cb5a06e

import re
import os
import sys
import codecs
# 用codecs以指定编码打开文件很有效，不然有时会有错误
filepath = sys.argv[1]
f = codecs.open(filepath, "r", 'utf-8')
lines = f.readlines()           #readlines()能生成一个list
f.close()

f_redundant = codecs.open(r'rudundant_words_in_jd.txt', "r", 'utf-8')
rdlines = f_redundant.readlines()
f_redundant.close()

filename = os.path.basename(filepath)
newFilename = "new_" + filename
newf = codecs.open(newFilename, "w", 'utf-8')


# 考虑到词库开头可能有rime特有的说明语句，先记录下词库真正开始的行数 beginrow
for i,line in enumerate(lines):
    beginrow = i
    if re.match(u'^\u4e00\ta', line):
        break

# wblines 是词库文件的所有字词组成的列表
wbwords = [line.split()[0] for line in lines[beginrow:]]   # 这是列表生成器的用法，速度更快

# rdwords 是所有待删词组成的列表
rdwords = [rdline.split()[0] for rdline in rdlines]
setrdwords = set(rdwords)
# 将其转化为集合后再用 if …… in …… 语句查找会快很多

for line in lines[:beginrow]:
    newf.write(line)

for i,wbword in enumerate(wbwords):
    if (wbword in setrdwords):
        continue
    newf.write(lines[i + beginrow])
# wbwords 和 lines 两个列表的顺序要对应

newf.close()
