# -*- coding:utf-8 -*-
# Python3

# 功能：正则表达式词法和语法分析器

import sys

from argv_parse import argv_parse
from utils import bit1_from_list, bit1_from_range, bit1_count, bit1_pos_yield, bit1_or, bit1_and, bit1_exclude, bit1_include_truely, bit1_include, CHARSET_SIZE, CHARSET_FULL, CHARSET_BORDER, CHARSET_DOT, CHARSET_WORDS, CHARSET_DIGITS, CHARSET_SPACES, charset_bit1_to_str

# 正则表达式的追加转义字符: \w, \d, \s, \W, \D, \S ，它们各自对应字符集
CHARSET_SPECIAL = {
    '\\w' : CHARSET_WORDS ,
    '\\d' : CHARSET_DIGITS ,
    '\\s' : CHARSET_SPACES ,
    '\\W' : bit1_exclude(CHARSET_DOT, CHARSET_WORDS) ,
    '\\D' : bit1_exclude(CHARSET_DOT, CHARSET_DIGITS) ,
    '\\S' : bit1_exclude(CHARSET_DOT, CHARSET_SPACES) ,
}


# 通用转义字符：
COMMON_ESCAPE = ['\\\\', '\\0', '\\a', '\\b', '\\e', '\\f', '\\n', '\\r', '\\t', '\\v']


# 正则表达式中的特殊计数约束: '?', '+', '*' ，以及其对应的计数范围=(最小, 最大) , 注意：-1代表正无穷+∞
COUNTING_CONSTRAINTS_SPECIAL = {
    '?' : (0,  1) ,
    '+' : (1, -1) ,
    '*' : (0, -1)
}



# 函数： regex_parse_2num_tuple
# 功能： 解析正则表达式中的计数约束
# 参数： 计数约束字符串 'n,m' ，是正则表达式的{}中抽取的，原始格式 '{n,m}'
# 返回： 二元组 (n,m)，n是最小计数约束，m是最大计数约束，m有可能=-1，代表正无穷+∞
#        如果不符合计数约束的格式，就抛出异常
def regex_parse_2num_tuple(string):
    string = string.strip()
    assert string != ''
    num_list = list( map( lambda x:x.strip(), string.split(',') ) )
    if num_list[0] == '':
        num_0 = 0
    else:
        num_0 = int(num_list[0])
        assert 0 <= num_0
    if len(num_list) < 2:
        return (num_0, num_0)
    elif num_list[1] == '':
        return (num_0, -1)
    else:
        num_1 = int(num_list[1])
        assert 0 < num_1 and num_0 <= num_1
        return (num_0, num_1)



# 函数： regex_lexical_parser
# 功能： 正则表达式词法分析器（基于 yield 的迭代器）
# 参数： str regex 正则表达式字符串
# 返回： 顺序迭代出正则表达式中的词语，包括以下三类：
#          第一类：单字符字符串，表示普通字符
#          第二类：双字符字符串，第一个字符是 '\\' ，第二个字符包括:
#                    1. 正则表达式追加转义字符，用来表示字符集的 w, s, d, W, S, D
#                    2. 通配符 .
#                    3. 边界符 ^ , $
#                    4. 用来表示自定义字符集的 [, [^, ] ，以及其中出现的用来表示字符集范围的 -
#                    5. 连词 (, ), |
#          第三类：二元组，计数约束范围 (n,m)，n是最小计数约束，m是最大计数约束，m有可能=-1，代表正无穷+∞
def regex_lexical_parser(regex):
    is_charset, canbe_range = False, False
    ptr = 0
    while ptr < len(regex):
        char  = regex[ptr]
        word  = regex[ptr:min(ptr+2,len(regex))]
        dword = regex[ptr:min(ptr+4,len(regex))]
        if   word in COMMON_ESCAPE:                                                     # 1. 遇到通用转义字符
            ptr += 2                                                                    # 1
            yield eval("'"+word+"'")                                                    # 1.   直接返回该单字符
        elif word == '\\x':                                                             # 2. 遇到十六进制数表示的字符
            try:                                                                        # 2
                tmp = eval("'"+dword+"'")                                               # 2
                assert len(tmp) == 1                                                    # 2
                ptr += 4                                                                # 2
                yield tmp                                                               # 2.   十六进制解析成功，直接返回该单字符
            except:                                                                     # 2
                ptr += 1                                                                # 2
                yield char                                                              # 2    十六进制解析失败，
        elif word in CHARSET_SPECIAL:                                                   # 3. 遇到正则表达式追加转义字符（也就是几种特殊字符集）
            ptr += 2                                                                    # 3
            yield word                                                                  # 3.   返回，前面必然带\，例如返回'\\w'
        elif char == '\\':                                                              # 4. 遇到其余转义字符，例如 \[ 被视作字符 [ ，而不是正则表达式中的字符集符号[]，另外，未定义的转义字符如果也被转义，则被视作原字符，例如 \z 被直接视作字符 z
            ptr += 2                                                                    # 4
            yield word[-1]                                                              # 4.   直接返回该单字符
        elif is_charset:                                                                # 5. 如果在字符集括号 [] 内
            ptr += 1                                                                    # 5
            if char == ']':                                                             # 5
                yield '\\]'                                                             # 5.   遇到字符集末尾 ] ，就返回 '\\]'
                is_charset, canbe_range = False, False                                  # 5
            elif char == '-' and canbe_range:                                           # 5
                yield '\\-'                                                             # 5.   遇到范围符号-，就返回 '\\-'
                canbe_range = False                                                     # 5
            else:                                                                       # 5
                yield char                                                              # 5.   遇到单字符，直接返回它
                canbe_range = True                                                      # 5
        elif word == '[]':
            ptr += 2
            yield '['
            yield ']'
        elif word == '[^':                                                              # 6. 遇到开始字符集符号 [^ (反向字符集)
            ptr += 2                                                                    # 6
            is_charset, canbe_range = True, False                                       # 6
            yield '\\[^'                                                                # 6.   返回 '\\[^'
        elif char == '[':                                                               # 7. 遇到开始字符集符号 [ (正向字符集)
            ptr += 1                                                                    # 7
            is_charset, canbe_range = True, False                                       # 7
            yield '\\['                                                                 # 7.   返回 '\\['
        elif char == '{':                                                               # 8. 遇到计数范围 {}
            ptr += 1                                                                    # 8
            eptr = regex.find('}', ptr)                                                 # 8
            if eptr < 0:                                                                # 8    找不到对应的 }
                yield char                                                              # 8
            else:                                                                       # 8    找到了对应的 {
                try:
                    yield regex_parse_2num_tuple(regex[ptr:eptr])
                    ptr = eptr + 1
                except:
                    yield char
        elif char in COUNTING_CONSTRAINTS_SPECIAL:                                      # 9. 遇到特殊计数约束: '?', '+', '*'
            ptr += 1                                                                    # 9
            yield COUNTING_CONSTRAINTS_SPECIAL[char]                                    # 9.   返回计数范围 (最小, 最大)
        elif char in '.^$()|':                                                          # 10.遇到其它特殊字符，包括全字符集(通配符). ，边界符 ^$， 连词 ()|
            ptr += 1                                                                    # 10
            yield '\\' + char                                                           # 10.  给它前面加上 '\\' ，返回
        else:                                                                           # 11.普通字符
            ptr += 1                                                                    # 11
            yield char                                                                  # 11.  返回该字符



# 迭代函数： regex_parser
# 功能： 正则表达式语法分析器
# 参数： str regex 正则表达式字符串
# 返回： 顺序迭代出语法元素，每条结果可以有三类：
#          第一类： 字符集，类型为 int
#          第二类： 量词，为 2-tuple，第一项是int型，代表最小重复次数；第二项是int型，代表最大重复次数。最大重复次数可能是 -1，代表正无穷+∞
#          第三类： 连词，为 str 类型，而且是单字符，只能是 '('和')'(表示子规则) '|'表示或
def regex_parser(regex:str):
    acc_cset = None
    last_char = '\xff'
    last_is_range = False
    is_inverse = False

    for word in regex_lexical_parser(regex):
        
        if word in ['\\(', '\\)', '\\|']:                                         # 对于连词，删除其开头的辅助性 \ 符号，直接返回
            yield word[-1]
            continue
        
        if word in ['\\^', '\\$']:                                                # 对于边界符，返回边界符字符集（把起始符^和结束符$当作一个特殊字符）
            yield CHARSET_BORDER
            continue
        
        if type(word) == tuple:                                                   # 对于量词（计数约束），直接返回
            yield word
            continue
        
        if   word == '\\.':                                                       # 对于 通配符 .
            cur_cset = CHARSET_DOT
        elif word in CHARSET_SPECIAL:                                             # 对于 正则表达式追加转义字符
            cur_cset = CHARSET_SPECIAL[word]
        elif len(word) == 1 and last_is_range:                                    # 对于单字符
            cur_cset = bit1_from_range(ord(last_char), ord(word))
            last_char = word
        elif len(word) == 1:
            cur_cset = bit1_from_list([ord(word)])
            last_char = word
        else:
            cur_cset = None
        
        last_is_range = word == '\\-'
        
        if not cur_cset is None:
            if acc_cset is None:
                assert cur_cset != 0
                yield cur_cset
            else:
                acc_cset = bit1_or(acc_cset, cur_cset)
        
        if   word == '\\[':
            acc_cset = 0
            is_inverse = False
        elif word == '\\[^':
            acc_cset = 0
            is_inverse = True
        elif word == '\\]':
            if is_inverse:
                acc_cset = bit1_exclude(CHARSET_DOT, acc_cset)
            assert acc_cset != 0
            yield acc_cset
            acc_cset = None



# 主程序：用于测试 函数 regex_parser
# 功能：指定一个正则表达式文件（里面每行一个正则表达式），打印其语法分析结果
if __name__ == '__main__':
    
    # 解析命令行参数
    (REGEX_FNAME,), _ = argv_parse(['.re'])
    if REGEX_FNAME == '':
        print('Usage: python %s <输入正则表达式文件(.re)>' % sys.argv[0])
        exit(-1)
    
    # 对逐个正则表达式打印词法元素
    for regex_no, regex in enumerate(open(REGEX_FNAME, 'rt').read().split('\n')):
        if len(regex) <= 0:
            continue
        
        print('\n------ regex#%d : %s' % (regex_no, regex))
        
        for syntax_item in regex_parser(regex):
            if   type(syntax_item) == int:
                print('字符集  :', charset_bit1_to_str(syntax_item) )
            elif type(syntax_item) == tuple:
                print('计数约束: {%s,%s}' % (str(syntax_item[0]),  '∞' if syntax_item[1]==-1 else str(syntax_item[1])) )
            else:
                print('连词    :', syntax_item )
        
        print('')


