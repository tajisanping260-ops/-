# -*- coding: utf-8 -*-
"""
cafeteria_cli.py
学食メニューCSV（niigata_univ_dai1_shokudo_nutrition.csv）を読み込み、
検索/表示/合計/複数品合計(sumx)を行う 1 ファイル完結のCLI。

使い方例:
  python3 cafeteria_cli.py stats
  python3 cafeteria_cli.py search ラーメン -n 5
  python3 cafeteria_cli.py show "カレー中"
  python3 cafeteria_cli.py sum カレー
  python3 cafeteria_cli.py sumx "カレー中" "豚汁"
  python3 cafeteria_cli.py sumx カレー 豚汁 --contains

前提:
  このスクリプトと同じフォルダに
  niigata_univ_dai1_shokudo_nutrition.csv があること。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import argparse
import csv
import math
import re
import sys
from typing import Dict, Iterable, List, Optional

# ---- 設定 ----
CSV_PATH = Path(__file__).with_name("niigata_univ_dai1_shokudo_nutrition.csv")

# 列名の正規化（表記ゆれ対応）
_COLMAP = {
    r"^name$|^メニュー名$|^商品名$": "name",
    r"^price$|^価格$|^値段$": "price_raw",
    r"^url$|^リンク$": "url",

    r"^energy.*kcal$|^k?cal$|^エネルギ.*|^カロリー$": "energy_kcal",
    r"^protein.*g$|^たんぱく.*|^蛋白.*": "protein_g",
    r"^fat.*g$|^脂質$|^脂肪$": "fat_g",
    r"^carb.*g$|^炭水化物$|^糖質$": "carbs_g",
    r"^salt.*g$|^食塩.*|^塩分$": "salt_g",

    r"^calcium.*mg$|^カルシウム$": "calcium_mg",
    r"^vegetables.*g$|^野菜量?$": "vegetables_g",
    r"^iron.*mg$|^鉄$": "iron_mg",
    r"^vitaminA.*(ug|μg).*|^ビタミン\s*A$": "vitaminA_ugRAE",
    r"^vitaminB1.*mg$|^ビタミン\s*B1$": "vitaminB1_mg",
    r"^vitaminB2.*mg$|^ビタミン\s*B2$": "vitaminB2_mg",
    r"^vitaminC.*mg$|^ビタミン\s*C$": "vitaminC_mg",
}

_NUTRIENT_KEYS = [
    "energy_kcal", "protein_g", "fat_g", "carbs_g", "salt_g",
    "calcium_mg", "vegetables_g", "iron_mg",
    "vitaminA_ugRAE", "vitaminB1_mg", "vitaminB2_mg", "vitaminC_mg",
]

# ---- ヘルパ ----
def _normalize_header(h: str) -> str:
    h = (h or "").strip()
    for pat, key in _COLMAP.items():
        if re.search(pat, h, flags=re.I):
            return key
    return h

def _to_float(x: str) -> Optional[float]:
    if x is None:
        return None
    t = str(x).replace("－", "-")
    m = re.search(r"-?\d+(?:\.\d+)?", t)
    return float(m.group(0)) if m else None

def _yen_to_int(x: str) -> Optional[int]:
    if not x:
        return None
    m = re.search(r"(\d{1,7})", str(x))
    return int(m.group(1)) if m else None

def fmt_price(yen):
    return f"¥{yen}" if isinstance(yen, int) else "-"

def fmt_num(x):
    return "-" if x is None else (str(int(x)) if float(x).is_integer() else f"{x}")

# ---- データ構造 ----
@dataclass
class Dish:
    name: str
    price_yen: Optional[int] = None
    url: str = ""
    nutrients: Dict[str, Optional[float]] = field(default_factory=dict)

    def get(self, key: str) -> Optional[float]:
        return self.nutrients.get(key)

# ---- ローダ ----
def load_menu(csv_path: str | Path) -> List[Dish]:
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {p}")

    dishes: List[Dish] = []
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header_map = {k: _normalize_header(k) for k in (reader.fieldnames or [])}

        for row in reader:
            norm = {header_map.get(k, k): (row.get(k) if row is not None else None) for k in row.keys()}
            name = (norm.get("name") or "").strip()
            if not name:
                continue

            price_yen = _yen_to_int(norm.get("price_raw", "")) if "price_raw" in norm else _yen_to_int(norm.get("price", ""))
            url = (norm.get("url") or "").strip()

            nutrients: Dict[str, Optional[float]] = {}
            for key in _NUTRIENT_KEYS:
                if key in norm and norm[key] not in (None, ""):
                    nutrients[key] = _to_float(norm[key])
                else:
                    nutrients[key] = None

            dishes.append(Dish(name=name, price_yen=price_yen, url=url, nutrients=nutrients))
    return dishes

# ---- 検索/集計 ----
def search_dishes(dishes: Iterable[Dish], keyword: str) -> List[Dish]:
    kw = keyword.strip()
    if not kw:
        return list(dishes)
    ds = list(dishes)
    return sorted(
        [d for d in ds if d.name.startswith(kw) or kw in d.name],
        key=lambda d: (0 if d.name.startswith(kw) else 1, d.name)
    )

def get_by_name(dishes: Iterable[Dish], name: str) -> Optional[Dish]:
    for d in dishes:
        if d.name == name:
            return d
    return None

def summarize_total(dishes: Iterable[Dish]) -> Dict[str, float]:
    total: Dict[str, float] = {k: 0.0 for k in _NUTRIENT_KEYS}
    for d in dishes:
        for k in _NUTRIENT_KEYS:
            v = d.get(k)
            if v is not None and not math.isnan(v):
                total[k] += float(v)
    return total

# ---- CLIコマンド ----
def ensure_csv_exists() -> None:
    if not CSV_PATH.exists():
        sys.stderr.write(f"[ERROR] CSV not found: {CSV_PATH}\n")
        sys.stderr.write("       このスクリプトと同じ場所に CSV を置いてください。\n")
        sys.exit(1)

def cmd_stats(args):
    ensure_csv_exists()
    dishes = load_menu(CSV_PATH)
    print(f"件数: {len(dishes)}")
    for d in dishes[: min(5, len(dishes))]:
        print(f"- {d.name} | {fmt_price(d.price_yen)} | kcal={fmt_num(d.get('energy_kcal'))}")

def cmd_search(args):
    ensure_csv_exists()
    dishes = load_menu(CSV_PATH)
    results = search_dishes(dishes, args.keyword)
    if not results:
        print("該当なし")
        return
    print(f"ヒット: {len(results)} 件（先頭 {args.limit} 件）")
    for d in results[: args.limit]:
        kcal = fmt_num(d.get("energy_kcal"))
        protein = fmt_num(d.get("protein_g"))
        fat = fmt_num(d.get("fat_g"))
        carb = fmt_num(d.get("carbs_g"))
        print(f"- {d.name} | {fmt_price(d.price_yen)} | kcal={kcal} P={protein}g F={fat}g C={carb}g")

def cmd_show(args):
    ensure_csv_exists()
    dishes = load_menu(CSV_PATH)
    d = get_by_name(dishes, args.name)
    if not d:
        print("見つかりませんでした。まずは search で名称を確認してください。")
        return
    print(f"[{d.name}]")
    print(f"価格: {fmt_price(d.price_yen)}")
    print(f"URL : {d.url or '-'}")
    print("栄養素:")
    for k in _NUTRIENT_KEYS:
        print(f"  - {k}: {fmt_num(d.get(k))}")

def cmd_sum(args):
    """名前に含むキーワードでまとめて合計（セット計算などに）"""
    ensure_csv_exists()
    dishes = load_menu(CSV_PATH)
    target = [d for d in dishes if args.keyword in d.name]
    if not target:
        print("該当なし")
        return
    total = summarize_total(target)
    print(f"対象件数: {len(target)}")
    print("合計値:")
    for k in _NUTRIENT_KEYS:
        print(f"  - {k}: {fmt_num(total.get(k))}")

def cmd_topkcal(args):
    ensure_csv_exists()
    dishes = load_menu(CSV_PATH)
    ds = [d for d in dishes if d.get("energy_kcal") is not None]
    ds.sort(key=lambda d: d.get("energy_kcal"), reverse=True)
    print(f"kcal上位 {args.n} 件")
    for d in ds[: args.n]:
        print(f"- {d.name} | {fmt_price(d.price_yen)} | kcal={fmt_num(d.get('energy_kcal'))}")

def cmd_sumx(args):
    """
    複数品を合計。デフォルト完全一致。--contains で部分一致。
    例:
      sumx "カレー中" "豚汁"
      sumx カレー 豚汁 --contains
    """
    ensure_csv_exists()
    dishes = load_menu(CSV_PATH)

    targets: List[Dish] = []
    not_found: List[str] = []

    if args.contains:
        seen = set()
        for token in args.items:
            matched = [d for d in dishes if token in d.name]
            if not matched:
                not_found.append(token)
                continue
            for d in matched:
                if id(d) not in seen:
                    seen.add(id(d))
                    targets.append(d)
    else:
        for name in args.items:
            d = get_by_name(dishes, name)
            if d:
                targets.append(d)
            else:
                not_found.append(name)

    if not targets:
        print("対象がありませんでした。")
        if not_found:
            print("未ヒット（名称差異の可能性）:")
            for x in not_found:
                print(f"  - {x}")
        return

    total = summarize_total(targets)

    print("合計対象:")
    for d in targets:
        print(f"  - {d.name} | {fmt_price(d.price_yen)}")
    if not_found:
        print("未ヒット:")
        for x in not_found:
            print(f"  - {x}")

    print("合計値:")
    for k in _NUTRIENT_KEYS:
        print(f"  - {k}: {fmt_num(total.get(k))}")

# ---- 引数パーサ ----
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="学食メニューCSV CLI（1ファイル完結版）")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("stats", help="件数とサンプル表示")
    sp.set_defaults(func=cmd_stats)

    sp = sub.add_parser("search", help="キーワード検索（部分一致/前方一致）")
    sp.add_argument("keyword", type=str, help="例: ラーメン")
    sp.add_argument("-n", "--limit", type=int, default=10, help="表示件数")
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("show", help="完全一致で1件表示")
    sp.add_argument("name", type=str, help="メニュー完全名")
    sp.set_defaults(func=cmd_show)

    sp = sub.add_parser("sum", help="名前に含むキーワードで絞って合計")
    sp.add_argument("keyword", type=str, help="例: カレー")
    sp.set_defaults(func=cmd_sum)

    sp = sub.add_parser("topkcal", help="kcal上位N件を表示")
    sp.add_argument("-n", type=int, default=10)
    sp.set_defaults(func=cmd_topkcal)

    sp = sub.add_parser("sumx", help="複数メニュー名をまとめて合計")
    sp.add_argument("items", nargs="+", help='例: "カレー中" "豚汁" もしくは カレー 豚汁 --contains')
    sp.add_argument("--contains", action="store_true", help="完全一致ではなく部分一致で拾う")
    sp.set_defaults(func=cmd_sumx)

    return p

def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()

