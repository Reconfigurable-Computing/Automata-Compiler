# -*- coding:utf-8 -*-
# Python3
# 功能: 建立 NFA

import sys
import os
from time import time
from graphviz import Digraph

from argv_parse import argv_parse
from utils import bit1_from_list, bit1_from_range, bit1_count, bit1_pos_yield, bit1_or, bit1_and, bit1_exclude, bit1_include_truely, bit1_include, CHARSET_SIZE, CHARSET_FULL, CHARSET_BORDER, CHARSET_DOT, CHARSET_WORDS, CHARSET_DIGITS, CHARSET_SPACES, charset_bit1_to_str
from dual_key_dict import dual_key_dict
from regex_tree import build_syntax_tree



class NFA():
    
    # 功能： 构造函数，以字符串数组 regex_strings 作为正则表达式集，建立 NFA ，并移除所有 ε 边
    def __init__(self, regex_strings):
        self.T = dual_key_dict()               # NFA 的转换边集合
        self.A = dual_key_dict()               # NFA 的接受状态对应关系集合
        
        self.addT(0, 0, CHARSET_FULL)          # 给起始状态建立一个自环，包含所有字符
        
        n = 0                                  # 状态号，从  0 开始向正整数方向增大
        self.n_accept = 0                      # 接受号，从 -1 开始向负整数方向减小
        
        # 把每个 regex 转成语法树，加入 NFA
        synodes = []                           # 保存所有 RegexSet（未展开的正则表达式集）   结构： [(int sn, int en, SyntaxNode synode), ...]
        for regex in regex_strings:
            n += 1
            self.n_accept -= 1
            synodes.append((0, n, build_syntax_tree(regex)))
            self.A[(n, self.n_accept)] = 'ε'
        
        E_tran = dual_key_dict()               # NFA 的 ε 边集合（临时，后续就消除掉了）
        
        while bool(synodes):                                                 # 遍历所有 RegexSet 的转换（语法节点）
            sn, en, synode = synodes.pop()                                   #   拿到一个语法节点，它从 sn 转换到 en
            if synode.next is not None:                                      #   如果该语法节点有后继节点
                n += 1                                                       #     新的中间状态 n
                synodes.append((n, en, synode.next))                         #     新建边 n→en
                en = n                                                       #     en←n
            min, max = synode.minmax                                         #   拿到语法节点的重复次数 (min, max)
            if   min <= 2 and max < 0:                                       #   min∈[1,2], max=∞ ，则直接展开
                n += 1                                                       #     新的中间状态 n
                if min == 2:
                    synodes.append((sn,  n, synode.isolate()))
                elif sn != n:
                    E_tran[(sn, n)] = 'ε'
                if min >= 1:
                    synodes.append(( n, en, synode.isolate()))
                elif n != en:
                    E_tran[(n, en)] = 'ε'
                synodes.append(( n,  n, synode.isolate()))                   #
            elif min > 1:                                                    #   min∈[2,∞) ，则拆出一个
                n += 1                                                       #     新的中间状态 dn
                synodes.append((sn,  n, synode.isolate(min-1, max-1)))       #     重复次数-1
                synodes.append(( n, en, synode.isolate()))                   #     拆出来的状态
            elif min == 0:                                                   #   min=0, max<∞ ，则拆出来该ε边
                synodes.append((sn, en, synode.isolate(min+1, max)))         # 
                if sn != en:
                    E_tran[(sn, en)] = 'ε'                                   #     拆出来的ε边
            elif max >= 2:                                                   #   min=1, max∈[2,∞) ，则拆出来一个边
                synodes.append((sn, en, synode.isolate(min+1, max)))         # 
                synodes.append((sn, en, synode.isolate()))                   # 
            else:                                                            #   min=max=1
                if synode.is_sub_regexs():                                   #     synode 是子表达式集
                    for sub_synode in synode.content:                        #       拆出其中的子表达式集
                        synodes.append((sn, en, sub_synode))                 #
                else:                                                        #     synode 是一个单字符转换边
                    self.addT(sn, en, synode.content)                        #       之间添加简单的转换边
        
        # 移除所有 ε 边
        while bool(E_tran):                             # 只要 Te 不空
            sn, en, _ = E_tran.pop_one_pair()           #   就拿出其中一个
                
            # 把 en 的所有出边继承给 sn
            for n, cset in self.T.keya_dict(en).items():
                self.addT(sn, n, cset)
            for an      in self.A.keya_dict(en):
                self.A[(sn, an)] = 'ε'
            for n       in E_tran.keya_dict(en):
                if sn != n:
                    E_tran[(sn, n)] = 'ε'
            
            # 如果状态 en 没有出边且不是接受状态，或没有入边，就删除 en
            if not ( bool(self.T.keya_dict(en)) or bool(E_tran.keya_dict(en)) or bool(self.A.keya_dict(en)) ) or not ( bool(self.T.keyb_dict(en)) or bool(E_tran.keyb_dict(en)) ):
                self.T.rm_key_both(en)
                E_tran.rm_key_both(en)
                self.A.rm_keya(en)
    
    
    
    # 功能 ： 获取一个集合（set类型），里面包含 NFA 的所有状态号
    def all_stats(self):
        return self.T.all_keyb()
    
    
    
    # 功能：判断是不是 homo NFA
    def is_homo_nfa(self):
        for en in self.T.all_keyb():                       # 对于任意的状态 en
            cset_ref = None
            for sn, cset in self.T.keyb_dict(en).items():  #   对于到达 en 的字符集 cset
                if cset_ref is None:
                    cset_ref = cset
                elif cset_ref != cset:                     #     如果有字符集不同
                    return False                           #       就不是 homo NFA
        return True
    
    
    
    # 返回  ： 字符串形式的对象，一般用于打印
    def __str__(self):
        return '<NFA: %d rules, %d stats, %d trans, homo=%s>' % (-self.n_accept, len(self.all_stats()), len(self.T), str(self.is_homo_nfa()))
    
    
    
    # 返回  ： NFA 的可视化图 (Digraph 类的对象)
    def get_digraph(self):
        digraph = Digraph()
        digraph.attr('node', style='filled', color='lightblue2', shape='circle')
        
        digraph.node(str(0), color='red', shape='circle')                          # 起始状态标为红色
        
        for sn in self.T.all_keya():
            for en, cset in self.T.keya_dict(sn).items():
                digraph.edge(str(sn), str(en), charset_bit1_to_str(cset).replace('\\','\\\\') )    # 这里要把 \ 字符替换成 \\ ，因为 Digraph 库会把 \ 字符本身当作转义字符（又转义了一次，我认为这是它这个库的bug）
        
        for sn in self.A.all_keya():
            for en in self.A.keya_dict(sn):
                digraph.edge(str(sn), str(en), '')
                digraph.node(str(en), color='green', shape='doublecircle')         # 接受状态标为绿色
        
        return digraph
    
    
    
    # 功能： 自检，包含一些 assert ，为了检查算法是否可能写错
    def self_check(self):
        self.A.self_check(), 'nfa.A is not complete'
        self.T.self_check(), 'nfa.T is not complete'
        
        assert self.A.all_keyb() == set(list(range(self.n_accept, 0))), 'some accept number is deleted'      # 所有接受号都要是可达的，不能在化简中把一些接受号消除掉了
        
        # 检查接受规则
        for sn, an, item in self.A.tolist():
            assert sn >= 0 and an < 0
            assert item == 'ε'
        
        # 检查转换边
        for sn, en, cset in self.T.tolist():
            assert sn >= 0 and en >= 0
            assert type(cset) == int 
            assert cset != 0                    # 所有边都不能是空字符集
        
        # 检查状态
        for n in self.all_stats():
            # 检查孤岛
            assert bool(self.T.keya_dict(n)) or bool(self.A.keya_dict(n)) , 'there exist islands in NFA!'    #   n 必须有出边或是接受状态
            assert bool(self.T.keyb_dict(n)) , 'there exist islands in NFA!'                                 #   n 必须有入边
    
    
    
    # 作用  ： 在 sn 到 en 之间添加字符。如果尚没有边，就添加边，如果已经有边，就把字符添加进该边的字符集
    # 参数  :  sn, en : 任意状态
    #          cset: 必须是 int 类，也即字符集
    def addT(self, sn:int, en:int, cset:int):
        if (sn, en) in self.T:                                      # 如果已经有边
            self.T[(sn, en)] = bit1_or(self.T[(sn, en)], cset)      # 就把字符添加进该边的字符集
        else:                                                       # 如果尚没有边
            self.T[(sn, en)] = cset                                 # 就添加边
    
    
    
    # 功能  ： 删除状态 n
    # 参数  ： n: 状态号
    def remove(self, n:int):
        self.T.rm_key_both(n)
        self.A.rm_keya(n)
    
    
    
    # 功能  ： 尝试合并状态 n1, n2
    #          如果它们有相同的出边 ，则把 n2 合并到 n1 （删除 n2，保留 n1 ）
    # 适用于： ε-NFA, NFA
    # 返回  ： 成功 True, 失败 False
    def merge_when_same_out(self, n1:int, n2:int):
        if n2 != n1:
            if self.A.keya_dict(n1) == self.A.keya_dict(n2) and self.T.keya_dict(n1) == self.T.keya_dict(n2) :  # n2 和 n1 是否有完全相同的出边？
                
                # 如果到达 n1 和 n2 的边的字符集不一样，就不允许合并，避免破坏 homo-NFA 结构
                for n1s, n1s_cset in self.T.keyb_dict(n1).items():
                    for n2s, n2s_cset in self.T.keyb_dict(n2).items():
                        if n1s_cset != n2s_cset:
                            return False
                
                #   将 n2 的入边继承给 n1
                for n, cset in self.T.keyb_dict(n2).items():
                    self.addT(n, n1, cset)
                
                self.remove(n2)
                return True
        return False
    
    
    
    # 功能  ： 尝试合并状态 n1, n2
    #          如果它们有相同的入边 ，则把 n2 合并到 n1 （删除 n2，保留 n1 ）
    # 适用于： ε-NFA, NFA
    # 返回  ： 成功 True, 失败 False
    def merge_when_same_in(self, n1:int, n2:int):
        if n2 != n1:
            all2n1 = dict(self.T.keyb_dict(n1))          # 获得 n1 的所有普通入边
            all2n2 = dict(self.T.keyb_dict(n2))          # 获得 n2 的所有普通入边
            
            if n2 in all2n2:                             # 如果有 n1→n1
                cset = all2n2.pop(n2)                    #   n2→n1 = n1→n1 ，同时删去 n1→n1
                if n1 in all2n2:
                    all2n2[n1] = bit1_or(all2n2[n1], cset)
                else:
                    all2n2[n1] = cset
            
            if n2 in all2n1:                             # 如果有 n1→n2
                cset = all2n1.pop(n2)                    #   n2→n2 = n1→n2 ，同时删去 n1→n2
                if n1 in all2n1:
                    all2n1[n1] = bit1_or(all2n1[n1], cset)
                else:
                    all2n1[n1] = cset
            
            if all2n1 == all2n2:    # n2 和 n1 是否有完全相同的入边？
                
                #   将 n2 的出边和接受状态继承给 n1
                for n, cset in self.T.keya_dict(n2).items():
                    self.addT(n1, n, cset)
                for an in self.A.keya_dict(n2):
                    self.A[(n1, an)] = 'ε'
                
                self.remove(n2)
                return True
        return False
    
    
    
    # 功能： 化简 NFA (目前尚未化成最简的形式，但不一定要化成最简）
    # 注意： 必须对调用 remove_epsilon 后的 NFA 使用
    def simplify(self):
        retry = True
        while retry:
            retry = False
            for sn in self.T.all_keya():                                   # 对于所有出发状态 sn
                all4n = self.T.keya_dict(sn)
                for n1 in all4n:                                           # n1 和 n2 都来自 sn
                    for n2 in all4n:
                        if n1 < n2 and self.merge_when_same_in(n1, n2):    # 如果 n1 和 n2 有相同的入边
                            retry = True
        retry = True
        while retry:
            retry = False
            for en in self.A.all_keyb():                                   # 对于所有接受号 en
                all2n = self.A.keyb_dict(en)
                for n1 in all2n:                                           # n1 和 n2 都会到达 en
                    for n2 in all2n:
                        if n1 < n2 and self.merge_when_same_out(n1, n2):
                            retry = True
        retry = True
        while retry:
            retry = False
            for en in self.T.all_keyb():                                   # 对于所有到达状态 en
                all2n = self.T.keyb_dict(en)
                for n1 in all2n:                                           # n1 和 n2 都会到达 en
                    for n2 in all2n:
                        if n1 < n2 and self.merge_when_same_out(n1, n2):
                            retry = True
    
    
    
    # 功能： 转 homo-NFA
    def to_homo_nfa(self):
        nn = max(self.all_stats())
        retry = True
        while retry:
            retry = False
            for en in self.T.all_keyb():                                     # 对于所有到达状态 en
                csets = set()
                for sn, cset in self.T.keyb_dict(en).items():
                    if bool(csets) and cset not in csets:
                        nn += 1                                              # 新建状态
                        self.addT(sn, nn, self.T.pop_pair((sn, en)))
                        for een, een_cset in self.T.keya_dict(en).items():
                            self.addT(nn, een, een_cset)
                        for an in self.A.keya_dict(en):
                            self.A[(nn, an)] = 'ε'
                        retry = True
                    csets.add(cset)
    
    
    
    # 功能： 重组织状态号，按广度优先遍历来走
    def reorganize(self):
        subset = set()
        tmpset = [0]
        
        new_n = 0
        rename_dict = dict()
        
        # 广度优先遍历，同时分配重命名号
        while bool(tmpset):
            sn = tmpset.pop(0)
            if sn not in subset:
                subset.add(sn)                             # 子集新加入 sn
                rename_dict[sn] = new_n
                new_n += 1
                for en in self.T.keya_dict(sn):            # 对于所有 sn→en
                    if en not in subset:                   #   如果 en 不在子集中
                        tmpset.append(en)                  #     tmpset |= en
        
        rebuild_T = dual_key_dict()
        rebuild_A = dual_key_dict()
        
        # remap old number to new number
        for sn, en, cset in self.T.tolist():
            rebuild_T[(rename_dict[sn], rename_dict[en])] = cset
        
        for sn, an, _ in self.A.tolist():
            rebuild_A[(rename_dict[sn], an)] = 'ε'
        
        self.T = rebuild_T
        self.A = rebuild_A




# 函数 : 生成 homo-NFA
# 如果不在乎 NFA 的细节，而是想一步生成化简的 homo-NFA ，就用这个函数
def genHomoNFAfromRegex(regexs):
    nfa = NFA(regexs)
    nfa.simplify()
    nfa.to_homo_nfa()
    nfa.simplify()
    nfa.reorganize()
    nfa.self_check()   ####
    return nfa





# 主函数
# 从命令行参数读入文件名，从文件中读出正则表达式集（一行一条），转换成 NFA-ε ， 然后转换成 NFA，然后化简
if __name__ == '__main__':
    
    # 解析命令行参数
    (REGEX_FNAME, DRAW_FNAME), _ = argv_parse(['.re', '.gv'])
    if REGEX_FNAME == '':
        print('Usage: python %s <输入正则表达式文件(.re)> [输出绘图文件(.gv)]' % sys.argv[0])
        exit(-1)
    
    # 读取文件，得到一行一行的 regex ，去重 ， 按 ASCII 编码排序
    regex_strings = list( set( filter( lambda regex:len(regex)>0 , open(REGEX_FNAME, 'rt').read().split('\n') ) ) )
    regex_strings.sort()
    print('total %d regexs (after remove duplicate)\n' % len(regex_strings))
    
    # 起始时间
    stime = int(round(time()*1000))
    
    # 创建 NFA 对象
    nfa = NFA(regex_strings)
    print('[%12d ms]  ' % (int(round(time()*1000)) - stime) , 'build NFA   ' , nfa )
    nfa.self_check()
    
    # 化简 NFA
    nfa.simplify()
    print('[%12d ms]  ' % (int(round(time()*1000)) - stime) , 'simplify    ' , nfa )
    nfa.self_check()
    
    # 转 homo NFA
    nfa.to_homo_nfa()
    print('[%12d ms]  ' % (int(round(time()*1000)) - stime) , 'to_homo     ' , nfa )
    nfa.self_check()
    
    # 转为 homo NFA 后，再次化简 NFA（这一步一般不会化简太多，耗时也不长）
    nfa.simplify()
    print('[%12d ms]  ' % (int(round(time()*1000)) - stime) , 'simplify    ' , nfa )
    nfa.self_check()
    
    # 重组织 NFA（按广度优先遍历顺序重新给状态编号）
    nfa.reorganize()
    print('[%12d ms]  ' % (int(round(time()*1000)) - stime) , 'reorganize  ' , nfa )
    nfa.self_check()
    
    # NFA 绘图
    if DRAW_FNAME != '':
        nfa.get_digraph().render(DRAW_FNAME, view=False)
        os.remove(DRAW_FNAME)






