#!/usr/bin/python
# -*- coding: UTF-8 -*-

#    Copyright © 2020 Polyakov Sergey (PolSerg). All rights reserved.

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  (Это свободная программа: вы можете перераспространять ее и/или изменять
#   ее на условиях Стандартной общественной лицензии GNU в том виде, в каком
#   она была опубликована Фондом свободного программного обеспечения; либо
#   версии 3 лицензии, либо (по вашему выбору) любой более поздней версии.
#
#   Эта программа распространяется в надежде, что она будет полезной,
#   но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
#   или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной
#   общественной лицензии GNU.
#
#   Вы должны были получить копию Стандартной общественной лицензии GNU
#   вместе с этой программой. Если это не так, см.
#   <https://www.gnu.org/licenses/>.)


import Image
import os, zipfile
from bitarray import bitarray
import configparser
import sys

def fwrite(fh, imgFILENAME):
    im=Image.open(imgFILENAME).convert('1')
    pix=im.load()
    w=im.size[0]
    h=im.size[1]
    a = bitarray()

    for i in range(h):
        for j in reversed(range(0,w,8)):
            for x in range(j-8,j):
                a.append(pix[x,i]>=125)
    a.tofile(fh)    

if len(sys.argv)!=2 or len(sys.argv)==2 and sys.argv[1]=="-h":
    print '''
    Prusa SL1 to Sparkmaker WOW file converter of July 2020 by Polyakov Sergey (PolSerg)
    questions and suggestions can be sent by e-mail: polserg12x@mail.ru

    Usage: sl1ToWOW.py file[.sl1]'''
    sys.exit (1)

filename=sys.argv[1]
if filename.find(".sl1")==-1:
    filename+=".sl1"

zipFile = zipfile.ZipFile(filename, 'r')
zipFile.extractall(filename+"_sl1")
zipFile.close()

files = os.listdir(filename+"_sl1") 
images = filter(lambda x: x.endswith('.png'), files)
images.sort()

strStart='''G21;
G91;
M17;
M106 S0;
G28 Z0;
;W:480;
;H:854;
;L:1;
M106 S0;
G1 Z[lifting_height] F[upSpeed];
G1 Z-[lowering_height] F[downSpeed];
{{
'''

strLayer='''
}}
M106 S255;
G4 S[layerTime];
;L:[layerNumber];
M106 S0;
G1 Z[lifting_height] F[upSpeed];
G1 Z-[lowering_height] F[downSpeed];
{{
'''

strEnd='''
}}
M106 S255;
G4 S[layerTime];
M106 S0;
G1 Z10 F[upSpeed];
M18;
'''

with open(os.path.join(filename+"_sl1","config.ini")) as f:
    file_content = u'[dummy_section]\n' + f.read()

config_parser = configparser.RawConfigParser()
config_parser.read_string(file_content)


layerTime=config_parser.getint("dummy_section","expTime") #15
startLayerTime=config_parser.getint("dummy_section","expTimeFirst") #150
startlayers=config_parser.getint("dummy_section","numFade") #10
upSpeed=25
downSpeed=80
layerHeight=config_parser.getfloat("dummy_section","layerHeight") #0.1
lifting_height=5
lowering_height=lifting_height-layerHeight

with open(filename+".wow", 'wb') as fh:
     
    fh.write(strStart.replace('''[lifting_height]''',str(lifting_height)).replace('''[lowering_height]''',str(lowering_height)).replace('''[layerTime]''',str(startLayerTime)).replace('''[upSpeed]''',str(upSpeed)).replace('''[downSpeed]''',str(downSpeed)))
    strNewLayer=""
    layerNumber=1
    for filename in images:
        nLayerTyme=layerTime if layerNumber>startlayers+1 else startLayerTime
        fh.write(strNewLayer.replace('''[lifting_height]''',str(lifting_height)).replace('''[lowering_height]''',str(lowering_height)).replace('''[layerNumber]''',str(layerNumber)).replace('''[layerTime]''',str(nLayerTyme)).replace('''[upSpeed]''',str(upSpeed)).replace('''[downSpeed]''',str(downSpeed)))
        fwrite(fh, os.path.join("pr_archive",filename))
        strNewLayer=strLayer
        layerNumber+=1
    

    fh.write(strEnd.replace('''[upSpeed]''',str(upSpeed)).replace('''[downSpeed]''',str(downSpeed)).replace('''[layerTime]''',str(layerTime)))
    fh.close()    