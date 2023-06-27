#!/usr/bin/python
# coding=utf-8
from pw import OPENAI
import pandas as pd
import numpy as np
import sys
import json
import openai
import chatgpt

_default_file_path = r'E:\projects\files'
_default_file_name = r'test'
_default_return_col = ['title', 'summary', 'description', 'keywords', 'title_cn', 'summary_cn', 'description_cn',
                       'keywords_cn']
openai.api_key = OPENAI


def generate_desc_en(row):
    writer_setting = '''
    You are an expert of digital marketing, you will describe product information in a clear and attracting way. 
    You are using English.'''
    input_key = row['input']
    product_prompt = f'''
    Return the answer as a JSON object.
    {input_key} According to my input of product information above in Chinese，generate Product Title, 
    Product Keywords, Product Summary and Product Description. Requirement： 1. Generate Product Title less than 50 
    letters; 2. Generate Product Summary less than 180 letters; 3. Generate Product Description in 600-700 letters; 
    4. Generate Product Keywords less than 30 words, according to product information. Each keyword should be less 
    than 3 words, capitalize first letter and splited by comma; 5. Return the answer as a JSON object with title, 
    summary, description and keywords.'''

    try:
        writer = chatgpt.Conversation(writer_setting, 5)
        product_ans = writer.ask(product_prompt)
        product_dict = json.loads(product_ans)
        row[_default_return_col] = np.nan
        row[list(product_dict.keys())] = pd.Series(product_dict)
        row['output_en'] = product_ans
    except Exception as e:
        print(e)
        return row


def generate_desc_cn(row):
    writer_setting = '''
    You are an expert of digital marketing, you will describe product information in a clear and attracting way. 
    You are using traditional Chinese.'''
    input_key = row['input']
    product_prompt = f'''
    Return the answer as a JSON object.
    {input_key} According to my input of product information above in Chinese，generate Product Title, 
    Product Keywords, Product Summary and Product Description. Requirement： 1. Generate Product Title less than 50 
    letters; 2. Generate Product Summary less than 180 letters; 3. Generate Product Description in 600-700 letters; 
    4. Generate Product Keywords less than 30 words, according to product information. Each keyword should be less 
    than 3 words, capitalize first letter and split by comma; 5. Return the answer as a JSON object with title, 
    summary, description and keywords. Return answer in traditional Chinese.'''

    try:
        writer = chatgpt.Conversation(writer_setting, 5)
        product_ans = writer.ask(product_prompt)
        print(product_ans)
        product_dict = json.loads(product_ans)
        row[_default_return_col] = np.nan
        row[list(product_dict.keys())] = pd.Series(product_dict)
        row['output_cn'] = product_ans
        print(row)
    except Exception as e:
        print(e)
        return row


def translate(row):
    if 'output_en' in row.cols():
        product_ans = row['output_cn']
    else:
        print('需要先执行en')
        return row

    try:
        translator_setting = '''
        You are a Taiwan native speaker. You are good at translating English into traditional Chinese.'''
        translator = chatgpt.Conversation(translator_setting, 5)
        trans_prompt = f'''
        Return the answer as a JSON object with title, summary, description and keywords.
        Translate each JSON values below from English into traditional Chinese.\n{product_ans}'''
        trans_ans = translator.ask(trans_prompt)
        trans_dict = json.loads(trans_ans)
        trans_dict = {f'{key}_cn': val for key, val in trans_dict.items()}
        row[_default_return_col] = np.nan
        row[list(trans_dict.keys())] = pd.Series(trans_dict).add_suffix('_cn')
        row['output_cn'] = trans_ans
    except Exception as e:
        print(e)
        return row

    return row


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

    print('\n开始和chatgpt聊天\n')
    if sys.platform == 'win32':
        from tqdm import tqdm

        tqdm.pandas(desc='pandas bar')
        if language == 'en':
            print('生成英文产品描述中：')
            df = df.progress_apply(generate_desc_en, axis=1)
            print('生成翻译中：')
            result = df.progress_apply(translate, axis=1)
        elif language == 'cn':
            print('生成中文产品描述中：')
            result = df.progress_apply(generate_desc_cn, axis=1)

    else:
        from pandarallel import pandarallel

        pandarallel.initialize(progress_bar=True)
        if language == 'en':
            print('生成英文产品描述中：')
            df = df.parallel_apply(generate_desc_en, axis=1)
            print('生成翻译中：')
            result = df.parallel_apply(translate, axis=1)
        elif language == 'cn':
            print('生成中文产品描述中：')
            result = df.parallel_apply(generate_desc_cn, axis=1)

    with pd.ExcelWriter(fr'{full_path}', engine='openpyxl', mode='a', if_sheet_exists='new') as xlsx_writer:
        print(fr'正在写入: {full_path}, sheet: output')
        result.to_excel(xlsx_writer, sheet_name='output', index=False)
        print('已完成')


input_path = input('输入文件夹路径（默认可直接回车）:')
input_file = input('输入文件名（默认可直接回车）:')
input_sheet = input('输入sheet名（默认可直接回车）:')
input_lang = input('输入cn or en:')
exec_func(input_path, input_file, input_sheet, input_lang)
