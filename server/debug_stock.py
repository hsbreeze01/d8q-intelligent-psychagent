#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本，用于查看akshare返回的股票列表数据结构
"""

import json
import akshare as ak

try:
    # 获取股票实时行情
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    
    # 打印数据结构信息
    print("数据列名:", list(stock_zh_a_spot_em_df.columns))
    
    # 打印前5行数据，查看数据格式
    print("\n前5行数据:")
    print(stock_zh_a_spot_em_df.head().to_string())
    
    # 尝试查找贵州茅台
    print("\n尝试查找贵州茅台:")
    # 先查看代码是否有问题
    code_search = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'].str.contains('600519', na=False)]
    if not code_search.empty:
        print("按代码查找结果:")
        print(code_search.to_dict('records')[0])
    
    # 再查看名称
    name_search = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['名称'].str.contains('贵州', na=False)]
    if not name_search.empty:
        print("\n按名称(贵州)查找结果:")
        print(name_search[['代码', '名称']].to_string())
    
    # 查看所有股票数量
    print(f"\n总股票数量: {len(stock_zh_a_spot_em_df)}")
    
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()