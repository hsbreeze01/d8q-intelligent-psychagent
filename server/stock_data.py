#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取脚本，使用akshare获取股票实时数据
"""

import sys
import json
import akshare as ak


def get_stock_data(stock_code):
    """
    获取股票实时数据和历史数据
    :param stock_code: 股票代码或名称
    :return: 包含股票信息的字典
    """
    try:
        # 获取股票实时行情
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        
        # 查找匹配的股票
        stock_info = None
        
        # 1. 首先尝试精确匹配股票代码
        # 处理可能的代码格式问题（如去除前缀或空格）
        clean_stock_code = stock_code.strip()
        # 尝试精确匹配
        code_match = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == clean_stock_code]
        if not code_match.empty:
            stock_info = code_match.iloc[0].to_dict()
        else:
            # 2. 尝试模糊匹配股票代码（如输入部分代码）
            partial_code_match = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'].str.contains(clean_stock_code, na=False)]
            if not partial_code_match.empty:
                stock_info = partial_code_match.iloc[0].to_dict()
            else:
                # 3. 尝试匹配股票名称
                # 清理输入的名称
                clean_stock_name = stock_code.strip()
                
                # 使用正则表达式去除名称中的特殊前缀（XD、XR、DR）
                import re
                def clean_name(name):
                    return re.sub(r'^[XDR]+', '', name)
                
                # 创建一个新列用于匹配，包含清理后的名称
                stock_zh_a_spot_em_df['clean_name'] = stock_zh_a_spot_em_df['名称'].apply(clean_name)
                
                # 更灵活的名称匹配策略
                found = False
                
                # a. 首先尝试精确匹配清理后的名称
                exact_name_match = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['clean_name'] == clean_stock_name]
                if not exact_name_match.empty:
                    stock_info = exact_name_match.iloc[0].to_dict()
                    found = True
                
                # b. 如果没有找到，尝试部分匹配（用户输入的名称是股票名称的子集）
                if not found:
                    # 将用户输入的名称拆分为单个字符，确保至少有两个字符匹配
                    if len(clean_stock_name) >= 2:
                        # 构建正则表达式，匹配包含所有字符（顺序不限）的名称
                        # 例如："贵州茅台" 会匹配 "贵州茅" 或 "贵州茅台集团" 等
                        name_chars = list(clean_stock_name)
                        regex_pattern = '.*'.join(name_chars)
                        
                        # 匹配包含所有输入字符的清理后名称
                        partial_name_match = stock_zh_a_spot_em_df[
                            stock_zh_a_spot_em_df['clean_name'].str.contains(regex_pattern, na=False)
                        ]
                        
                        if not partial_name_match.empty:
                            stock_info = partial_name_match.iloc[0].to_dict()
                            found = True
                
                # c. 如果仍然没有找到，尝试更宽松的匹配：只要包含输入名称的前几个字符
                if not found:
                    # 取输入名称的前3个字符进行匹配
                    if len(clean_stock_name) >= 1:
                        prefix = clean_stock_name[:3]  # 取前3个字符
                        prefix_match = stock_zh_a_spot_em_df[
                            stock_zh_a_spot_em_df['clean_name'].str.startswith(prefix, na=False)
                        ]
                        
                        if not prefix_match.empty:
                            stock_info = prefix_match.iloc[0].to_dict()
                            found = True
                
                # d. 最后尝试直接匹配原始名称（包含特殊前缀）
                if not found:
                    original_name_match = stock_zh_a_spot_em_df[
                        stock_zh_a_spot_em_df['名称'].str.contains(clean_stock_name, na=False)
                    ]
                    
                    if not original_name_match.empty:
                        stock_info = original_name_match.iloc[0].to_dict()
        
        if not stock_info:
            return {'error': '未找到该股票信息'}
        
        # 获取股票历史数据
        # 注意：period参数可能不被接受，尝试去掉或使用正确的参数
        try:
            # 先尝试使用默认参数
            stock_zh_a_hist_df = ak.stock_zh_a_hist(
                symbol=stock_info['代码'],
                adjust="qfq"
            )
        except Exception as e:
            # 如果失败，尝试指定period参数
            try:
                stock_zh_a_hist_df = ak.stock_zh_a_hist(
                    symbol=stock_info['代码'],
                    period="daily",
                    adjust="qfq"
                )
            except Exception as e2:
                # 如果还是失败，返回基本数据，不包含历史数据
                return {
                    'code': stock_info['代码'],
                    'name': stock_info['名称'],
                    'price': float(stock_info['最新价']),
                    'change': str(stock_info['涨跌幅']),
                    'volume': int(stock_info['成交量']),
                    'history': []  # 空历史数据
                }
        
        # 处理历史数据
        history_data = []
        for index, row in stock_zh_a_hist_df.tail(30).iterrows():
            history_data.append({
                'date': str(row['日期']),
                'open': float(row['开盘']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'close': float(row['收盘'])
            })
        
        # 构建返回数据
        result = {
            'code': stock_info['代码'],
            'name': stock_info['名称'],
            'price': float(stock_info['最新价']),
            'change': str(stock_info['涨跌幅']),
            'volume': int(stock_info['成交量']),
            'history': history_data
        }
        
        return result
    
    except Exception as e:
        return {'error': f'获取股票数据失败: {str(e)}'}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(json.dumps({'error': '参数错误，需要股票代码或名称'}))
        sys.exit(1)
    
    stock_code = sys.argv[1]
    result = get_stock_data(stock_code)
    print(json.dumps(result, ensure_ascii=False))
