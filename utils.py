# -*- coding:utf-8 -*-
# Python3
# 功能: 一些工具函数

from functools import reduce


# 函数: assert_positive_int
# 功能: 断言参数是非负整数
# 参数: 
#    v: 数
def assert_positive_int(v):
    assert type(v) == int
    assert v >= 0


# 函数: bit1_from_list
# 功能: 构造一个非负整数，它的第 i 个 bit=1，其余bit=0 。其中 i 来自一个数组
# 参数: 
#    int_list: 包含 i 的数组
# 返回:
#    整数
def bit1_from_list(int_list):
    return reduce(lambda x,y:x|y, [1<<i for i in int_list])


# 函数: bit1_from_range
# 功能: 构造一个非负整数，它的第 i 个(包含)到第 j 个(包含)的bit=1，其余bit=0
# 参数: 
#    i: 整数
#    j: 整数
# 返回:
#    整数
def bit1_from_range(i, j):
    if i > j:
        i, j = j, i
    return bit1_from_list(list(range(i, j+1)))


# 函数: bit1_count
# 功能: 计算一个非负整数的二进制表示有多少个 bit=1
# 参数: 
#    v: 整数
# 返回:
#    整数
def bit1_count(v):
    assert_positive_int(v)
    cnt = 0
    while v != 0:
        if (v & 1):
            cnt += 1
        v >>= 1
    return cnt


# 迭代函数: bit1_pos_yield
# 功能: 返回一个非负整数的二进制表示的所有 bit=1 的位置序号
# 参数: 
#    v: 整数
# yield:
#    整数
# 举例:
#    for n in bit1_pos_yield(v):
#        print('v的第%d个bit=1' % n)
def bit1_pos_yield(v):
    assert_positive_int(v)
    cnt = 0
    while v > 0:                                                                      
        if v & 1:
            yield cnt
        v >>= 1
        cnt += 1


# 函数: bit1_or
# 功能: 两个非负整数按位或，得到整数
# 参数: 
#    v1: 整数
#    v2: 整数
# 返回:
#    整数
def bit1_or(v1, v2):
    assert_positive_int(v1)
    assert_positive_int(v2)
    return v1 | v2


# 函数: bit1_and
# 功能: 两个非负整数按位与，得到整数
# 参数: 
#    v1: 整数
#    v2: 整数
# 返回:
#    整数
def bit1_and(v1, v2):
    assert_positive_int(v1)
    assert_positive_int(v2)
    return v1 & v2


# 函数: bit1_exclude
# 功能: 两个非负整数按位差（差集），得到整数
# 参数: 
#    v1: 整数
#    v2: 整数
# 返回:
#    整数
def bit1_exclude(v1, v2):
    assert_positive_int(v1)
    assert_positive_int(v2)
    return v1 & (~v2)


# 函数: bit1_include_truely
# 功能: 输入两个非负整数 v1, v2 ，判断 v1 的bit=1的位是否真包含 v2 的bit=1的位
# 参数: 
#    v1: 整数
#    v2: 整数
# 返回:
#    整数
def bit1_include_truely(v1, v2):
    assert_positive_int(v1)
    assert_positive_int(v2)
    return bool(v1 & (~v2))


# 函数: bit1_include
# 功能: 输入两个非负整数 v1, v2 ，判断 v1 的bit=1的位是否包含 v2 的bit=1的位
# 参数: 
#    v1: 整数
#    v2: 整数
# 返回:
#    整数
def bit1_include(v1, v2):
    assert_positive_int(v1)
    assert_positive_int(v2)
    return (v1 | v2) == v1










# 函数: is_ascii_printable
# 功能: 判断一个字符串是不是 ASCII 可打印的
def is_ascii_printable(string):
    for c in string:
        if not c in ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~' :
            return False
    return True



###################################################################################################################################################################
# 用非负整数表示字符集，第i个bit=1代表 ASCII码=i 的字符在集合中
###################################################################################################################################################################

CHARSET_SIZE = 256 + 1        # 字符总数: total 256 ASCII chars + string border (＾)

CHARSET_FULL   = bit1_from_range(0, CHARSET_SIZE-1)                                                           # 全字符集
CHARSET_BORDER = bit1_from_list([CHARSET_SIZE-1])                                                             # 只包含边界符 (＾) 的字符集
CHARSET_DOT    = bit1_exclude(CHARSET_FULL, CHARSET_BORDER)                                                   # 通配(.) 包含除了 边界符 (＾) 外的所有字符
CHARSET_WORDS  = bit1_from_list(map(ord, 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789_'))  # 包含所有字母+_的字符集，对应正则表达式中的 \w
CHARSET_DIGITS = bit1_from_list(map(ord, '0123456789'))                                                       # 包含所有数字的字符集，对应正则表达式中的 \d
CHARSET_SPACES = bit1_from_list(map(ord, ' \f\n\r\t\v'))                                                      # 包含所有空字符的字符集，对应正则表达式中的 \s

# 函数: charset_bit1_to_str
# 功能: 用非负整数表示字符集，bit=1的位置代表对应的 ASCII 码的字符在集合中。打印该字符集
def charset_bit1_to_str(v):
    SHOW_CNT_MAX = 5
    string = ''
    if bit1_and(v, CHARSET_BORDER):
        string += '^'
    v = bit1_and(v, CHARSET_DOT)
    cnt = bit1_count(v)
    if   cnt == 0:
        return string
    elif cnt == CHARSET_SIZE-1:
        return string + '.'
    elif cnt >= (CHARSET_SIZE-1-SHOW_CNT_MAX):
        v = bit1_exclude(CHARSET_DOT, v)
        string += '[^'
    else:
        string += '['
    show_cnt = 0
    for n in bit1_pos_yield(v):
        if show_cnt >= SHOW_CNT_MAX:
            return string + (']#%d' % cnt)
        c = chr(n)
        if is_ascii_printable(c):
            string += c
        else:
            string += c.__repr__()[1:-1]
        show_cnt += 1
    return string + ']'





