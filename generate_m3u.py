#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

EPG_FILE = "epg_data.json"
CHANNEL_FILE = "channels.txt"
OUTPUT_FILE = "live.m3u"

EPG_URL = "https://github.com/badboys88888/epg/raw/main/epg.xml.gz"

# ===================== 读取EPG ===================== #
def load_epg():
    with open(EPG_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    epg_map = {}

    for item in data.get("epgs", []):
        epgid = item.get("epgid", "").strip()
        logo = item.get("logo", "").strip()
        names = item.get("name", "")

        # 拆分别名
        alias_list = [n.strip() for n in names.split(",") if n.strip()]

        for name in alias_list:
            epg_map[name] = {
                "id": epgid,
                "logo": logo
            }

    return epg_map


# ===================== 匹配频道 ===================== #
def match_epg(channel_name, epg_map):
    # 精确匹配
    if channel_name in epg_map:
        return epg_map[channel_name]

    # 模糊匹配（包含关系）
    for name in epg_map:
        if name in channel_name or channel_name in name:
            return epg_map[name]

    return {"id": "", "logo": ""}


# ===================== 生成M3U ===================== #
def generate_m3u():
    epg_map = load_epg()

    with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(f'#EXTM3U x-tvg-url="{EPG_URL}"\n')

        group = ""

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # 分组
            if line.startswith("#genre#"):
                group = line.replace("#genre#", "").strip()
                continue

            if "," not in line:
                continue

            name, url = line.split(",", 1)
            name = name.strip()
            url = url.strip()

            epg = match_epg(name, epg_map)

            tvg_id = epg["id"]
            tvg_logo = epg["logo"]

            out.write(
                f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-name="{name}" tvg-logo="{tvg_logo}" group-title="{group}",{name}\n'
            )
            out.write(f"{url}\n")

    print("✅ 已生成 live.m3u")


if __name__ == "__main__":
    generate_m3u()
