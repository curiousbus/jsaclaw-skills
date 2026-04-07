#!/usr/bin/env python3
"""财报关注列表管理脚本

命令:
  add-us <symbol> [name]     添加美股到关注列表
  add-hk <symbol> <name> [date]  添加港股到关注列表
  remove-us <symbol>         从关注列表删除美股
  remove-hk <symbol>         从关注列表删除港股
  list                       列出所有关注的股票和财报日期
  check                      运行财报检查主程序
  summary <symbol>           生成指定股票的财报简报
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path


# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace" / "earnings-alert"
CONFIG_PATH = WORKSPACE / "config.json"
FETCH_HK_PATH = WORKSPACE / "src" / "fetch_hk.py"
DB_PATH = WORKSPACE / "data" / "earnings.db"


def load_config():
    """加载配置文件"""
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(config):
    """保存配置文件"""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def add_us_stock(symbol: str, name: str = None):
    """添加美股到关注列表"""
    symbol = symbol.upper()
    config = load_config()

    # 检查是否已存在
    us_stocks = config.get("us_stocks", [])
    if symbol in us_stocks:
        print(f"✓ {symbol} 已在美股关注列表中")
        return

    # 添加到列表
    us_stocks.append(symbol)
    config["us_stocks"] = us_stocks
    save_config(config)

    display_name = name or symbol
    print(f"✓ 已添加美股关注: {symbol} ({display_name})")


def add_hk_stock(symbol: str, name: str, earnings_date: str = None):
    """添加港股到关注列表

    需要同时更新:
    1. config.json 的 hk_stocks 列表
    2. src/fetch_hk.py 的 HK_EARNINGS_DATA 字典
    """
    # 标准化股票代码（补零到4位）
    symbol = symbol.zfill(4)

    config = load_config()

    # 检查是否已存在
    hk_stocks = config.get("hk_stocks", [])
    for stock in hk_stocks:
        if stock.get("code") == symbol:
            print(f"✓ {symbol} 已在港股关注列表中")
            return

    # 添加到 config.json
    hk_stocks.append({"code": symbol, "name": name})
    config["hk_stocks"] = hk_stocks
    save_config(config)

    # 更新 fetch_hk.py 中的 HK_EARNINGS_DATA
    update_hk_earnings_data(symbol, name, earnings_date)

    print(f"✓ 已添加港股关注: {symbol} - {name}")
    if earnings_date:
        print(f"  财报日期: {earnings_date}")


def update_hk_earnings_data(symbol: str, name: str, earnings_date: str = None):
    """更新 fetch_hk.py 中的 HK_EARNINGS_DATA 字典

    使用正则表达式和文本替换来修改 Python 代码中的字典定义
    """
    # 默认财报日期：3个月后
    if not earnings_date:
        default_date = (date.today() + timedelta(days=90)).isoformat()
        earnings_date = default_date

    # 读取 fetch_hk.py 文件
    with open(FETCH_HK_PATH, "r") as f:
        content = f.read()

    # 构建要添加的新条目
    new_entry = '    "{}": {{"name": "{}", "earnings_date": "{}"}},'.format(symbol, name, earnings_date)

    # 检查是否已存在
    if '"{}":'.format(symbol) in content:
        # 更新现有条目
        pattern = r'"{symbol}":\s*\{{"name":\s*"[^"]*",\s*"earnings_date":\s*"[^"]*"\}}'.format(symbol=symbol)
        replacement = '"{}": {{"name": "{}", "earnings_date": "{}"}}'.format(symbol, name, earnings_date)
        content = re.sub(pattern, replacement, content)
    else:
        # 添加新条目 - 找到 HK_EARNINGS_DATA = { 后添加
        # 在最后一个字典条目后添加新条目
        pattern = r'(HK_EARNINGS_DATA\s*=\s*\{[^}]*?)(\n\s*\})'
        replacement = rf'\1\n{new_entry}\2'

        # 如果正则匹配失败，尝试在字典末尾添加
        if not re.search(pattern, content, re.DOTALL):
            # 找到字典的结束位置
            dict_end = content.find("}\n\n\nclass HKEarningsFetcher")
            if dict_end == -1:
                dict_end = content.find("}\n\n\nclass")
            if dict_end == -1:
                dict_end = content.rfind("}")
            if dict_end != -1:
                content = content[:dict_end] + new_entry + "\n" + content[dict_end:]
        else:
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    # 写回文件
    with open(FETCH_HK_PATH, "w") as f:
        f.write(content)


def remove_us_stock(symbol: str):
    """从关注列表删除美股"""
    symbol = symbol.upper()
    config = load_config()

    us_stocks = config.get("us_stocks", [])
    if symbol not in us_stocks:
        print(f"✗ {symbol} 不在美股关注列表中")
        return

    us_stocks.remove(symbol)
    config["us_stocks"] = us_stocks
    save_config(config)

    print(f"✓ 已删除美股关注: {symbol}")


def remove_hk_stock(symbol: str):
    """从关注列表删除港股

    需要同时更新:
    1. config.json 的 hk_stocks 列表
    2. src/fetch_hk.py 的 HK_EARNINGS_DATA 字典
    """
    # 标准化股票代码
    symbol = symbol.zfill(4)

    config = load_config()
    hk_stocks = config.get("hk_stocks", [])

    # 从 config.json 删除
    original_length = len(hk_stocks)
    hk_stocks = [s for s in hk_stocks if s.get("code") != symbol]

    if len(hk_stocks) == original_length:
        print(f"✗ {symbol} 不在港股关注列表中")
        return

    config["hk_stocks"] = hk_stocks
    save_config(config)

    # 从 fetch_hk.py 删除
    remove_from_hk_earnings_data(symbol)

    print(f"✓ 已删除港股关注: {symbol}")


def remove_from_hk_earnings_data(symbol: str):
    """从 fetch_hk.py 的 HK_EARNINGS_DATA 中删除条目"""
    with open(FETCH_HK_PATH, "r") as f:
        content = f.read()

    # 删除对应的条目（包括注释）
    # 匹配条目及前面的注释
    pattern = r'(?:\s*#[^\n]*\n)*\s*"' + re.escape(symbol) + r'":\s*\{[^}]*\},?\n'

    content = re.sub(pattern, "", content)

    with open(FETCH_HK_PATH, "w") as f:
        f.write(content)


def set_threshold(value: float):
    """设置涨跌幅阈值"""
    config = load_config()

    # 确保 price_alert 配置存在
    if "price_alert" not in config:
        config["price_alert"] = {}

    config["price_alert"]["threshold"] = value
    config["price_alert"]["enabled"] = True
    save_config(config)

    print(f"✓ 涨跌幅阈值已设置为 {value}%")
    print(f"✓ 异动提醒已开启")


def turn_on_alert():
    """开启异动提醒"""
    config = load_config()

    # 确保 price_alert 配置存在
    if "price_alert" not in config:
        config["price_alert"] = {}

    config["price_alert"]["enabled"] = True
    save_config(config)

    threshold = config["price_alert"].get("threshold", 5.0)
    print(f"✓ 异动提醒已开启")
    print(f"  当前阈值: {threshold}%")


def turn_off_alert():
    """关闭异动提醒"""
    config = load_config()

    # 确保 price_alert 配置存在
    if "price_alert" not in config:
        config["price_alert"] = {}

    config["price_alert"]["enabled"] = False
    save_config(config)

    print(f"✓ 异动提醒已关闭")


def show_alert_status():
    """查看异动提醒配置"""
    config = load_config()
    price_alert = config.get("price_alert", {})

    enabled = price_alert.get("enabled", True)
    threshold = price_alert.get("threshold", 5.0)
    check_interval = price_alert.get("check_interval_minutes", 15)

    print("\n🔔 异动提醒配置:")
    print(f"  状态: {'✓ 已开启' if enabled else '✗ 已关闭'}")
    print(f"  阈值: ±{threshold}%")
    print(f"  检查间隔: {check_interval} 分钟")
    print()


def list_watchlist():
    """列出所有关注的股票和财报日期"""
    try:
        import sqlite3
        from datetime import date as date_type
    except ImportError:
        print("✗ 需要 sqlite3 支持")
        return

    config = load_config()
    us_stocks = config.get("us_stocks", [])
    hk_stocks = config.get("hk_stocks", [])

    # 查询数据库获取财报日期
    earnings_data = {}
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        today = date_type.today().isoformat()

        cursor.execute("""
            SELECT symbol, name, market, earnings_date
            FROM earnings
            WHERE earnings_date >= ?
            ORDER BY earnings_date ASC
        """, (today,))

        for row in cursor.fetchall():
            key = f"{row['market']}:{row['symbol']}"
            earnings_data[key] = {
                "name": row["name"],
                "date": row["earnings_date"]
            }

        conn.close()

    # 输出美股列表
    print("\n📈 美股关注列表:")
    if not us_stocks:
        print("  (无)")
    else:
        for symbol in sorted(us_stocks):
            key = f"US:{symbol}"
            if key in earnings_data:
                e = earnings_data[key]
                # 计算距离天数
                try:
                    d = date_type.fromisoformat(e["date"])
                    days = (d - date_type.today()).days
                    days_str = f" ({days}天后)" if days > 0 else " (今天)"
                except:
                    days_str = ""
                print(f"  • {symbol:8s} - {e['name']:20s} | 财报: {e['date']}{days_str}")
            else:
                print(f"  • {symbol:8s} - (暂无财报数据)")

    # 输出港股列表
    print("\n🇭🇰 港股关注列表:")
    if not hk_stocks:
        print("  (无)")
    else:
        for stock in sorted(hk_stocks, key=lambda x: x.get("code", "")):
            code = stock.get("code", "")
            name = stock.get("name", "")
            key = f"HK:{code}"
            if key in earnings_data:
                e = earnings_data[key]
                try:
                    d = date_type.fromisoformat(e["date"])
                    days = (d - date_type.today()).days
                    days_str = f" ({days}天后)" if days > 0 else " (今天)"
                except:
                    days_str = ""
                print(f"  • {code:8s} - {name:20s} | 财报: {e['date']}{days_str}")
            else:
                print(f"  • {code:8s} - {name:20s}")

    print()


def run_check():
    """运行财报检查主程序"""
    venv_path = WORKSPACE / "venv"
    activate_script = venv_path / "bin" / "activate"

    if not activate_script.exists():
        print(f"✗ 虚拟环境不存在: {venv_path}")
        return

    cmd = f"cd {WORKSPACE} && source {activate_script} && python3 -m src.main"

    result = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"✗ 财报检查执行失败 (退出码: {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def generate_summary(symbol: str):
    """生成指定股票的财报简报"""
    # 确定股票市场
    if symbol[0].isdigit():
        market = "HK"
        symbol = symbol.zfill(4)
    else:
        market = "US"
        symbol = symbol.upper()

    # 检查数据库中是否有该股票的财报信息
    try:
        import sqlite3
        from datetime import date as date_type
    except ImportError:
        print("✗ 需要 sqlite3 支持")
        return

    if not DB_PATH.exists():
        print(f"✗ 数据库不存在，请先运行 check 命令获取财报数据")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT symbol, name, market, earnings_date
        FROM earnings
        WHERE symbol = ? AND market = ?
    """, (symbol, market))

    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"✗ 未找到 {symbol} ({market}) 的财报信息")
        print(f"  请先运行 check 命令获取财报数据")
        return

    # 调用 summary.py 生成简报
    venv_path = WORKSPACE / "venv"
    activate_script = venv_path / "bin" / "activate"

    if not activate_script.exists():
        print(f"✗ 虚拟环境不存在: {venv_path}")
        return

    # 创建临时脚本来生成简报
    temp_script = f"""
import sys
sys.path.insert(0, '{WORKSPACE}')
from datetime import date
from src.models import Earning
from src.summary import EarningsSummaryGenerator

earning = Earning(
    symbol='{row["symbol"]}',
    name='{row["name"]}',
    market='{row["market"]}',
    earnings_date=date.fromisoformat('{row["earnings_date"]}')
)

config = load_config()
api_key = config.get("alphavantage_api_key", "")
telegram_chat_id = config.get("telegram_chat_id", "")
finnhub_key = config.get("finnhub_api_key", "")

generator = EarningsSummaryGenerator(api_key, telegram_chat_id, finnhub_key)
success = generator.generate_and_send_summary(earning)

if success:
    print(f"✓ 已发送 {{earning.name}} ({earning.symbol}) 的财报简报")
else:
    print(f"✗ 发送简报失败")
    sys.exit(1)
"""

    # 临时脚本需要先导入必要的模块
    full_script = f"""
import sys
sys.path.insert(0, '{WORKSPACE}')
import json

def load_config():
    with open('{CONFIG_PATH}', 'r') as f:
        return json.load(f)

{temp_script}
"""

    cmd = f"cd {WORKSPACE} && source {activate_script} && python3 -c \"{full_script}\""

    result = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode != 0:
        print(f"✗ 生成简报失败 (退出码: {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="财报关注列表管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s add-us AAPL Apple
  %(prog)s add-hk 0700 腾讯控股 2026-05-15
  %(prog)s remove-us TSLA
  %(prog)s remove-hk 9988
  %(prog)s list
  %(prog)s check
  %(prog)s summary NVDA
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # add-us 命令
    add_us_parser = subparsers.add_parser("add-us", help="添加美股到关注列表")
    add_us_parser.add_argument("symbol", help="股票代码 (如: AAPL)")
    add_us_parser.add_argument("name", nargs="?", help="公司名称 (可选)")

    # add-hk 命令
    add_hk_parser = subparsers.add_parser("add-hk", help="添加港股到关注列表")
    add_hk_parser.add_argument("symbol", help="股票代码 (如: 0700)")
    add_hk_parser.add_argument("name", help="公司名称")
    add_hk_parser.add_argument("date", nargs="?", help="财报日期 YYYY-MM-DD (可选)")

    # remove-us 命令
    remove_us_parser = subparsers.add_parser("remove-us", help="删除美股关注")
    remove_us_parser.add_argument("symbol", help="股票代码")

    # remove-hk 命令
    remove_hk_parser = subparsers.add_parser("remove-hk", help="删除港股关注")
    remove_hk_parser.add_argument("symbol", help="股票代码")

    # list 命令
    subparsers.add_parser("list", help="列出所有关注的股票")

    # check 命令
    subparsers.add_parser("check", help="运行财报检查")

    # summary 命令
    summary_parser = subparsers.add_parser("summary", help="生成财报简报")
    summary_parser.add_argument("symbol", help="股票代码")

    # threshold 命令
    threshold_parser = subparsers.add_parser("threshold", help="设置涨跌幅阈值")
    threshold_parser.add_argument("value", type=float, help="阈值（百分比，如 3.5）")

    # threshold-on 命令
    subparsers.add_parser("threshold-on", help="开启异动提醒")

    # threshold-off 命令
    subparsers.add_parser("threshold-off", help="关闭异动提醒")

    # alert-status 命令
    subparsers.add_parser("alert-status", help="查看异动提醒配置")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行对应命令
    if args.command == "add-us":
        add_us_stock(args.symbol, args.name)
    elif args.command == "add-hk":
        add_hk_stock(args.symbol, args.name, args.date)
    elif args.command == "remove-us":
        remove_us_stock(args.symbol)
    elif args.command == "remove-hk":
        remove_hk_stock(args.symbol)
    elif args.command == "list":
        list_watchlist()
    elif args.command == "check":
        run_check()
    elif args.command == "summary":
        generate_summary(args.symbol)
    elif args.command == "threshold":
        set_threshold(args.value)
    elif args.command == "threshold-on":
        turn_on_alert()
    elif args.command == "threshold-off":
        turn_off_alert()
    elif args.command == "alert-status":
        show_alert_status()


if __name__ == "__main__":
    main()
