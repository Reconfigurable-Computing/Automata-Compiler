# -*- coding:utf-8 -*-
# Python3

# 本代码文件提供 homo-NFA 的一些快速演算的函数集
# 用整数表示 NFA 的一个子集：
#     每个bit代表一个NFA状态，最低bit代表0号状态，第1bit代表1号状态，……
#     bit=0代表该NFA状态不激活，bit=1代表激活
# 则 NFA 的相关计算可以快速用查找表和位运算来实现


from utils import CHARSET_SIZE
from nfa import NFA



# 生成 homo-NFA 的快速查询表：
# 参数：
#     nfa: 必须是 class NFA
# 返回：
#     NFA_N: NFA 状态数
#     NFAhomo_fore_net : 正向转换查询表，NFAhomo_fore_net[n] = 状态n的下一个状态的集合
#     NFAhomo_back_net : 反向转换查询表，NFAhomo_back_net[n] = 状态n的上一个状态的集合
#     NFAhomo_char_mask: 字符激活查询表，NFAhomo_char_mask[c]= 字符c会到达的状态的集合 ，注意：homo-NFA 的任意状态的所有入边都有相同的字符集，即对于 n1, n2 ，若 δ(n1,c1)=δ(n2,c2) , 则 c1=c2
#     NFAhomo_csets    : 
#     NFAhomo_accept_net:
def get_NFA_homo_LUT(nfa):
    assert nfa.is_homo_nfa()                # 必须是 homo-NFA 才能执行该算法
    
    NFA_N = len(nfa.all_stats())            # NFA 状态数
    
    NFAhomo_fore_net = [0] * NFA_N
    NFAhomo_back_net = [0] * NFA_N
    for sn in nfa.T.all_keya():
        for en in nfa.T.keya_dict(sn):
            NFAhomo_fore_net[sn] |= (1<<en)
            NFAhomo_back_net[en] |= (1<<sn)
    
    NFAhomo_accept_net = [0] * NFA_N
    for sn in nfa.A.all_keya():
        for en in nfa.A.keya_dict(sn):
            NFAhomo_accept_net[sn] |= (1<<(-en))
    
    NFAhomo_char_mask = [0] * CHARSET_SIZE
    NFAhomo_csets = [0] * NFA_N
    for en in nfa.T.all_keyb():
        for _, cset in nfa.T.keyb_dict(en).items():
            NFAhomo_csets[en] = cset
            for ci in range(CHARSET_SIZE):
                if cset & (1<<ci):
                    NFAhomo_char_mask[ci] |= (1<<en)
            break
    
    return NFA_N, NFAhomo_fore_net, NFAhomo_back_net, NFAhomo_char_mask, NFAhomo_csets, NFAhomo_accept_net




# 函数: get_NFA_homo_accpet_mask
def get_NFA_homo_accpet_mask(nfa):
    NFAhomo_accept_mask = 0
    for sn in nfa.A.all_keya():
        NFAhomo_accept_mask |= (1<<sn)
    return NFAhomo_accept_mask



# 计算 NFA 子集 nset 的单步传递，
# 当 NFAhomo_net 是 NFAhomo_fore_net 时，返回一个 NFA 状态集的"下一个"子集
# 当 NFAhomo_net 是 NFAhomo_back_net 时，返回一个 NFA 状态集的"上一个"子集
def get_next_mask(nset, NFAhomo_net):
    s_next_mask = 0
    n = 0
    while nset != 0:
        if (nset & 1):
            s_next_mask |= NFAhomo_net[n]
        nset >>= 1
        n += 1
    return s_next_mask



# 得到一个 NFA 子集 nset 的封闭集：不断把 nset 的上一个、上上一个、上上上一个…… 的 NFA 状态加入 nset ，直到没有更多的状态加入为止，也就是让 nset 变得封闭，只有出边，没有入边
def get_close_by_expand(nset, NFAhomo_back_net):
    nset_old = 0
    while nset != nset_old:
        nset_old = nset
        nset |= get_next_mask(nset_old, NFAhomo_back_net)
    return nset



# 判断一个 NFA 子集 nset 是不是封闭子图
# 封闭子图的定义是：只能有出边，不能有入边
def is_close(nset, NFAhomo_back_net):
    nset_previous = get_next_mask(nset, NFAhomo_back_net)
    return (nset | nset_previous) == nset



