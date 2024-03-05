"""
@Desc: 每日聊天信息总结，生成每日热词和词云
@Author: Martin Huang
@Date: 2020-04-03 10:01:18
@Modify Notes: 
"""

from Utils.ml.TextRank4ZH import TextRank4Keyword
from Utils.JsonUtils import JsonUtils
from Utils.IOUtils import IOUtils
from PIL import Image
from wordcloud import WordCloud
import time
import re
import random
import traceback
import numpy as np
from pathlib import Path
from nonebot.log import logger
from nonebot import MessageSegment
from base64 import b64encode
from .pathSetting import CONFIG_FILE, GROUP_DATA_PATH, IMAGE_PATH, WC_PATH


class DailyConlusion:

    def __init__(self, groupId):
        self.__configuration = JsonUtils.json2Dict(CONFIG_FILE)
        self.__groupId = groupId
        GROUP_PATH = GROUP_DATA_PATH / self.__groupId
        GROUP_PATH.mkdir(parents=True, exist_ok=True)
        dataDict = IOUtils.deserializeObjFromPkl(GROUP_PATH / "var.pkl")
        # 确定使用哪个文件
        self.__useFile = dataDict["file"]
        # 结束时间即为运行这个程序的当前时间
        self.__endTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.__beginTime = None
        self.__chatlog = self.__cleaning()
        for each in self.__configuration["template"]:
            if each["groupId"] == groupId:
                self.__template = each["content"]
                break

    # 数据预处理
    def __cleaning(self):
        chatlog = ""
        CUR_PATH: Path = GROUP_DATA_PATH / self.__groupId / self.__useFile
        try:
            with open(CUR_PATH, "r", encoding="utf-8") as f:
                isFirst = True
                for eachLine in f:
                    # 获取聊天记录开始时间
                    if isFirst:
                        res = re.search(
                            "^\d{4}-\d{2}-\d{1,2} \d{1,2}:\d{2}:\d{2}", eachLine
                        )
                        pos = res.span()
                        self.__beginTime = eachLine[pos[0] : pos[1]]
                        isFirst = False
                    else:
                        if (
                            re.search(
                                "^\d{4}-\d{2}-\d{1,2} \d{1,2}:\d{2}:\d{2} \d{5,11}",
                                eachLine,
                            )
                            is None
                        ):
                            # 正则非贪婪模式 过滤CQ码
                            eachLine = re.sub("\[CQ:\w+,.+?\]", "", eachLine)
                            # 过滤URL
                            eachLine = re.sub(
                                "(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]",
                                "",
                                eachLine,
                            )
                            # 特殊情况过滤
                            eachLine = eachLine.replace(
                                "&#91;视频&#93;你的QQ暂不支持查看视频短片，请升级到最新版本后查看。",
                                "",
                            )
                            if eachLine == "\n":
                                continue
                            chatlog += eachLine
        except:
            traceback.print_exc()
        return chatlog

    # 生成每日总结词云
    async def __generateWC(self):
        report = ""
        imginfo = []
        maskArray = self.__configuration["wcImg"]
        windowSize = self.__configuration["windowSize"]
        keyWordLen = self.__configuration["keyWordLen"]
        keyWordNum = self.__configuration["keyWordNum"]
        chatlog = self.__chatlog
        # 随机获取一张图片作为mask
        temp = []
        for i in range(len(maskArray)):
            temp.append(i)
        index = random.choice(temp)
        todayMask = maskArray[index]
        imageU = IMAGE_PATH / todayMask["fileName"]
        desc = todayMask["desc"]
        mask = np.array(Image.open(imageU))
        try:
            tr4w = TextRank4Keyword.TextRank4Keyword()
            tr4w.analyze(text=chatlog, lower=True, window=windowSize)
            wordDic = dict()
            for item in tr4w.get_keywords(keyWordNum, word_min_len=keyWordLen):
                wordDic[item.word] = item.weight
            wc = WordCloud(
                font_path=str(Path(__file__).parent / "SourceHanSans.otf"),
                mask=mask,
                background_color="white",
            )
            wc.generate_from_frequencies(wordDic)
            figName = (
                time.strftime("%Y-%m-%d%H-%M-%S", time.localtime())
                + "-"
                + str(round(random.uniform(0, 100)))
                + ".png"
            )
            wc.to_file(WC_PATH / figName)
            imginfo.append(
                MessageSegment.image(
                    f"base64://{b64encode(await IOUtils.local_to_bytes(WC_PATH / figName)).decode()}"
                )
            )
            imginfo.append(
                MessageSegment.image(
                    f"base64://{b64encode(await IOUtils.local_to_bytes(imageU)).decode()}"
                )
            )
            imginfo.append(desc)
            for i in range(3):
                report += "Top" + str(i + 1) + "：" + list(wordDic.keys())[i] + "\n"
            return report, imginfo
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            return None

    # 生成每日总结
    async def generateReport(self):
        report = ""
        templateList = self.__configuration["template"]
        for each in templateList:
            if each["groupId"] == self.__groupId:
                template1 = each["content"][0]
                template2 = each["content"][1]
                break
        tempReport = await self.__generateWC()
        if tempReport is None:
            for eachLine in template2.items():
                report += eachLine[1] + "\n"
            return report
        else:
            for eachLine in template1.items():
                tempStr = eachLine[1]
                if eachLine[0] == "time":
                    tempStr = tempStr.replace("{string}", self.__beginTime, 1)
                    tempStr = tempStr.replace("{string}", self.__endTime, 1)
                elif eachLine[0] == "content":
                    tempStr = tempStr.replace("{string}", tempReport[0])
                elif eachLine[0] == "wcImg":
                    tempStr = tempStr.replace("{img}", str(tempReport[1][0]))
                elif eachLine[0] == "wcImgDesc":
                    tempStr = tempStr.replace("{string}", tempReport[1][2])
                elif eachLine[0] == "oriImg":
                    tempStr = tempStr.replace("{img}", str(tempReport[1][1]))
                report += tempStr + "\n"
            return report
