'''
@desc: FG主入口
@author: Martin Huang
@time: created on 2020/4/4 14:57
@修改记录:
'''
import os
import nonebot

if __name__ == '__main__':
    nonebot.init()
    nonebot.load_plugins(
        os.path.join(os.path.dirname(__file__), 'cn', 'acmsmu'),
        'cn.acmsmu'
    )
    nonebot.run(host="0.0.0.0", port=1206)