"""镜头表模板：复制本目录为 topics/<slug>/ 后，按提示词的分镜逐镜填写。

- text：主字幕原文照录，用“／”分行；每屏最多两行，单行尽量不超过 12 个汉字。
- tag：固定角标，只用“情境演绎 / 研究示意 / 机制示意 / 反思练习 / 生活提示 / 参考资料”。
- cues：候选音画事件。音色键见 kepu.config.SOUNDS；snap=False 为移动类柔和动作；音色为空串表示无新增音效。
- extra：研究段、陌生术语另加阅读余量（秒）；含数字时引擎自动另加 0.8 秒。
- credit=True：片尾来源卡，首个事件为来源卡落定，window 限定在镜头开头 0.45 秒内。
- 镜头基准时长默认 6 秒，总长 = 镜头数 × 6；需要别的时长时在下面的循环里改 start。
"""

from kepu.config import Cue, Shot


def shots() -> list[Shot]:
    s = [
        Shot(1, "示例问题，／第二行字幕？", "情境演绎",
             [Cue("hit", 1.2, "kick", "核心物体出现并撞击落定")]),
        Shot(2, "示例机制：／围着同一件事打转。", "机制示意",
             [Cue("lap", 1.6, "tom", "卡片完成第一圈"),
              Cue("move", 3.0, "shaker", "卡片继续移动", 0.7, snap=False)]),
        Shot(3, "参考：年份／《文献中文题名》", "参考资料",
             [Cue("credit", 0.4, "cymbal", "来源卡落定", 0.8, window=(-0.02, 0.45))], extra=1.0, credit=True),
    ]
    for i, sh in enumerate(s):
        sh.start = i * 6.0
    return s
