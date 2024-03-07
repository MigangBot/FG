"""
@desc: FG定时发布每日总结
@author: Martin Huang
@time: created on 2020/4/4 16:22
@修改记录:
        2020/4/12 => 修改定时器模式
"""

import nonebot
from cn.acmsmu.FG import DailyConclusion
from Utils.JsonUtils import JsonUtils
from Utils.IOUtils import IOUtils
from .pathSetting import GROUP_DATA_PATH, CONFIG_FILE


async def handleTimer(groupId):
    dataDict = IOUtils.deserializeObjFromPkl(GROUP_DATA_PATH / groupId / "var.pkl")
    flag = dataDict["flag"]
    # print(timerName+'的每日总结为\n'+report)
    clu = DailyConclusion.DailyConlusion(groupId)
    report = await clu.generateReport()
    try:
        await bot.send_group_msg(group_id=int(groupId), message=report)
    finally:
        if flag:
            dataDict["flag"] = False
            dataDict["file"] = "chatB.txt"
            IOUtils.serializeObj2Pkl(dataDict, GROUP_DATA_PATH / groupId / "var.pkl")
            IOUtils.deleteFile(GROUP_DATA_PATH / groupId / "chatA.txt")
        else:
            dataDict["flag"] = True
            dataDict["file"] = "chatA.txt"
            IOUtils.serializeObj2Pkl(dataDict, GROUP_DATA_PATH / groupId / "var.pkl")
            IOUtils.deleteFile(GROUP_DATA_PATH / groupId / "chatB.txt")


bot = nonebot.get_bot()
configuration = JsonUtils.json2Dict(CONFIG_FILE)
print(configuration)
groupInfo = configuration["groupInfo"]
for each in groupInfo:
    hour = each["beginHour"]
    minutes = each["beginMinutes"]
    nonebot.scheduler.add_job(
        handleTimer,
        "cron",
        hour=hour,
        minute=minutes,
        args=[each["groupId"]],
    )
    print("定时器" + each["timer"] + "定时任务添加成功!")
