#!/usr/bin/python
# coding=utf-8
from pw import OPENAI
import pandas as pd
import numpy as np
import sys
import json
import openai
import chatgpt

_default_file_path = r'C:\Users\BingliangChen\PycharmProjects\files'
_default_file_name = r'test'
_default_return_col = ['title', 'summary', 'description', 'keywords', 'title_cn', 'summary_cn', 'description_cn',
                       'keywords_cn']
_col_map = {
    'title': ['標題', '标题', 'titles'],
    'summary': ['摘要', '摘要', 'summaries'],
    'description': ['描述', '描述', 'descriptions'],
    'keywords': ['關鍵詞', '关键词', 'keyword']
}
openai.api_key = OPENAI


def gen_chat(row, task):
    if task == 'en':
        from bot_configs import en as bc
    elif task == 'cn':
        from bot_configs import cn as bc
        input_key = row['input']
    elif task == 'trans':
        from bot_configs import trans as bc
        if 'output_en' in row.cols():
            input_key = row['output_en']
        else:
            print('需要先执行en')
            gen_chat(row, 'en')
            return row
    else:
        print('输入有误')
        quit()

    try:
        bot = chatgpt.Conversation(bc['system'], 5)
        product_ans = bot.ask(bc['prompt'].format(input_key))
        product_dict = json.loads(product_ans)
        product_dict = map_ans_cols(product_dict)
        row[list(product_dict.keys())] = pd.Series(product_dict).add_suffix(f'_{task}')
        row[f'output_{task}'] = product_ans
    except Exception as e:
        print(e)
        return row

    return row


def map_ans_cols(ans_dict):
    for kt, vt in _col_map.items():
        key_hits = list(set(vt).intersection(ans_dict.keys()))
        if key_hits:
            ans_dict[kt] = ans_dict.pop(key_hits.pop())
    return ans_dict


def exec_func(path=None, file_name=None, sheet_name=0, language=None):
    if not path:
        path = _default_file_path
    if not file_name:
        file_name = _default_file_name
    if not sheet_name:
        sheet_name = 0
    if not language:
        print('请输入cn or en.')
        return exit()

    full_path = f'{path}\{file_name}.xlsx'
    df = pd.read_excel(fr'{full_path}', sheet_name=sheet_name)
    if not set(_default_return_col).issubset(set(list(df.columns))):
        df[_default_return_col] = np.nan
    print(fr'读取成功: {full_path}, sheet: {sheet_name}. 共{df.shape[0]}行数据.')

    print('开始和chatgpt聊天')
    if sys.platform == 'win32':
        from tqdm import tqdm

        tqdm.pandas(desc='pandas bar')
        result = df.progress_apply(lambda x: gen_chat(x, language), axis=1)

    else:
        from pandarallel import pandarallel

        pandarallel.initialize(progress_bar=True)
        result = df.parallel_apply(lambda x: gen_chat(x, language), axis=1)

    with pd.ExcelWriter(fr'{full_path}', engine='openpyxl', mode='a', if_sheet_exists='new') as xlsx_writer:
        print(fr'正在写入: {full_path}, sheet: output')
        result.to_excel(xlsx_writer, sheet_name='output', index=False)
        print('已完成')


input_path = input('输入文件夹路径（默认可直接回车）:')
input_file = input('输入文件名（默认可直接回车）:')
input_sheet = input('输入sheet名（默认可直接回车）:')
input_lang = input('输入cn or en:')
exec_func(input_path, input_file, input_sheet, input_lang)
