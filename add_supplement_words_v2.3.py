# -*- encoding: UTF-8 -*-
# 此脚本的作用是将supplement_bank.txt中的词按指定顺序添加到词库(word bank)中
# usage：add_supplement.py filename/filepath (需和supplement_bank.txt在同一目录下）
# 它将在当前文件夹生成一个新文件，命名为 new_filename
# 在变量中 supplement_bank 简称 sb, word bank 简称 wb

# 这个介绍下这个脚本的实现思路：
# 1. 建一个字典 sbdict, 以supplement_bank中的所有编码为key，以编码在 supplement_bank 和 word bank 中所对应的词为value。
# 2. 在sbdict中为词排序，排序流程见下：
# 2.1 假设某个编码对应的字词数为10，组成一个列表sglwords，另外建一个列表 normlist = [0, 1, …… , 9]
# 2.2 遍历sglwords，若其中的某字有权重，则在nromlist中删除这个权重
# 2.3 再次遍历sglistwords，为没有权重的字依次从normlist取一个值作为权重
#     并同时为sglistwords中的所有字再加一个新权重表示目前的位置关系
# 2.4 根据上面的两个权重对sglistwords进行多重排序
# 2.5 去掉sglistwords中的排序信息
# 3. 又建一个字典 wbdict，以word bank中的所有编码为key，以编码在word bank所对应的词为value
# 4. 合并 wbdict和 sbdict（sbdict 覆盖 wbdict），并按key排序
# 5. 输出 合并后的字典，程序结束

import re
import os
import sys
import codecs
from time import time 
from collections import OrderedDict    

# filepath = sys.argv[1]
filepath = r'bzzm.jd.dict.yaml'
f = codecs.open(filepath, "r", 'utf-8')
# 用codecs以指定编码打开文件很有效，不然有时会有错误
lines = f.readlines()           #readlines()能生成一个list
f.close()

f_sb = codecs.open(r'supplement_bank.txt', "r", 'utf-8')
sblines = f_sb.readlines()
f_sb.close()

filename = os.path.basename(filepath)
newFilename = "new_" + filename
newf = codecs.open(filepath, "w", 'utf-8')

for i,line in enumerate(lines):
    beginrow = i
    if re.match(u'^\u4e00\ta', line):
        break

# sbdict 是将要生的一个以custom_words.txt中的所有编码为键，
# 以编码所对应的字词为值的字典，我们所要进行的排序工作也将在里面进行。

sbdict = {}
for sbline in sblines:
    sbline_split = sbline.split()
    sbword = sbline_split[0]
    sbcode = sbline_split[1]
    if (len(sbline_split) == 3):
        weight = int(sbline_split[2])
    else:
        weight = 0
    try:
        sbdict[sbcode].append([sbword, weight])
    except KeyError:
        sbdict[sbcode] = [[sbword, weight]]
# sbdict 中的值是一个二元列表，每个字和他对应的权重先组成一个列表，然后有相同编码的字再又组成列表
# sbdict 此时格式为：{'eyo': [['苏', 0], ['你', 1]], …… }

# 下面这个循环的作用是按编码为 sbdict 加入词库中的字词（append 在后面）
# 并顺带将原词库建成一个字典
wbdict = {}
sbkeys = set(sbdict.keys())
for line in lines[beginrow:]:
    wbcode = line.split()[1] # wbcode 全称 word bank code
    wbword = line.split()[0]
    if wbcode in sbkeys:
        sglwords = sbdict[wbcode]   # sglwords 全称 single list words，
        if wbword not in [subl[0] for subl in sglwords]:   # 此时sglwords形式为 [['苏', 0] ……]
            sbdict[wbcode].append([wbword])
    try:
        wbdict[wbcode].append(wbword)
    except KeyError:
        wbdict[wbcode] = [wbword]
# 当前的 sbdict 是这样的 {'txar': [['序列', 0], ['决裂']], 'wylo': [['官网', 0], ['扇贝']]}
# 当前的 wbdict 是这样的 {'txar': ['决裂', '序列'] …… }

# 下面的循环是为字典排序（这是程序的核心），有两个规则：
# 1. 当指定了顺序时严格按指定的顺序来排，若顺序重复，则它们会排在一起，再按它们在码表中的先后顺序来排
# 2. 当没有指定顺序时，在保证指定己指定的顺序不动的情况下按先后顺序排。
for key in sbdict:
    sglwords = sbdict[key]   # sglwords 为 [['苏', 0], ['你'] ……]
    normlist = [i for i in range(0,len(sglwords))]
    for sglword in sglwords:
        if (len(sglword) == 2 and sglword[1] in normlist):
            normlist.remove(sglword[1])

    position = 0 # 标记上初始的位置关系，这样当序号一样时，按此来排序
    for sglword in sglwords:
        if (len(sglword) == 1):
            sglword.append(normlist[0])
            del normlist[0]
        sglword.append(position)
        position += 1
    # 此时sglwords形式为 [['苏', 1, 0], ['你',0, 1] ……]
    sbdict[key] = sorted(sglwords, key = lambda v: (v[1], v[2]))   # 多重排序，很cool

    
for key in sbdict:
    sglwords = sbdict[key]
    sbdict[key] = [subl[0] for subl in sglwords]
# 这是去掉 sglwords 中的排序信息，此时sglwords为 ['苏','你']

wbmerge = dict(wbdict, **sbdict)
wbmerge = OrderedDict(sorted(wbmerge.items(), key = lambda d: d[0]))

for line in lines[:beginrow]:
    newf.write(line)

for code, words in wbmerge.iteritems():
    for word in words:
        concatline = word + '\t' + code + '\n'
        newf.write(concatline)

newf.close()