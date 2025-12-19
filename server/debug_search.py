#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细调试股票查找过程的脚本
"""

import json
import akshare as ak
import re

# 用户输入
stock_input = "贵州茅台"

# 清理函数
def clean_name(name):
    return re.sub(r'^[XDR]+', '', name)

try:
    # 获取股票数据
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    print(f"总股票数量: {len(stock_zh_a_spot_em_df)}")
    
    # 步骤1: 精确匹配代码
    print(f"\n步骤1: 精确匹配代码 '{stock_input}'")
    code_match = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == stock_input.strip()]
    print(f"精确代码匹配结果: {len(code_match)} 条")
    
    # 步骤2: 模糊匹配代码
    print(f"\n步骤2: 模糊匹配代码 '{stock_input}'")
    partial_code_match = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'].str.contains(stock_input.strip(), na=False)]
    print(f"模糊代码匹配结果: {len(partial_code_match)} 条")
    
    # 步骤3: 模糊匹配名称
    print(f"\n步骤3: 模糊匹配名称 '{stock_input}'")
    
    # 先检查所有包含'贵州'的股票
    guizhou_stocks = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['名称'].str.contains('贵州', na=False)]
    print(f"包含'贵州'的股票数量: {len(guizhou_stocks)}")
    if len(guizhou_stocks) > 0:
        print("包含'贵州'的股票:")
        for _, row in guizhou_stocks.iterrows():
            print(f"  代码: {row['代码']}, 原始名称: {row['名称']}, 清理后名称: {clean_name(row['名称'])}")
    
    # 检查是否有包含'茅台'的股票
    maotai_stocks = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['名称'].str.contains('茅台', na=False)]
    print(f"\n包含'茅台'的股票数量: {len(maotai_stocks)}")
    if len(maotai_stocks) > 0:
        print("包含'茅台'的股票:")
        for _, row in maotai_stocks.iterrows():
            print(f"  代码: {row['代码']}, 原始名称: {row['名称']}, 清理后名称: {clean_name(row['名称'])}")
    
    # 尝试直接使用清理后的名称进行匹配
    print(f"\n尝试使用清理后的名称进行匹配:")
    stock_zh_a_spot_em_df['clean_name'] = stock_zh_a_spot_em_df['名称'].apply(clean_name)
    
    # 尝试匹配'贵州茅台'
    clean_match = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['clean_name'].str.contains('贵州茅台', na=False)]
    print(f"清理后名称匹配'贵州茅台'结果: {len(clean_match)} 条")
    
    # 尝试匹配'贵州'
    clean_guizhou_match = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['clean_name'].str.contains('贵州', na=False)]
    print(f"清理后名称匹配'贵州'结果: {len(clean_guizhou_match)} 条")
    if len(clean_guizhou_match) > 0:
        print("清理后名称包含'贵州'的股票:")
        for _, row in clean_guizhou_match.iterrows():
            print(f"  代码: {row['代码']}, 原始名称: {row['名称']}, 清理后名称: {row['clean_name']}")
    
    # 尝试匹配'茅台'
    clean_maotai_match = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['clean_name'].str.contains('茅台', na=False)]
    print(f"\n清理后名称匹配'茅台'结果: {len(clean_maotai_match)} 条")
    if len(clean_maotai_match) > 0:
        print("清理后名称包含'茅台'的股票:")
        for _, row in clean_maotai_match.iterrows():
            print(f"  代码: {row['代码']}, 原始名称: {row['名称']}, 清理后名称: {row['clean_name']}")
    
    # 尝试按代码600519查找
    print(f"\n步骤4: 直接按代码'600519'查找")
    code_600519 = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == '600519']
    if len(code_600519) > 0:
        print("找到600519:")
        stock_info = code_600519.iloc[0].to_dict()
        print(f"  代码: {stock_info['代码']}, 名称: {stock_info['名称']}, 最新价: {stock_info['最新价']}")
    
    # 检查clean_name列的前10行
    print(f"\n前10行的清理后名称:")
    for _, row in stock_zh_a_spot_em_df.head(10).iterrows():
        print(f"  {row['名称']} -> {clean_name(row['名称'])}")
    
    # 检查是否存在编码问题
    print(f"\n检查编码:")
    test_str = "贵州茅台"
    print(f"用户输入: '{test_str}', 类型: {type(test_str)}")
    
    # 尝试手动构建匹配
    print(f"\n手动尝试匹配:")
    for idx, row in stock_zh_a_spot_em_df.iterrows():
        name = row['名称']
        clean = clean_name(name)
        if '贵州' in clean and '茅' in clean:
            print(f"找到匹配: 代码={row['代码']}, 名称={name}, 清理后={clean}")
            break
    
    print(f"\n查找结束")
    
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()