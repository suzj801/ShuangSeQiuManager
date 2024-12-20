#### AI生成蒙特卡洛选取双色球方法
import random
from collections import Counter

def monte_carlo_lottery(historical_data):
    # 提取蓝球和红球的历史数据
    all_red_numbers = [num for draw in historical_data for num in draw['red']]
    red_freq = Counter(all_red_numbers)
    
    # 提取所有历史蓝色号码
    blue_numbers = [draw['blue'] for draw in historical_data]
    blue_freq = Counter(blue_numbers)

    while 1:
        # 蒙特卡洛模拟
        blue_num = random.choices(list(blue_freq.keys()), weights=list(blue_freq.values()), k=1)[0]
        
        # 使用加权随机选择红色号码
        red_nums = random.choices(
            list(red_freq.keys()), 
            weights=list(red_freq.values()), 
            k=6
        )
        
        # 确保红色号码唯一且在1-33范围内
        red_nums = list(set(red_nums))
        while len(red_nums) < 6:
            new_num = random.randint(1, 33)
            if new_num not in red_nums:
                red_nums.append(new_num)
        
        yield {"blue": blue_num, "red": sorted(red_nums[:6])}
    


def continuity_analysis(historical_data):
    # 分析号码的连续性和间隔模式
    red_intervals = {}
    blue_intervals = {}
    
    for i in range(len(historical_data) - 1):
        current_draw = historical_data[i]
        next_draw = historical_data[i + 1]
        
        # 分析红球的连续性
        for red_num in current_draw['red']:
            if red_num in next_draw['red']:
                red_intervals[red_num] = red_intervals.get(red_num, 0) + 1
        
        # 分析蓝球的连续性
        if current_draw['blue'] == next_draw['blue']:
            blue_intervals[current_draw['blue']] = blue_intervals.get(current_draw['blue'], 0) + 1
    
    return red_intervals, blue_intervals

# 历史数据
history_data = [
    {'blue': 16, 'red': [1, 8, 13, 18, 20, 26]},    #2024128
    {'blue': 1, 'red': [9, 10, 13, 19, 24, 32]},    #2024129
    {'blue': 16, 'red': [1, 8, 12, 17, 19, 24]},    #2024130
    {'blue': 13, 'red': [4, 5, 11, 15, 20, 32]},    #2024131
    {'blue': 3, 'red': [1, 4, 25, 27, 30, 33]},     #2024132
    {'blue': 1, 'red': [1, 11, 15, 27, 30, 33]},    #2024133
    {'blue': 16, 'red': [2, 4, 13, 16, 18, 20]},    #2024134
    {'blue': 13, 'red': [5, 11, 17, 18, 30, 31]},   #2024135
    {'blue': 3, 'red': [3, 11, 15, 21, 25, 26]},    #2024136
    {'blue': 12, 'red': [4, 9, 10, 19, 26, 27]},    #2024137
    {'blue': 2, 'red': [2, 7, 11, 21, 27, 28]},     #2024138
    {'blue': 14, 'red': [15, 16, 20, 22, 23, 29]},  #2024139
    {'blue': 15, 'red': [4, 7, 8, 17, 22, 26]},     #2024140
    {'blue': 12, 'red': [1, 2, 7, 15, 24, 29]},     #2024141
    {'blue': 6, 'red': [4, 6, 13, 21, 22, 25]},     #2024142
    {'blue': 10, 'red': [2, 5, 11, 22, 30, 33]},    #2024143
    {'blue': 11, 'red': [2, 9, 11, 17, 20, 30]},    #2024144
]

def print_balls(index, balls):
    print(f"预测号码组 {index}: 蓝球 {balls['blue']} 红球 {balls['red']}")

def test1():
    #纯随机
    yieldBalls = monte_carlo_lottery(history_data)
    for i in range(5):
        balls = next(yieldBalls)
        print_balls(i, balls)

def test2():
    #取连续出现过的红球, 上球蓝球出过不要
    yieldBalls = monte_carlo_lottery(history_data)
    continuityBalls = continuity_analysis(history_data)
    redContinuityBalls = set(continuityBalls[0].keys())
    lastBlueBall = history_data[-1]['blue']
    print("连接出过的红球有:", redContinuityBalls, f"上期蓝球 {lastBlueBall} 跳过")
    i = 5
    while i > 0:
        balls = next(yieldBalls)
        if set(balls['red']) & redContinuityBalls and balls['blue'] != lastBlueBall :
            print_balls(6-i, balls)
            i -= 1

if __name__ == "__main__":
    # 分析连续性和间隔模式
    test2()
