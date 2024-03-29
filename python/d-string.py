# 要用到pyperclip完成剪切板操作
import re
import os
from pyperclip import copy
from typing import Callable, Union
from functools import partial
import json
import datetime
import markdown
import shutil


SECTION_NAME = [
    r'第1章 引言',
    r'第2章 从头开始：自然数',
    r'第3章 集合论',
    r'第4章 整数和有理数',
    r'第5章 实数',
    r'第6章 序列的极限',
    r'第7章 级数',
    r'第8章 无限集',
    r'第9章 R上的连续函数',
    r'第10章 函数的微分',
    r'第11章 黎曼积分',
    r'第12章 度量空间',
    r'第13章 度量空间上的连续函数',
    r'第14章 一致收敛',
    r'第15章 幂级数',
    r'第16章 傅里叶级数',
    r'第17章 多元微分学',
    r'第18章 勒贝格测度',
    r'第19章 勒贝格积分'
]


# 实分析笔记用这个快速转换跳转超链接
def md2pdf(post, force: str = None):
    _p = re.compile(r'实分析 (\d{1,2}\.\d{1,2} .*?)\.md')
    if _p.search(post) is not None:
        _name = _p.search(post).group(1)
    else:
        _name = '额外注释'
    with open(post, 'r', encoding='utf-8') as _f:
        _s = _f.read()
    match force:            # 检查是否通过参数强制设置单向转换
        case None:
            if _s.find(r'\md') == -1:
                _s = _s.replace(r'\pdf', r'\md')
                _s = _s.replace(r'.pdf', r'.md')
                _st = 'md'
            else:
                _s = _s.replace(r'\md', r'\pdf')
                _s = _s.replace(r'.md', r'.pdf')
                _st = 'pdf'
        case 'md':
            _s = _s.replace(r'\pdf', r'\md')
            _s = _s.replace(r'.pdf', r'.md')
            _st = 'md'
        case 'pdf':
            _s = _s.replace(r'\md', r'\pdf')
            _s = _s.replace(r'.md', r'.pdf')
            _st = 'pdf'
        case _:
            print('非法的输入')
    with open(post, 'w', encoding='utf-8') as _f:
        _f.write(_s)
    print(f'成功转换 {_name} 中跳转链接为指向{_st}')
    # 更新日期
    with open('date.json', 'r', encoding='utf-8') as _date_file:
        _data = json.load(_date_file)
    _today = datetime.datetime.now()
    _data[post] = f'{_today.year}-{_today.month}-{_today.day}'
    with open('date.json', 'w', encoding='utf-8') as _date_file:
        json.dump(_data, _date_file)


# 快速获取跳转超链接,注意要在跳转链接全是md时使用
def get_url(post):
    def get_num(_s1):
        _p = re.compile('(\d{1,2})\.(\d{1,2})')
        _s1 = _p.search(_s1)
        _num = int(_s1.group(1)) * 100 + int(_s1.group(2))
        return _num

    with open(post, 'r', encoding='utf-8') as _f:
        _s = _f.read()
    _p1 = re.compile(r'\[.*?\]\((.{6}第\d{1,2}章.{4}实分析.*?\.md)\)')
    _p2 = re.compile(r'md\\(实分析.*?)\.md')
    # 去重
    _list = list(set(_p1.findall(_s)))
    _list.sort(key=get_num)
    if not _list:
        print(f'本节({_p2.search(post).group(1)})没有需要标注的跳转链接')
    else:
        _output = '## 本节相关跳转\n'
        for _i in _list:
            _mess = _p2.search(_i)
            _output += f'\n[{_mess.group(1)}]({_i})\n'
        print(_output)
        # 复制到剪切板
        copy(_output)
    # 更新日期
    with open('date.json', 'r', encoding='utf-8') as _date_file:
        _data = json.load(_date_file)
    _today = datetime.datetime.now()
    _data[post] = f'{_today.year}-{_today.month}-{_today.day}'
    with open('date.json', 'w', encoding='utf-8') as _date_file:
        json.dump(_data, _date_file)


# 根据README.md快速制作目录文件SUMMARY.md
def make_summary():
    def get_num(_s1):
        _p = re.compile('(\d{1,2})\.(\d{1,2})')
        _s1 = _p.search(_s1)
        _num = int(_s1.group(1)) * 100 + int(_s1.group(2))
        _num1 = int(_s1.group(1))
        _num2 = int(_s1.group(2))
        return _num, _num1, _num2

    _project_dir = os.path.dirname(os.getcwd())
    _readme_path = os.path.join(_project_dir, 'README.md')
    _summary_path = os.path.join(_project_dir, 'SUMMARY.md')
    # 章节名字,以后记得补充
    global SECTION_NAME
    # 判断README中说的写到的位置
    with open(_readme_path, 'r', encoding='utf-8') as _f:
        _progress = re.search(r'笔记到(\d{1,2}\.\d{1,2})节，习题到(\d{1,2}.\d{1,2})节', _f.read())
        _goal = get_num(_progress.group(1))
        _bool = get_num(_progress.group(2))
    # 要写入SUMMARY.md的字符串
    _s = '# 目录\n\n* [引言](README.md)\n* [额外注释](额外注释\\md\\额外注释.md)'
    # 正则表达式
    _pattern1 = re.compile(r'实分析 (\d{1,2}\.\d{1,2} .*?)\.md')
    _pattern2 = re.compile(r'实分析 \d{1,2}\.\d{1,2} .*?\.md')
    for _i in range(_goal[1]):
        _s += f'\n* {SECTION_NAME[_i]}'
        _path = os.path.join(_project_dir, f'第{_i+1}章', 'md')
        # 获取目录下方文件名并依据章节号排序
        _file = [_x for _x in os.listdir(_path) if _pattern2.match(_x) is not None]
        _file.sort(key=lambda x: get_num(x)[2])
        # 历遍文件夹下所有文件
        for _j in _file:
            _sec = _pattern1.search(_j)[1]
            _pat = os.path.join(f'第{_i + 1}章', 'md', _j)
            # 当章节序号小于写到的题目时，标记为[x]
            if get_num(_j)[0] <= _bool[0]:
                _s += f'\n  * [x] [{_sec}]({_pat})'
            # 当章节序号大于写到的题目而小于笔记的章节时，标记为[ ]
            elif get_num(_j)[0] <= _goal[0]:
                _s += f'\n  * [ ] [{_sec}]({_pat})'
    # 写入文件，然后输出消息提示运行结束
    with open(_summary_path, 'w', encoding='utf-8') as _f:
        _f.write(_s)
    print(f'成功更新SUMMARY.md, 目前笔记进度{_goal[1]}.{_goal[2]}, 习题进度{_bool[1]}.{_bool[2]}')


# 寻找指定的md文件，并应用函数于文件路径，默认寻找全部的md文件
def map_file(func: Callable = print, field: str = None) -> None:
    _project_path = os.path.dirname(os.getcwd())
    _pattern = re.compile('(\d{1,2})\.(\d{1,2})')
    match field:
        case None:                                                                              # all
            for _dir in os.listdir(_project_path):
                _absolute_path = os.path.join(_project_path, _dir, 'md')
                if os.path.isdir(_absolute_path):
                    for _file in os.listdir(_absolute_path):
                        if os.path.splitext(_file)[1] == '.md':
                            func(os.path.join(_absolute_path, _file))
        case _ if os.path.isdir(os.path.join(_project_path, field, 'md')):         # directory
            _absolute_path = os.path.join(_project_path, field, 'md')
            for _file in os.listdir(_absolute_path):
                if os.path.splitext(_file)[1] == '.md':
                    func(os.path.join(_absolute_path, _file))
        case _match if _pattern.search(field):                                                  # file
            _match = _pattern.search(field)
            _absolute_path = os.path.join(_project_path, f'第{_match.group(1)}章', 'md')
            if os.path.isfile(os.path.join(_absolute_path, field)):
                func(os.path.join(_absolute_path, field))
        case _:
            print('无识别结果，已退出')


# 对指定的md文件做文本替换操作
def sub_string(file: str,
               old: str = None,
               new: str = None,
               use_re: bool = False,
               write_in: bool = True) -> Union[None, str]:
    with open(file, 'r', encoding='utf-8') as _f:
        _old_text = _f.read()
    if old is None or new is None:
        _new_text = _old_text
    else:
        if use_re:
            _compile = re.compile(old)
            _new_text = _compile.sub(new, _old_text)
        else:
            _new_text = _old_text.replace(old, new)
    if write_in:
        with open(file, 'w', encoding='utf-8') as _f:
            _f.write(_new_text)
    else:
        return _new_text


# 将指定的文件推送到gatsby的文件夹下
def write_in_gatsby(file: str):
    global SECTION_NAME
    _file_name = os.path.splitext(os.path.split(file)[1])[0]
    _pattern = re.compile('(\d{1,2})\.(\d{1,2}) (.+?)$')

    # 处理frontmatter
    _frontmatter = '---\ntype: "real-analysis"\n'
    _match = _pattern.search(_file_name)
    if _match is not None:
        _chapter = _match.group(1)
        _section = _match.group(2)
        _name = _match.group(3)
        _index = int(_chapter) * 100 + int(_section)
        _frontmatter += f'slug: "section-{_chapter}-{_section}"\n'
        _frontmatter += f'name: "{_chapter}.{_section} {_name}"\n'
        _frontmatter += f'index: {_index}\n'
        _chapter_name = SECTION_NAME[int(_chapter) - 1]
        _frontmatter += f'chapter: "{_chapter_name}"\n'
        _c_index = chr(int(_chapter) + 96)
        _frontmatter += f'chapter_index: {_c_index}\n'
    elif _file_name == '额外注释':
        _frontmatter += 'slug: "extra"\n'
        _frontmatter += 'name: "额外注释"\n'
        _frontmatter += 'index: 10000\n'
        _frontmatter += 'chapter: "额外注释"\n'
        _c_index = chr(25 + 96)
        _frontmatter += f'chapter_index: {_c_index}\n'
    _frontmatter += f'title: "{_file_name}"\n'
    with open('date.json', 'r', encoding='utf-8') as _date:
        _data = json.load(_date)
        _frontmatter += f'date: "{_data[file]}"\n'
    _frontmatter += '---\n'
    # 处理正文
    with open(file, 'r', encoding='utf-8') as _file:
        _text = _file.read()

    _dir = r'E:\Gatsby\personal-site\static\datafile\real-analysis'
    # 写到用于下载的数据文件夹
    with open(os.path.join(_dir, f'{_file_name}.md'), 'w', encoding='utf-8') as _goal:
        _goal.write(_text)

    _text = _text.replace(r'[toc]', "```toc\n```")  # 使用插件生成toc

    def _process_math_block(_match) -> str:
        _replaced = _match.group(0)
        _replaced = _replaced.replace(r'*', r'\*')
        _replaced = _replaced.replace(r'\\', r'\\\\')  # 先转换换行符
        _replaced = _replaced.replace(r'\#', r'\\#')  # 数学公式中使用的#也要转换
        _replaced = _replaced.replace(r'\{', r'\\{')  # 数学公式中使用的{和}也要转换
        _replaced = _replaced.replace(r'\}', r'\\}')
        _replaced = _replaced.replace(r'\;', r'\\;')  # 几种空格
        _replaced = _replaced.replace(r'\:', r'\\:')
        _replaced = _replaced.replace(r'\$', r'\\$')  # 原本使用了转义的$也要额外添加转义
        _replaced = _replaced.replace(r'\verb|\|', r'\textbackslash ')
        return _replaced

    _text = re.sub(r'(?<!\\)\$([\s\S]*?)(?<!\\)\$', _process_math_block, _text)
    _text = re.sub(r'(?<!\\)\${2}([\s\S]*?)(?<!\\)\${2}', _process_math_block, _text)

    def _repo(_match):
        _new = _match.group(1)
        if '额外注释' in _new:
            return '(../extra)'
        else:
            _result = re.search('(\d{1,2})\.(\d{1,2})', _new)
            return f'(../section-{_result[1]}-{_result[2]})'

    _text = re.sub(r'\(\.\.[\\/]\.\.[\\/].+?\\.+?\\(.+?)\)', _repo, _text)      # 处理跳转url

    # _text = re.sub(r'\$([^\n]+?)\$', r' $\1$ ', _text)
    # _text = re.sub(r'^(#{1,6} .*?)$', r'\1 {\1}', _text, flags=re.M)
    _text = _text.replace('_', r'\_')

    # 合并，然后写入到文件夹
    _main = _frontmatter + _text
    _dir = r'E:\Gatsby\personal-site\markdown\real-analysis\file'

    with open(os.path.join(_dir, f'{_file_name}.md'), 'w', encoding='utf-8') as _goal:
        _goal.write(_main)

    # 如果有图片也一并迁移过去
    _img_source = os.path.join(os.path.dirname(os.path.dirname(file)), 'img')
    _img_dir = os.path.join(os.path.dirname(_dir), 'img')
    if os.path.isdir(_img_source):
        if not os.path.isdir(_img_dir):
            os.mkdir(_img_dir)
        for _image in os.listdir(_img_source):
            _source = os.path.join(_img_source, _image)
            _destination = os.path.join(_img_dir, _image)
            shutil.copy(_source, _destination)
    print(f'成功将 {_file_name} 内容写入gatsby网站的文件夹')


# 临时函数，需要时可以用一下
def draft(path):
    pass


if __name__ == '__main__':
    p = r'E:\学习\导出文件汇总\Typora\笔记\实分析\第8章\md\实分析 8.5 有序集.md'
    # print(draft(p))
    # map_file(write_in_gatsby)
    # write_in_gatsby(p)
    # func = partial(sub_string, old=r'__(.+?)__', new=r'**\1**', use_re=True)
    # map_file(func)
    md2pdf(p)
    # get_url(p)
    # make_summary()
