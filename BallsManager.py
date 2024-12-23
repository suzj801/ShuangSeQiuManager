import os
import time
import random
from BallsDB import LotteryBalls, PaidBalls, initDB
from BallsScrapy import get_lottery_balls, ScrapyException
from datetime import datetime
from tabulate import tabulate
import functools
import traceback

def wraps_KeyBoardInterrupt(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n")
    return wrapper

@wraps_KeyBoardInterrupt
def scrape_balls():
    scrape_range = [None, None]
    while 1:
        if scrape_range[0] == None:
            startLotteryNo = input("请输入开始期号(ctrl+c退出):")
            try:
                startLotteryNo = int(startLotteryNo)
            except:
                print("输入的期号格式不正确")
                continue
            scrape_range[0] = startLotteryNo
        if scrape_range[1] == None:
            endLotteryNo = input("请输入结束期号(输入0表示爬取到最新一期, ctrl+c退出):")
            try:
                endLotteryNo = int(endLotteryNo)
                if endLotteryNo and endLotteryNo < startLotteryNo:
                    print("结束期号必须大于开始期号")
                    continue
            except:
                print("输入的期号格式不正确")
                continue
        break
    while 1:
        if endLotteryNo and startLotteryNo > endLotteryNo:
            break
        try:
            balls = get_lottery_balls(str(startLotteryNo))
            print("获取第%s期开奖号码, 中奖号码为:"%startLotteryNo, end='')
            LotteryBalls.add_balls(balls)
            print(f"蓝球:{balls['blue']}, 红球: {*balls['red'],}")
            startLotteryNo += 1
            time.sleep(1)
        except Exception as e:
            #traceback.print_exc()
            if isinstance(e, ScrapyException):
                yes = input(f"\r第{startLotteryNo}期未爬到结果:({e.message}), 是否继续?(请输入y或者n)")
                if yes.lower() in ["y", "yes"]:
                    continue
            break
    print("")

@wraps_KeyBoardInterrupt
def add_paid_balls():
    paidDate = None
    lotteryNo = None
    goOn = ""
    addedBalls = []
    while 1:
        if not paidDate:
            dateExample = datetime.now().strftime("%Y-%m-%d")
            _paidDate = input(f"请输入购买日期(格式:{dateExample}, 直接回车则代表今天, ctrl+c退出)")
            if _paidDate:
                try:
                    paidDate = datetime.strptime(_paidDate, "%Y-%m-%d")
                except:
                    print("日期格式不正确")
                    continue
            else:
                paidDate = datetime.today()
        if not lotteryNo:
            newestLotteryNo = LotteryBalls.get_newest_lotteryno()
            newestLotteryMessage = f"直接回车代表购买最新一期:{int(newestLotteryNo)+1}, " if newestLotteryNo else "" 
            lotteryNo = input(f"请输入购买期号({newestLotteryMessage}ctrl+c退出)")
            try:
                if lotteryNo.isdigit():
                    lotteryNo = int(lotteryNo)
                elif newestLotteryNo:
                    lotteryNo = int(newestLotteryNo) + 1
                else:
                    raise Exception()
            except:
                print("期号格式不正确")
                continue
        try:
            _balls = input(f"请{goOn}输入购买的号码(第1个为红球, 最后1个为蓝球, 以空格隔开, ctrl+c退出)")
        except KeyboardInterrupt:
            if addedBalls:
                print("\n本次添加以下号码:\n")
                pretty_print_balls(addedBalls)
            raise
        *redBalls, blueBall = _balls.split(" ")
        try:
            PaidBalls.add_balls({
                'blue': int(blueBall),
                'red': [int(ball) for ball in redBalls],
                'lotteryNo': lotteryNo,
                'paidDate': paidDate
            })
            goOn = "继续"
            addedBalls.append({
                "序号": f"第{len(addedBalls)+1}组",
                "期号": lotteryNo,
                "蓝球": f"{blueBall:02d}",
                "红球": " ".join(f"{ball:02d}" for ball in redBalls)
            })
        except:
            #traceback.print_exc()
            print("输入的号码格式不正确")
            continue

def pretty_print_balls(balls):
    print(tabulate(balls, headers="keys", tablefmt="simple_grid"))

def format_paid_balls(balls):
    _balls = []
    for ball in balls:
        _balls.append({
            "购买日期": ball["paidDate"],
            "期号": ball["lotteryNo"],
            "蓝球": f"{ball['ballBlue']:02d}",
            "红球": f"{ball['ballRed1']:02d} {ball['ballRed2']:02d} {ball['ballRed3']:02d} " \
                f"{ball['ballRed4']:02d} {ball['ballRed5']:02d} {ball['ballRed6']:02d}",
            "是否中奖": ball["winningLevel"]
        })
    return _balls

@wraps_KeyBoardInterrupt
def check_paid_balls():
    checkedBalls = PaidBalls.check_lottery()
    if checkedBalls:
        pretty_print_balls(format_paid_balls(checkedBalls))
    else:
        newestLotteryNo = LotteryBalls.get_newest_lotteryno()
        yes = input(f"所有中奖结果都检查完毕, 是否打印最新一期({newestLotteryNo})的中奖结果?(请输入y或者n)")
        if yes.lower() in ["y", "yes"]:
            pretty_print_balls(format_paid_balls(PaidBalls.get_balls({"lotteryNo": newestLotteryNo})))
    print("\n")

def print_all_unchecked_balls():
    pretty_print_balls(format_paid_balls(PaidBalls.get_balls({"checked": False})))
    print("\n")

def print_split_line(message):
    width = os.get_terminal_size().columns - len(message)
    print("")
    print(message.center(width, "-"))
    print("")

def random_balls_with_monte_carlo(balls):
    #使用蒙特卡洛模拟法随机取球
    while 1:
        blueBalls = random.choices(list(balls["blue"].keys()), weights=list(balls["blue"].values()), k=1)
        if blueBalls:
            blueBall = blueBalls[0]
        else:
            blueBall = random.choice(balls["blue"])
        redBalls = random.choices(list(balls["red"].keys()), weights=list(balls["red"].values()), k=6)
        redBalls = list(set(redBalls))
        while len(redBalls) < 6:
            redBalls.append(random.choice(list(balls["red"].keys())))
        yield {"blue": blueBall, "red": sorted(redBalls)}

def print_picked_balls(balls):
    if balls:
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
        print("已选取以下号码:")
        pretty_print_balls([{
            "序号": i+1,
            "红球": " ".join(f"{b:02d}" for b in ball["red"]),
            "蓝球": f"{ball['blue']:02d}"
        } for i, ball in enumerate(balls)])
        print_split_line("")

@wraps_KeyBoardInterrupt
def pick_balls():
    pickedBalls = []
    while 1:
        print_picked_balls(pickedBalls)
        anayIndex = input("请选择分析历史球的模式(1: 出现次数 2: 连续出现次数 3:不用分析)(ctrl+c退出)")
        anayBalls = {}
        if anayIndex == "1":
            print("所有球出现次数分析中...", end="")
            startTime = time.time()
            anayBalls = LotteryBalls.get_balls_freq()
            endTime = time.time()
            print("用时%.2f秒"%(endTime-startTime))
        elif anayIndex == "2":
            print("所有球连续出现次数分析中...", end="\r")
            startTime = time.time()
            anayBalls = LotteryBalls.get_balls_continuity()
            endTime = time.time()
            print("用时%.2f秒"%(endTime-startTime))
        elif anayIndex == "3":
            anayBalls = {"blue":{i:1 for i in range(1, 17)}, "red":{i:1 for i in range(1, 34)}}
        else:
            print("输入有误, 请重新输入")
            continue
        for balls in random_balls_with_monte_carlo(anayBalls):
            print_picked_balls(pickedBalls)
            print(tabulate([["蓝球", f"{balls['blue']:02d}"], ["红球", " ".join(f"{b:02d}" for b in balls["red"])]],
                           tablefmt="simple_grid"))
            try:
                yes = input("是否保留此组号码(y/保留, n/跳过, c/重新分析继续选球)(ctrl+c退出)")
            except KeyboardInterrupt:
                print_picked_balls(pickedBalls)
                raise
            if yes.lower() in ["y", "yes"]:
                pickedBalls.append(balls)
            elif yes.lower() in ["c", "continue"]:
                break
@wraps_KeyBoardInterrupt
def main():
    initDB()
    while 1:
        print("请选择操作:")
        print("1. 爬取开奖号码")
        print("2. 添加购买号码")
        print("3. 检查中奖结果")
        print("4. 查看未出奖号码")
        print("5. 随机摇号")
        print("9. 退出(ctrl+c)")
        choice = input("请输入你的选择:")
        if choice == "1":
            print_split_line("爬取开奖号码")
            scrape_balls()
        elif choice == "2":
            print_split_line("添加购买号码")
            add_paid_balls()
        elif choice == "3":
            print_split_line("检查中奖结果")
            check_paid_balls()
        elif choice == "4":
            print_split_line("查看未出奖号码")
            print_all_unchecked_balls()
        elif choice == "5":
            print_split_line("随机摇号")
            pick_balls()
        elif choice == "9":
            break
        else:
            print("\n无效的选择\n")

if __name__ == "__main__":
    main()