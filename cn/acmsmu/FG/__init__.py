'''
@desc: FG群文件处理
@author: Martin Huang
@time: created on 2020/4/4 15:04
@修改记录:
'''
import nonebot
import time
from nonebot.log import logger
from Utils.JsonUtils import JsonUtils
from Utils.IOUtils import IOUtils
from Utils.ml.TextRank4ZH.Segmentation import STOP_WORD_PATH, MYDICT_PATH
from .pathSetting import CONFIG_FILE, GROUP_DATA_PATH
from pathlib import Path
import shutil
from .Timer import *

configuration = JsonUtils.json2Dict(CONFIG_FILE)
groupInfo = configuration['groupInfo']
for each in groupInfo:
    fpath: Path = GROUP_DATA_PATH / each['groupId']
    fpath.mkdir(parents=True, exist_ok=True)
    try:
        dataDict = dict()
        dataDict['flag'] = True
        dataDict['file'] = 'chatA.txt'
        IOUtils.serializeObj2Pkl(dataDict, fpath / 'var.pkl')
    except FileExistsError as e:
        logger.error(f"写入Pickel出错了，{e}")
        continue
if not STOP_WORD_PATH.exists():
    shutil.copy(Path(__file__).parent / "stopwords.txt", STOP_WORD_PATH)
if not MYDICT_PATH.exists():
    shutil.copy(Path(__file__).parent / "myDict.txt", MYDICT_PATH)
bot = nonebot.get_bot()

print('初始化完成')

@bot.on_message('group')
async def handleGroupMsg(session):
    groupInfo = configuration['groupInfo']
    for each in groupInfo:
        if each['groupId'] == str(session['group_id']):
            # 读取每个群文件夹的pkl
            dataDict = IOUtils.deserializeObjFromPkl(GROUP_DATA_PATH / each['groupId'] / 'var.pkl')
            # 确定flag的值
            flag = dataDict['flag']
            # 确定要往哪一个文件中写入聊天记录
            msg = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ' ' + str(session['user_id']) + '\n' + session['raw_message'] + '\n'
            if flag:
                with open(GROUP_DATA_PATH / each['groupId'] / 'chatA.txt', 'a', encoding='utf-8') as fileA:
                    fileA.write(msg)
            else:
                with open(GROUP_DATA_PATH / each['groupId'] / 'chatB.txt', 'a', encoding='utf-8') as fileB:
                    fileB.write(msg)
            break
