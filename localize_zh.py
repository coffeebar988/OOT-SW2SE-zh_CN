#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OOT SW2SE 简体中文本地化：把 editor.html 翻成中文。

用法:
    python localize_zh.py <源 editor.html> <输出 editor.zh-CN.html>
"""

import json
import re
import sys

# ---------------------------------------------------------------------------
# 1) 整句 / 整段：HTML 文本节点（>文本< 形式）
# ---------------------------------------------------------------------------
HTML_TEXT = [
    ("Requires <code>progress.sav</code> and <code>caption.sav</code>.",
     "需要 <code>progress.sav</code> 与 <code>caption.sav</code>。"),
    ("Open an extracted backup or an individual save folder.",
     "打开已解压的备份文件夹，或单个存档文件夹。"),
    ("Open Backup", "打开备份"),
    ("Save Slot", "存档槽位"),
    ("Switching slots resets unsaved edits.", "切换槽位会丢弃未保存的修改。"),
    ("Overview", "总览"),
    ("Stats", "属性"),
    ("Inventory", "物品栏"),
    ("Progress", "进度"),
    ("Export", "导出"),
    ("Edit Save", "编辑存档"),
    ("Hearts and Magic", "生命与魔法"),
    ("Max Hearts", "最大心数"),
    ("Current Hearts", "当前心数"),
    ("Magic Meter", "魔法槽"),
    ("Current Magic Points", "当前魔法值"),
    ("Refill Magic", "补满魔法"),
    ("This save contains magic values from an older editor version. Exporting converts them to the units used by the remake.",
     "此存档中的魔法值来自旧版编辑器，导出时会转换为重制版使用的单位。"),
    ("Set current health in quarter-heart steps. Upgrading the magic meter also adds the corresponding Great Fairy blessings.",
     "以四分之一心为单位设置当前生命值。升级魔法槽会同时获得对应的大妖精祝福。"),
    ("Swim Depth", "游泳深度"),
    ("How deep Link can swim (m)", "林克可下潜的深度（米）"),
    ("The game keeps this as one float: a save with the Silver Scale reads 6, one with the Gold Scale reads 9. The scale in the pouch is the item that normally sets it, so raising the number alone raises the limit.",
     "游戏内以单个浮点数保存此值：持有银鳞片的存档显示为 6，持有金鳞片显示为 9。背包中的鳞片是通常设定该值的道具，因此只提高数值也能提高上限。"),
    ("Rupees", "卢比"),
    ("Wallet", "钱包"),
    ("Bags and Quivers", "袋子与箭袋"),
    ("Unlock capacity upgrades directly, or select a smaller Seed Bag you already own. Quantities must fit the selected capacity.",
     "可直接解锁容量升级，也可选择你已拥有的更小种子袋。数量不得超过所选容量。"),
    ("Inventory Quantities", "物品数量"),
    ("Bottles", "瓶子"),
    ("Bottle Count", "瓶子数量"),
    ("New bottles are empty. Reducing the count removes the last occupied slots and their contents.",
     "新增的瓶子为空瓶。减少数量会移除最后占用的槽位及其内容。"),
    ("Small Keys by Area", "各区域小钥匙"),
    ("Edit the number of keys you carry. Doors, chests, and pickups have separate states.",
     "编辑携带的钥匙数量。门、宝箱与拾取物分别有独立状态。"),
    ("Voice Language", "语音语言"),
    ("Spoken Dialogue Language", "对话语音语言"),
    ("Check Add or Remove to change inventory. Removing an item keeps its acquisition history unless you also check Clear acquisition flags. This clears the catalog's mapped acquisition flags, not story events or quest progress. Equipped weapons and shields must be unequipped in both eras first. Default clothes cannot be removed here.",
     "勾选「添加」或「移除」来修改物品栏。移除物品会保留其获取记录，除非同时勾选「清除获取标志」。这里清除的是目录中映射的获取标志，不涉及剧情事件或任务进度。已装备的武器与盾牌需先在两个时代都卸下。默认服装无法在此移除。"),
    ("Progress Flags", "进度标志"),
    ("Check a box to set its flag to true. Some quests and cutscenes depend on multiple flags and items. Editing one flag changes only that value.",
     "勾选复选框可把该标志设为 true。部分任务与过场动画依赖多个标志和物品，修改单个标志只会改变该值。"),
    ("Save Patch", "保存补丁"),
    ("Save Back", "写回源文件"),
    ("Save Patch ZIP", "导出补丁 ZIP"),
    ("Export to Folder", "导出到文件夹"),
    ("Reset All Edits", "重置全部修改"),
    ("Field Inspector · Read-only", "字段查看器 · 只读"),
    ("Field names come from the Switch 2 remake. Unidentified fields appear with their hash and type. Arrays show the first eight values.",
     "字段名来自 Switch 2 重制版。未识别的字段以其哈希与类型显示。数组只显示前八个值。"),
    ("Named fields only", "仅显示已命名字段"),
    # 表头
    ("Item", "物品"),
    ("Category", "分类"),
    ("In Save", "存档中"),
    ("Add", "添加"),
    ("Remove", "移除"),
    ("Clear acquisition flags", "清除获取标志"),
    ("Flag", "标志"),
    ("Hash", "哈希"),
    ("In Patch", "补丁中"),
    ("Field", "字段"),
    ("Type", "类型"),
    ("Value", "值"),
    ("Previous", "上一页"),
    ("Next", "下一页"),
]

# ---------------------------------------------------------------------------
# 2) 引号内的字符串（属性值 / JS 字符串 / JSON 值）
# ---------------------------------------------------------------------------
QUOTED = [
    # 属性
    ("Editor sections", "编辑器分区"),
    ("Save preview", "存档预览"),
    ("Search inventory", "搜索物品"),
    ("Filter inventory", "筛选物品栏"),
    ("Search progress flags", "搜索进度标志"),
    ("Progress flag category", "进度标志分类"),
    ("Progress flag status", "进度标志状态"),
    ("Name or hash", "名称或哈希"),
    ("Name, hash, or type", "名称、哈希或类型"),
    ("Search fields", "搜索字段"),
    # 下拉选项
    ("Missing items you can add", "可添加的未拥有物品"),
    ("Already owned", "已拥有"),
    ("All readable entries", "全部可读取条目"),
    ("Masks", "面具"),
    ("Pending inventory changes", "待应用的物品改动"),
    ("All categories", "全部分类"),
    ("Events and cutscenes", "事件与过场动画"),
    ("Dialogue and Navi hints", "对话与娜薇提示"),
    ("Quests and other flags", "任务与其他标志"),
    ("All states", "全部状态"),
    ("Set in save", "存档中已置位"),
    ("Unset in save", "存档中未置位"),
    ("Changed", "已修改"),
    ("The two amiibo masks share one equipment tile. The other eight masks share a second tile.",
     "两个 amiibo 面具共用同一个装备格，其余八个面具共用第二个装备格。"),
    # 钱包 / 容量 / 素材
    ("Kokiri Wallet", "科奇里钱包"),
    ("Adult's Wallet", "成年钱包"),
    ("Giant's Wallet", "巨人钱包"),
    ("Deku Seed Bag", "德库种子袋"),
    ("Deku Nut Bag", "德库坚果袋"),
    ("Deku Stick Bag", "德库棒袋"),
    ("Bomb Bag", "炸弹袋"),
    ("Quiver", "箭袋"),
    ("Deku Seeds", "德库种子"),
    ("Deku Nuts", "德库坚果"),
    ("Deku Sticks", "德库棒"),
    ("Arrows", "箭"),
    ("Bombs", "炸弹"),
    ("Bombchus", "炸弹鼠"),
    ("Magic Beans", "魔法豆"),
    ("Business Scrub Seeds", "德库商人种子"),
    ("Gold Skulltula Tokens", "金色骷髅蜘蛛徽记"),
    ("Pieces of Heart", "心之碎片"),
    # 小钥匙区域
    ("Bottom of the Well", "井底"),
    ("Forest Temple", "森林神殿"),
    ("Fire Temple", "火之神殿"),
    ("Water Temple", "水之神殿"),
    ("Shadow Temple", "暗之神殿"),
    ("Spirit Temple", "魂之神殿"),
    ("Gerudo Fortress", "格鲁德要塞"),
    ("Gerudo Proving Grounds", "格鲁德训练场"),
    ("Ganondorf's Castle", "加侬多夫城堡"),
    # 瓶内物品
    ("empty", "空"),
    ("red potion", "红色药水"),
    ("green potion", "绿色药水"),
    ("blue potion", "蓝色药水"),
    ("blue fire", "蓝色火焰"),
    ("fish", "鱼"),
    ("letter", "信"),
    ("Big Poe", "大波"),
    ("Poe", "波"),
    ("bug", "虫子"),
    ("fairy", "妖精"),
    ("milk", "牛奶"),
    ("half milk", "半瓶牛奶"),
    # 魔法槽等级
    ("No Magic Meter", "无魔法槽"),
    ("Standard Magic Meter · 24 MP", "标准魔法槽 · 24 点"),
    ("Double Magic Meter · 48 MP", "双倍魔法槽 · 48 点"),
    # 语音语言
    ("Japanese", "日语"),
    ("English", "英语"),
    ("French (France)", "法语（法国）"),
    ("French (Canada)", "法语（加拿大）"),
    ("German", "德语"),
    ("Spanish (Spain)", "西班牙语（西班牙）"),
    ("Spanish (Latin America)", "西班牙语（拉丁美洲）"),
    ("Italian", "意大利语"),
    ("Portuguese (Brazil)", "葡萄牙语（巴西）"),
    # 存档时间
    ("autosave", "自动存档"),
    ("manual save", "手动存档"),
    # 概览字段
    ("Slot", "槽位"),
    ("Saved", "存档时间"),
    ("Area", "区域"),
    ("Progress ID", "进度 ID"),
    ("Hearts", "心数"),
    ("Magic", "魔法"),
    ("Gold Skulltulas", "金色骷髅蜘蛛"),
    ("Equipped", "已装备"),
    ("Position X / Y / Z", "坐标 X / Y / Z"),
    # 按钮 / 提示
    ("Remove this item from inventory", "从物品栏移除此物品"),
    ("Select Remove first. Clears mapped acquisition flags; quest progress stays unchanged.",
     "请先勾选「移除」。将清除映射的获取标志；任务进度不受影响。"),
    ("No matches", "无匹配结果"),
    ("0 flags", "0 个标志"),
    ("0 matches", "0 个匹配"),
    (" — add", " — 添加"),
    (" — remove", " — 移除"),
    (" — clear acquisition flags", " — 清除获取标志"),
    (" · newest", " · 最新"),
    (" · active", " · 当前"),
    (" · owned", " · 已拥有"),
    ("Slot ", "槽位 "),
    # ---- 错误与状态消息 ----
    ("This file does not match the supported Switch 2 save format.", "此文件与受支持的 Switch 2 存档格式不符。"),
    ("Duplicate field hash: ", "字段哈希重复："),
    ("Required field missing: ", "缺少必需字段："),
    ("Invalid data offset: ", "数据偏移无效："),
    ("The wallet, ownership flag, and rupee limit are inconsistent.", "钱包、拥有标志与卢比上限不一致。"),
    ("Unexpected rupee count in progress.sav.", "progress.sav 中的卢比数量异常。"),
    ("Unexpected inventory quantity in the save.", "存档中的物品数量异常。"),
    ("Unknown voice language value.", "未知的语音语言值。"),
    ("Unknown voice language.", "未知的语音语言。"),
    ("Unknown wallet.", "未知的钱包。"),
    ("Max hearts must be between 3 and 20.", "最大心数必须介于 3 与 20 之间。"),
    ("Current hearts must be between 0 and the maximum, in quarter-heart steps.",
     "当前心数必须介于 0 与最大值之间，且以四分之一心为单位。"),
    ("Select the current magic meter or an upgrade.", "请选择当前魔法槽或更高的升级。"),
    ("Magic points must be between 0 and ", "魔法值必须介于 0 与 "),
    (", in tenths.", " 之间，以十分之一为单位。"),
    ("Swim depth must be between 0 and 40 metres.", "游泳深度必须介于 0 与 40 米之间。"),
    ("This item cannot be added here: ", "此处无法添加该物品："),
    ("This flag cannot be edited here: ", "此处无法编辑该标志："),
    ("Only supported, owned single items can be removed here.", "此处只能移除受支持且已拥有的单个物品。"),
    ("The equipment fields could not be checked.", "无法检查装备字段。"),
    ("Unequip this item in both eras before removing it.", "移除前请先在两个时代都卸下此物品。"),
    ("An item cannot be added and removed in the same patch.", "同一补丁中不能同时添加与移除同一物品。"),
    ("Clearing acquisition flags requires removing the item.", "清除获取标志需要先移除该物品。"),
    ("A Progress flag conflicts with clearing acquisition flags: ", "进度标志与清除获取标志冲突："),
    ("An acquisition flag is shared with an item still in inventory: ", "某个获取标志与仍在物品栏中的物品共用："),
    ("The acquisition flags cannot be safely edited for ", "无法安全编辑该物品的获取标志："),
    ("The item and its acquisition flag conflict: ", "物品与其获取标志冲突："),
    ("The bottle ownership fields are inconsistent.", "瓶子拥有字段不一致。"),
    ("Invalid capacity tier for ", "容量等级无效："),
    ("SHA-256 is required to update the backup manifest.", "更新备份清单需要 SHA-256 支持。"),
    ("The manifest does not belong to a supported Ocarina of Time backup.",
     "该清单不属于受支持的《时之笛》备份。"),
    ("The manifest does not match ", "清单与以下文件不匹配："),
    ("No folder containing progress.sav and caption.sav was found.",
     "未找到同时包含 progress.sav 与 caption.sav 的文件夹。"),
    ("Select a single backup folder.", "请选择单个备份文件夹。"),
    ("No opened file to replace with ", "没有可替换的已打开文件："),
    ("The file could not be read.", "无法读取该文件。"),
    ("The manifest could not be read.", "无法读取清单文件。"),
    ("Open a backup containing option.sav to edit the voice language.",
     "打开包含 option.sav 的备份才能修改语音语言。"),
    ("Applies to the entire game profile. The patch includes option.sav when you select a different language.",
     "应用于整个游戏配置。选择不同语言时，补丁会包含 option.sav。"),
    ("Could not open option.sav. ", "无法打开 option.sav。"),
    ("The backup manifest could not be updated. Nothing was saved.",
     "无法更新备份清单，未写入任何内容。"),
    ("Save canceled.", "已取消保存。"),
    ("Backup manifest verified.", "备份清单校验通过。"),
    ("The manifest does not match this slot. The patch will contain the replacement files.",
     "清单与此槽位不匹配，补丁将包含替换文件。"),
    ("Exporting synchronizes the preview rupee count.", "导出时会同步预览中的卢比数量。"),
    ("Patch for ", "已保存 "),
    (" saved.", " 的补丁。"),
    (" loaded.", " 已载入。"),
    ("Loading ", "正在载入 "),
    ("Manifest skipped. ", "已跳过清单。"),
    ("Copy the files inside the UTC timestamp folder into a copy of your save folder. Exports contain replacement files, not a full backup.",
     "把 UTC 时间戳文件夹内的文件复制到你存档文件夹的副本中。导出内容是替换文件，不是完整备份。"),
    ("Copy the contents of the UTC timestamp folder into the files folder of a copy of your full backup. Copy manifest.json to the backup root when included. Exports contain replacement files, not a full backup.",
     "把 UTC 时间戳文件夹内的内容复制到你完整备份副本的 files 文件夹中。若包含 manifest.json，请一并复制到备份根目录。导出内容是替换文件，不是完整备份。"),
    (" Save Back writes the edits straight into the opened files. The files it replaces are first kept as a ZIP",
     " 「写回源文件」会把修改直接写入已打开的文件，被替换的文件会先保存为 ZIP"),
    ("Saved ", "已将 "),
    (" back to the opened files. The previous files are kept in ", " 写回已打开的文件。原文件保存在 "),
    ("Saved capacity: ", "存档容量："),
    (" · editor limit: ", " · 编辑器上限："),
    ("Up to ", "上限 "),
    ("Capacity changes in this patch: ", "本次补丁的容量变更："),
    (" to add · ", " 个待添加 · "),
    (" to remove · ", " 个待移除 · "),
    (" acquisition resets · ", " 项获取标志重置 · "),
    (" flag changes", " 项标志修改"),
    ("Limit · ", "上限 · "),
    (" rupees.", " 卢比。"),
    ("Automatic · saved capacity: ", "自动 · 存档容量："),
    ("In save: 0 bottles", "存档中：0 个瓶子"),
    ("In save: ", "存档中："),
    (" item entries are missing acquisition flags. Exporting adds the missing flags.",
     " 个物品条目缺少获取标志，导出时会自动补上。"),
    (" of ", " 项，共 "),
    (" flags", " 个标志"),
    (" matches", " 个匹配"),
    (" bytes at ", " 字节，位于 "),
    ("Block at ", "数据块位于 "),
    ("Invalid data offset ", "数据偏移无效 "),
    ("Set", "已置位"),
    ("Unset", "未置位"),
]

# ---------------------------------------------------------------------------
# 2b) 整表达式：拼接顺序需要调整、或结尾标点需要改写的地方
# ---------------------------------------------------------------------------
EXPR = [
    # 容量下拉：["Small","Medium","Large"] 同时用于生成内部 actor 名，只能改显示处
    ('new Option(["Small", "Medium", "Large"][i] + \' · \' + limit + status, String(limit))',
     'new Option(["小", "中", "大"][i] + \' · \' + limit + status, String(limit))'),
    # 数值范围校验
    ('label + " must be between 0 and " + max + "."',
     'label + " 必须介于 0 与 " + max + " 之间。"'),
    # 清单 / 文件路径结尾的英文句号
    ('"The manifest does not match " + path + \'.\'',
     '"清单与以下文件不匹配：" + path'),
    ('"No opened file to replace with " + path + \'.\'',
     '"没有可替换的已打开文件：" + path'),
    ('\'Invalid capacity tier for \' + group.label + \'.\'',
     '\'容量等级无效：\' + group.label'),
    ('group.label + " to " + limit', 'group.label + " → " + limit'),
    ('(desktop.features.saveBack.backupFolder ? " in " + desktop.features.saveBack.backupFolder : \'\') + "."',
     '(desktop.features.saveBack.backupFolder ? "（位于 " + desktop.features.saveBack.backupFolder + "）" : \'\') + "。"'),
    ('"Saved " + active.id + " back to the opened files. The previous files are kept in " +\n          saved.backup + \'.\'',
     '"已将 " + active.id + " 写回已打开的文件。原文件保存在 " + saved.backup + "。"'),
]

# ---------------------------------------------------------------------------
# 3) 物品目录：标题与分类（只在 catalog JSON 内替换）
# ---------------------------------------------------------------------------
ITEM_TITLES = {
    "Arrow": "箭", "Biggoron Sword": "大哥隆之剑", "Broken Giant's Knife": "断裂的巨人小刀",
    "Bunny Hood": "兔子头巾", "Deku Seed": "德库种子", "Deku Shield": "德库盾",
    "Echo Gem": "回响宝石", "Fairy Bow": "妖精之弓", "Fairy Slingshot": "妖精弹弓",
    "Fairy-Kid Mask": "妖精小孩面具", "Gerudo Mask": "格鲁德面具", "Giant's Knife": "巨人小刀",
    "Goron Mask": "哥隆面具", "Goron Tunic": "哥隆服", "Hero's Clothes": "勇者之服",
    "Hover Boots": "浮空靴", "Hylian Shield": "海利亚盾", "Iron Boots": "铁靴",
    "Keaton Mask": "基顿面具", "Kokiri Sword": "科奇里之剑", "Kokiri Tunic": "科奇里服",
    "Lenses of Truth": "真实之镜", "Mask of Truth": "真实面具", "Master Sword": "大师之剑",
    "Mirror Shield": "镜盾", "Princess Mask": "公主面具", "Skull Mask": "骷髅面具",
    "Spooky Mask": "恐怖面具", "Zora Mask": "佐拉面具", "Zora Tunic": "佐拉服",
    "Biggoron Receipt": "大哥隆收据", "Bomb": "炸弹", "Bombchu": "炸弹鼠",
    "Boomerang": "回旋镖", "Bow + Fire Arrow": "弓 + 火焰箭", "Bow + Ice Arrow": "弓 + 冰箭",
    "Bow + Light Arrow": "弓 + 光箭", "Broken Goron Sword": "断裂的哥隆剑",
    "Business Scrub Seed": "德库商人种子", "Cojiro": "科吉罗", "Deku Nut": "德库坚果",
    "Deku Stick": "德库棒", "Din's Fire": "丁之火", "Eyeball Frog": "眼珠蛙",
    "Farore's Wind": "法罗之风", "Fire Arrow": "火焰箭", "Hookshot": "钩索",
    "Ice Arrow": "冰箭", "Light Arrow": "光箭", "Longshot": "长钩索",
    "Megaton Hammer": "巨型锤", "Nayru's Love": "奈露之爱", "Odd Mushroom": "奇异蘑菇",
    "Odd Poultice": "奇异药膏", "Poacher's Saw": "盗猎者之锯", "Pocket Cucco": "口袋咕咕鸡",
    "Pocket Egg": "口袋蛋", "Prescription": "处方", "Specialty Eye Drops": "特制眼药水",
    "Wake-Up Cucco": "唤醒咕咕鸡", "Weird Egg": "奇怪蛋", "Zelda's Letter": "塞尔达的信",
    "amiibo": "amiibo",
    "Bigger Bomb Bag": "大炸弹袋", "Bigger Deku-Nut Bag": "大德库坚果袋",
    "Bigger Deku-Seed Bag": "大德库种子袋", "Bigger Deku-Stick Bag": "大德库棒袋",
    "Bigger Quiver": "大箭袋", "Biggest Bomb Bag": "最大炸弹袋",
    "Biggest Deku-Nut Bag": "最大德库坚果袋", "Biggest Deku-Seed Bag": "最大德库种子袋",
    "Biggest Deku-Stick Bag": "最大德库棒袋", "Biggest Quiver": "最大箭袋",
    "Deku-Nut Bag": "德库坚果袋", "Deku-Seed Bag": "德库种子袋", "Deku-Stick Bag": "德库棒袋",
    "Fairy Ocarina": "妖精陶笛", "Fire Medallion": "火之徽章", "Forest Medallion": "森之徽章",
    "Gerudo Pass": "格鲁德通行证", "Gift of Doubled Magic": "双倍魔法之赐",
    "Gift of Halved Damage": "减半伤害之赐", "Gift of Improved Spin": "强化回旋斩之赐",
    "Golden Gauntlets": "黄金护手", "Golden Scale": "金鳞片", "Goron Bracelet": "哥隆手镯",
    "Goron Ruby": "哥隆红宝石", "Kokiri Emerald": "科奇里绿宝石",
    "Light Medallion": "光之徽章", "Ocarina of Time": "时之笛", "Piece of Heart": "心之碎片",
    "Shadow Medallion": "暗之徽章", "Silver Gauntlets": "银色护手", "Silver Scale": "银鳞片",
    "Spirit Medallion": "魂之徽章", "Token": "骷髅蜘蛛徽记", "Water Medallion": "水之徽章",
    "Zora Sapphire": "佐拉蓝宝石",
}

ITEM_CATEGORIES = {"KeyItem": "关键物品", "Equipment": "装备", "Item": "道具"}


def localize_catalog(html):
    """把 <script id="catalog"> 内的物品标题与分类翻成中文。"""
    pattern = re.compile(r'(<script id="catalog" type="application/json">)(.*?)(</script>)', re.S)
    match = pattern.search(html)
    if not match:
        raise SystemExit("找不到 catalog JSON")
    catalog = json.loads(match.group(2))
    titles = dict(QUOTED)
    titles.update(ITEM_TITLES)
    missing = []
    for row in catalog["inventory"]:
        title, category = row[4], row[2]
        if title and title not in titles:
            missing.append(title)
        if title:
            row[4] = titles[title]
        row[2] = ITEM_CATEGORIES.get(category, category)
    if missing:
        print("  [警告] 未翻译的物品名:", sorted(set(missing)))
    body = json.dumps(catalog, ensure_ascii=False, separators=(",", ":"))
    return html[:match.start(2)] + body + html[match.end(2):]


def apply(html, stats):
    # 整表达式优先（含引号与标点的长片段）
    for en, zh in EXPR:
        count = html.count(en)
        if count:
            html = html.replace(en, zh)
        stats[en] = stats.get(en, 0) + count

    # 整句与词条：同一词条可能出现在文本节点（>文本<）或字符串字面量（"文本" / '文本'）中，
    # 长串优先，避免短串先吃掉长串。
    pairs = sorted(HTML_TEXT + QUOTED, key=lambda kv: -len(kv[0]))
    for en, zh in pairs:
        total = 0
        for lead in ("", " "):
            for left, right in (('"', '"'), ("'", "'"), (">", "<")):
                needle = left + lead + en + right
                count = html.count(needle)
                if count:
                    html = html.replace(needle, left + lead + zh + right)
                    total += count
        stats[en] = stats.get(en, 0) + total
    return html


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "editor.html"
    out = sys.argv[2] if len(sys.argv) > 2 else "editor.zh-CN.html"
    with open(src, encoding="utf-8") as handle:
        html = handle.read()

    html = html.replace('<html lang="en"', '<html lang="zh-CN"')
    html = localize_catalog(html)

    # 中文字体栈
    html = html.replace(
        'font-family: "Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif;',
        'font-family: "Segoe UI Variable Text", "Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei", system-ui, sans-serif;')

    stats = {}
    html = apply(html, stats)

    # 压掉行首缩进与空行：中文比英文占字节，靠这点余量让 gzip 后不超过原资源长度。
    # 换行全部保留，因此 JS 的自动分号插入语义不变。
    lines = [line.lstrip(" \t") for line in html.split("\n")]
    html = "\n".join(line for line in lines if line.strip())

    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(html)

    unused = [en for en, _ in HTML_TEXT + QUOTED if not stats.get(en)]
    print("已写入:", out, len(html.encode("utf-8")), "字节")
    if unused:
        print("[未命中] 以下条目在源文件中未出现：")
        for en in unused:
            print("   -", en[:90])


if __name__ == "__main__":
    main()
