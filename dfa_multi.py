# -*- coding:utf-8 -*-
# Python3

import os
import sys

from argv_parse import argv_parse
from nfa import NFA, genHomoNFAfromRegex
from nfa_homo_calculation import get_NFA_homo_LUT, get_next_mask



# 转 DFA ， 返回 DFA 状态数
# 在状态数>max_dfa_stat 时放弃，避免浪费过多的计算时间
def dfa_stats_count(NFAhomo_fore_net, NFAhomo_char_mask, max_dfa_stat=-1):
    St = {1}
    So = set()
    while bool(St):
        s = St.pop()
        So.add(s)
        if max_dfa_stat >= 0 and len(So) > max_dfa_stat:
            return False, len(So)
        tmask = get_next_mask(s, NFAhomo_fore_net)
        for cmask in NFAhomo_char_mask:
            t = tmask & cmask
            if not t in So:
                St.add(t)
    return True, len(So)





# regex 分组，每组一个 DFA ，剩下的放到 NFA
def dfa_multi(regexs, DFA_GROUP_MAX, DFA_COEF):
    regexs.sort()
    
    # 筛选出值得纳入 DFA 的 regex，尽量把多个 regex 合并成一个 DFA -------------------------------------------------------------------------------------------------------------------------------
    groups = [[0,0,[]],]
    group_nfa = []
    for regex_ii, regex in enumerate(regexs):                             # 对于每项 regex
        for gi in range(len(groups)):                                     # 对于每个 group
            nfa = genHomoNFAfromRegex( groups[gi][-1] + [regex] )
            NFA_N, NFAhomo_fore_net, _, NFAhomo_char_mask, _, _ = get_NFA_homo_LUT(nfa)
            ret, DFA_N = dfa_stats_count(NFAhomo_fore_net, NFAhomo_char_mask, max_dfa_stat=int(NFA_N*DFA_COEF) )
            if ret:
                print('regex#%d->DFA,  NFA#S=%d  DFA#S=%d' % (regex_ii, NFA_N, DFA_N) )
                _, _, group = groups.pop(gi)
                group.append(regex)
                groups.insert(0, [NFA_N, DFA_N, group])
                if len(groups[-1][-1]) > 0:
                    groups.append([0,0,[]])
                break
        else:
            group_nfa.append(regex)
    
    if len(groups[-1][-1]) <= 0:
        groups.pop()
    
    
    # 保留前 DFA_GROUP_MAX 个最大的 DFA group ，其余的小 DFA group 扔回 NFA
    groups.sort(key=lambda x:x[0], reverse=True)                  # 按照每组包含的 NFA 状态数进行排序
    for i in range(len(groups)-DFA_GROUP_MAX):                    # 要删除的 group 有 len(groups)-DFA_GROUP_MAX 组
        NFA_N, DFA_N, group = groups.pop()
        group_nfa += group
        print('move a DFA group to NFA group,  regex#%d  NFA#S=%d  DFA#S=%d' % (len(group), NFA_N, DFA_N) )
        
    
    print('-------- summary : %d groups --------' % len(groups) )
    # 打印 DFA groups 信息 -------------------------------------------------------------------------------------------------------------------------------
    total_regex_n, total_nfa_n, total_dfa_n = 0, 0, 0
    for gi, (NFA_N, DFA_N, group) in enumerate(groups):
        total_regex_n += len(group)
        total_nfa_n   += NFA_N
        total_dfa_n   += DFA_N
        print('DFA group#%d:  regex#%d  NFA#S=%d  DFA#S=%d' % (gi, len(group), NFA_N, DFA_N) )
    print('DFA groups total:  regex#%d  NFA#S=%d  DFA#S=%d' % (total_regex_n, total_nfa_n, total_dfa_n) )
    
    
    # 删除 DFA groups 的附加信息 -------------------------------------------------------------------------------------------------------------------------------
    for gi in range(len(groups)):
        groups[gi] = groups[gi][-1]
    
    
    # 整合 NFA ；统计数据，打印 -------------------------------------------------------------------------------------------------------------------------------
    group_nfa.sort()
    nfa = genHomoNFAfromRegex( group_nfa )
    print('NFA group: ' , nfa)
    
    return groups, group_nfa






if __name__ == '__main__':

    # 解析命令行参数 -------------------------------------------------------------------------------------------------------------------------------
    (REGEX_FNAME,), ARGV_NUMS = argv_parse(['.re'])
    if REGEX_FNAME == '' or len(ARGV_NUMS) != 2:
        print('Usage: python %s <输入正则表达式文件(.re)> <最大DFA状态数/NFA状态数> <最大DFA组数>' % sys.argv[0])
        exit(-1)
    DFA_COEF, DFA_GROUP_MAX = ARGV_NUMS
    DFA_GROUP_MAX = int(DFA_GROUP_MAX)
    
    
    # 读取文件，得到一行一行的 regex ，去重，排序 -------------------------------------------------------------------------------------------------------------------------------
    regexs = list( set( filter( lambda regex:len(regex)>0 , open(REGEX_FNAME, 'rt').read().split('\n') ) ) )
    print('%d regexs (after remove duplicate)\n' % len(regexs))
    
    
    # DFA 分组 -------------------------------------------------------------------------------------------------------------------------------
    groups, group_nfa = dfa_multi(regexs, DFA_GROUP_MAX, DFA_COEF)
    
    
    # 创建输出文件夹 -------------------------------------------------------------------------------------------------------------------------------
    while True:
        SAVE_DIR = input('请指定输出目录名（回车放弃）：')
        if SAVE_DIR == '':
            if 'y' == input('确认放弃？(y|n)：'):
                exit(0)
        elif os.path.isdir(SAVE_DIR):
            print('目录已存在，请重新指定')
        else:
            try:
                os.mkdir(SAVE_DIR)
            except:
                continue
            break
    
    # 保存 -------------------------------------------------------------------------------------------------------------------------------
    for gi, group in enumerate(groups):
        FNAME = SAVE_DIR + os.path.sep + ('dfa%d.re' % gi)                 # 文件名: dfa%d.re
        open(FNAME, 'wt').writelines( [regex+'\n' for regex in group] )
    
    FNAME = SAVE_DIR + os.path.sep + ('nfa.re')                            # 文件名: nfa.re
    open(FNAME, 'wt').writelines( [regex+'\n' for regex in group_nfa] )


