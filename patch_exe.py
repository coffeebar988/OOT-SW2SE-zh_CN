#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把简体中文界面写进 OOT SW2SE 的 exe。

原理：exe 是 .NET 单文件，界面 HTML 以 gzip 形式作为清单资源嵌在 PE 里，
C# 侧只负责开窗、文件对话框与读写存档。因此本地化只需两件事：

1. 用等长的 gzip 流替换 editor.html.gz 资源（用 gzip 的 FEXTRA 字段把长度补齐，
   这样清单资源表的 offset/size 完全不用动）；
2. 把 #US 字符串堆里的对话框文案就地换成中文（不足处补 U+0000，长度不变）。

用法:
    python patch_exe.py <原 exe> <中文 html> <输出 exe>
"""

import struct
import sys
import zlib

# C# 侧对用户可见的文案：英文 -> 中文
CS_STRINGS = {
    "Offline save editor for the Nintendo Switch 2 remake": "任天堂 Switch 2 重制版离线存档编辑器",
    "A file dialog is already open.": "已有文件对话框处于打开状态。",
    "No folder containing progress.sav and caption.sav was found.":
        "未找到同时包含 progress.sav 与 caption.sav 的文件夹。",
    "The backup files exceed the expected size.": "备份文件超出了预期大小。",
    "A backup file was truncated while reading it.": "读取时备份文件被截断。",
    "The patch ZIP is empty or too large.": "补丁 ZIP 为空或过大。",
    "The editor did not create a valid patch ZIP.": "编辑器未能生成有效的补丁 ZIP。",
    "Invalid patch folder name.": "补丁文件夹名称无效。",
    "Invalid patch file list.": "补丁文件列表无效。",
    "Invalid patch file.": "补丁文件无效。",
    "The patch files are too large.": "补丁文件过大。",
    "The Microsoft Edge WebView2 Runtime is required to run this app.":
        "运行本程序需要 Microsoft Edge WebView2 运行时。",
    "The editor window could not start.\n\n": "编辑器窗口无法启动。\n\n",
    "The Microsoft WebView2 loader could not start.": "Microsoft WebView2 加载器无法启动。",
    "Save patch": "保存补丁",
    "ZIP archive (*.zip)|*.zip": "ZIP 压缩包 (*.zip)|*.zip",
    "Select a backup or save folder": "选择备份或存档文件夹",
    "Select where to create the patch folder": "选择补丁文件夹的创建位置",
    "Select Folder": "选择文件夹",
}


def build_gzip(raw, size, level=9):
    """生成恰好 size 字节的 gzip 流：多余的字节塞进 FEXTRA 字段。"""
    head = b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xff"
    comp = zlib.compressobj(level, zlib.DEFLATED, -15)
    body = comp.compress(raw) + comp.flush()
    tail = struct.pack("<II", zlib.crc32(raw) & 0xFFFFFFFF, len(raw) & 0xFFFFFFFF)
    fixed = len(head) + len(body) + len(tail)
    if size < fixed:
        raise SystemExit("压缩后仍比原资源大 %d 字节，需要进一步精简 HTML。" % (fixed - size))
    pad = size - fixed
    if pad:
        if pad < 2:
            raise SystemExit("FEXTRA 至少需要 2 字节，余量不足。")
        extra = b"\x00" * (pad - 2)
        head = b"\x1f\x8b\x08\x04\x00\x00\x00\x00\x02\xff" + struct.pack("<H", len(extra)) + extra
    return head + body + tail


def find_gzip_members(data):
    """返回文件中所有完整 gzip 成员的 (偏移, 长度, 解压内容)。"""
    members = []
    index = 0
    while True:
        index = data.find(b"\x1f\x8b\x08", index)
        if index < 0:
            return members
        try:
            probe = zlib.decompressobj(31)
            out = probe.decompress(data[index:])
            if probe.eof:
                members.append((index, len(data[index:]) - len(probe.unused_data), out))
        except zlib.error:
            pass
        index += 1


def patch_strings(blob, report):
    """把 #US 堆里的英文换成中文，用 U+0000 补齐，字节长度保持不变。"""
    for english, chinese in CS_STRINGS.items():
        needle = english.encode("utf-16-le")
        count = blob.count(needle)
        if count == 0:
            report.append(("MISS", english))
            continue
        if count > 1:
            report.append(("DUP%d" % count, english))
        room = len(english)
        if len(chinese) > room:
            report.append(("LONG", english))
            continue
        replacement = (chinese + "\x00" * (room - len(chinese))).encode("utf-16-le")
        assert len(replacement) == len(needle)
        blob = blob.replace(needle, replacement)
        report.append(("OK", english))
    return blob


def pe_checksum(blob, offset):
    """按 PE 规范重算校验和（仅当原文件带校验和时才写回）。"""
    data = bytearray(blob)
    data[offset:offset + 4] = b"\x00\x00\x00\x00"
    total = 0
    length = len(data)
    for i in range(0, length - 1, 2):
        total += data[i] | (data[i + 1] << 8)
        total = (total & 0xFFFF) + (total >> 16)
    if length % 2:
        total += data[-1]
        total = (total & 0xFFFF) + (total >> 16)
    total = (total & 0xFFFF) + (total >> 16)
    return (total + length) & 0xFFFFFFFF


def main():
    # 两参数模式：从 exe 里抽出内嵌的英文界面，便于重新翻译
    #   python patch_exe.py "OOT SW2SE.exe" embedded-en.html
    if len(sys.argv) == 3:
        original = open(sys.argv[1], "rb").read()
        for offset, length, content in find_gzip_members(original):
            if content.startswith(b"<!doctype html>") or b"OOT SW2SE" in content[:4096]:
                open(sys.argv[2], "wb").write(content)
                print("已抽出界面: 偏移 0x%X, gzip %d 字节, HTML %d 字节 -> %s"
                      % (offset, length, len(content), sys.argv[2]))
                return
        raise SystemExit("没有在 exe 里找到内嵌的 editor.html.gz")

    src, html_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    original = open(src, "rb").read()
    blob = bytearray(original)

    members = find_gzip_members(original)
    target = None
    for offset, length, content in members:
        if content.startswith(b"<!doctype html>") or b"OOT SW2SE" in content[:4096]:
            target = (offset, length, content)
            break
    if target is None:
        raise SystemExit("没有在 exe 里找到内嵌的 editor.html.gz")
    offset, length, old_html = target
    print("内嵌界面资源: 偏移 0x%X, gzip %d 字节, HTML %d 字节" % (offset, length, len(old_html)))

    new_html = open(html_path, "rb").read()
    packed = build_gzip(new_html, length)
    assert len(packed) == length, (len(packed), length)
    blob[offset:offset + length] = packed
    print("新界面资源: gzip %d 字节 (等长替换), HTML %d 字节" % (len(packed), len(new_html)))

    report = []
    blob = patch_strings(bytes(blob), report)
    for status, text in report:
        if status != "OK":
            print("  [%s] %s" % (status, text))
    print("对话框文案替换成功 %d 条" % sum(1 for s, _ in report if s == "OK"))

    # 校验和（若原文件写了非零校验和）
    e_lfanew = struct.unpack_from("<I", original, 0x3C)[0]
    opt = e_lfanew + 24
    magic = struct.unpack_from("<H", original, opt)[0]
    check_offset = opt + 64 if magic == 0x20B else opt + 64
    if struct.unpack_from("<I", original, check_offset)[0]:
        value = pe_checksum(bytes(blob), check_offset)
        struct.pack_into("<I", blob, check_offset, value)
        print("PE 校验和已更新: 0x%08X" % value)

    open(out, "wb").write(blob)
    print("已写出:", out, len(blob), "字节")


if __name__ == "__main__":
    main()
