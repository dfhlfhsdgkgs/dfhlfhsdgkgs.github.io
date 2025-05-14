# -*- coding: utf-8 -*-
import requests
import json

# DOI 列表
# -*- coding: utf-8 -*-
# 10 篇文献的 DOI 列表
dois = [
    "10.1109/MI-STA52233.2021.9464433",
    "10.1109/SERA.2016.7516136",
    "10.1016/j.procs.2018.04.010",
    "10.1109/REW61692.2024.00044",
    "10.1023/a:1022916028950",
    "10.1002/spe.2384",
    "10.2495/DATA020321",
    "10.1142/S0218213018500276",
    "10.1145/2699697",
]


entries = {}
for doi in dois:
    try:
        # 调用 Crossref API 获取元数据
        resp = requests.get(f"https://api.crossref.org/works/{doi}", timeout=10).json().get("message", {})

        # 提取年份（优先 published-print，其次 published-online）
        date = resp.get("published-print", resp.get("published-online", {}))
        year = date.get("date-parts", [[None]])[0][0] or ""

        # 键名：第一作者姓氏 + 年份
        first_author = resp.get("author", [{}])[0].get("family", "")
        key = f"{first_author}{year}"

        # 构造完整条目，保证每个字段都有
        entries[key] = {
            "abstract":  resp.get("abstract", ""),
            "author":    " and ".join(f"{a.get('family','')}, {a.get('given','')}" for a in resp.get("author", [])),
            "doi":       doi,
            "journal":   resp.get("container-title", [""])[0],
            "keywords":  ", ".join(resp.get("subject", [])),
            "number":    resp.get("issue", ""),
            "publisher": resp.get("publisher", ""),
            "series":    resp.get("series", [""])[0] if resp.get("series") else "",
            "title":     resp.get("title", [""])[0],
            "type":      resp.get("type", ""),
            "url":       resp.get("URL", ""),
            "volume":    resp.get("volume", ""),
            "year":      str(year),
        }
    except Exception as e:
        print(f"Error processing {doi}: {e}")

# 指定输出属性顺序
fields_order = [
    "abstract", "author", "doi", "journal", "keywords",
    "number", "publisher", "series", "title", "type",
    "url", "volume", "year"
]

# 重建字典以保持顺序
ordered_entries = {}
for k, v in entries.items():
    ordered_entries[k] = {f: v.get(f, "") for f in fields_order}

# 写入 JS 文件
with open("generatedBibEntries.js", "w", encoding="utf-8") as f:
    f.write("const generatedBibEntries = ")
    json.dump(ordered_entries, f, ensure_ascii=False, indent=2)
    f.write(";")
