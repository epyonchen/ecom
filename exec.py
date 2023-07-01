#!/usr/bin/python
# coding=utf-8
from pw import OPENAI
from configs import bot_configs, env_configs
import pandas as pd
import numpy as np
import sys
import json
import openai
import chatgpt

global env
env = sys.platform

openai.api_key = OPENAI


def gen_chat(row, task, bot_config):    
    if task in ['cn', 'en']:
        input_key = row['input']
    elif task == 'trans':
        if 'output_en' in row.cols():
            input_key = row['output_en']
        else:
            print('需要先执行en')
            gen_chat(row, 'en', bot_config)
            return row
    else:
        print('输入有误')
        quit()
    try:
        bot = chatgpt.Conversation(bot_config['system'], 5)
        product_ans = bot.ask(bot_config['prompt'].format(input_key))
        row[f'output_{task}'] = product_ans
        
        product_dict = json.loads(product_ans)
        product_dict = map_ans_cols(ans_dict=product_dict, col_map=bot_configs['col_map'])
        product_series = pd.Series(product_dict).add_suffix(f'_{task}')
        row[product_series.index] = product_series
        
    except Exception as e:
        print(e)
        return row
    return row


def map_ans_cols(ans_dict, col_map):
    for kt, vt in col_map.items():
        key_hits = list(set(vt).intersection(ans_dict.keys()))
        if key_hits:
            ans_dict[kt] = ans_dict.pop(key_hits.pop())
    return ans_dict


def get_file_path(env_config, file_path=None, file_name=None):
    sep = env_config['sep']
    default_path = env_config['file_path']
    default_file = env_config['file_name']
    
    full_path = f'{file_path if file_path else default_path}{sep}{file_name if file_name else default_file}.xlsx'
    
    return full_path


def init_df(df, default_cols, task):
    task_cols = [col + '_' + task for col in default_cols]
    
    if not set(task_cols).issubset(set(list(df.columns))):
        df[task_cols] = np.nan
        
    return df


def exec_func(file_path=None, file_name=None, sheet_name=0, language=None):
    bc = bot_configs[language]
    ec = env_configs[env]
    full_path = get_file_path(env_config=ec, file_path=file_path, file_name=file_name)

    if not sheet_name:
        sheet_name = 0
    if not language:
        print('请输入cn/en/trans:')
        return exit()
    
    df = pd.read_excel(f'{full_path}', sheet_name=sheet_name)
    df = init_df(df=df, default_cols=bot_configs['default_cols'], task=language)   
    print(fr'读取成功: {full_path}, sheet: {sheet_name}. 共{df.shape[0]}行数据.')

    print('开始和chatgpt聊天')
    if env == 'win32':
        from tqdm import tqdm

        tqdm.pandas(desc='pandas bar')
        result = df.progress_apply(lambda x: gen_chat(x, language, bot_config=bc), axis=1)

    else:
        from pandarallel import pandarallel

        pandarallel.initialize(progress_bar=True, nb_workers=3)
        result = df.parallel_apply(lambda x: gen_chat(row=x, task=language, bot_config=bc), axis=1)

    with pd.ExcelWriter(f'{full_path}', engine='openpyxl', mode='a', if_sheet_exists='new') as xlsx_writer:
        print(fr'正在写入: {full_path}, sheet: output')
        result.to_excel(xlsx_writer, sheet_name='output', index=False)
        print('已完成')


input_path = input('输入文件夹路径（默认可直接回车）:')
input_file = input('输入文件名（默认可直接回车）:')
input_sheet = input('输入sheet名（默认可直接回车）:')
input_lang = input('输入cn/en/trans:')

exec_func(input_path, input_file, input_sheet, input_lang)
