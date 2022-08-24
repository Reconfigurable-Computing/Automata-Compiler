# -*- coding:utf-8 -*-
# Python3

# 功能：正则表达式语法树建立

import sys

from argv_parse import argv_parse
from utils import charset_bit1_to_str
from regex_parser import regex_parser



# 类： SyntaxNode
# 功能： 定义正则表达式短语，构成语法树节点，有三个字段：
#           1. 主语： 字符集 ( int 类型) 或 子表达式集(list)
#           2. 量语： 计数约束，包括最小min和最大max重复次数
#           3. next指针:  指向另一个 SyntaxNode 实例，self 与 next 具有先后关系（匹配完self再匹配next）
# SyntaxNode 会连城一条链，并等效于原正则表达式。
class SyntaxNode():
    
    @property
    def min(self):
        return self._min
    
    @min.setter
    def min(self, value):
        self._min = max(0, value)
    
    @property
    def max(self):
        return self._max
    
    @max.setter
    def max(self, value):
        if value < 0:                   # 
            self._max = -1              # max=-1 代表最大重复无穷次
        else:
            self._max = max(1, value)
    
    @property
    def minmax(self):
        return self.min, self.max
    
    @minmax.setter
    def minmax(self, value):
        self.min, self.max = value
    
    # 构造函数
    def __init__(self, _content=None, _minmax=(1,1)):
        self.content = _content        # 主语： 字符集(int 类型) 或 子表达式集(list类型)
        self.minmax = _minmax          # 量语： 计数约束
        self.next = None               # next 指针
    
    def isolate(self, min=1, max=1):
        return SyntaxNode(self.content, (min, max))
    
    # 判断节点是不是子表达式集
    def is_sub_regexs(self):
        return type(self.content) == list
    
    # 判断节点是不是字符集
    def is_charset(self):
        return type(self.content) == int
    
    # 判断节点的量语是不是平凡的（即 min=max=1）
    def is_plain_minmax(self):
        return self.min == 1 and self.max == 1
    
    # 给节点下面挂一个子表达式，若节点已是子表达式集，就加入其中，或者加入现有子表达式中（是一种化简手段）；
    #                           若节点不是子表达式集，就把他变成子表达式集
    def add_sub_node(self, node):
        if self.is_sub_regexs():             # 若节点已经是子表达式集
            self.content.append(node)
        else:                                # 若节点不是子表达式集
            assert not self.is_charset()     #    ***ASSERT: 正常情况不该把已有的字符集覆盖掉，即只允许 self.content = None
            self.content = [node]
    
    # 返回当前节点的叶子节点（沿着 next 指针摸到叶子节点）
    def seek2leaf(self):
        node = self
        while node.next is not None:
            node = node.next
        return node
    
    # 化简：当前节点若是子表达式集，一些特殊情况下可以化简
    def simplify(self):
        if   self.is_sub_regexs() and len(self.content)==1 and self.is_plain_minmax():                                                                              # 化简情况1：若建立的树是子表达式集但只有一条链，且重复次数是(1,1)
            return self.content[0]                                                                                                                                  #    就把这条链拆出来
        elif self.is_sub_regexs() and len(self.content)==1 and self.content[0].is_plain_minmax() and self.content[0].is_charset() and self.content[0].next is None: # 化简情况2，若建立的树是子表达式集但只有一条链，且该链是字符集且没有 next （链长=1）
            self.content = self.content[0].content                                                                                                                  #    就把这条链拆出来
            return self
        else:
            return self
    
    # 返回字符串表示的量语
    def repr_minmax(self):
        if self.min != self.max:
            return '{%d,%s}' % (self.min, str(self.max) if self.max>=0 else '∞')
        elif self.min != 1:
            return '{%d}' % self.min
        else:
            return ''
    
    def __str__(self):
        if   self.is_sub_regexs():
            return '%d-subs %s' % (len(self.content), self.repr_minmax())
        elif self.is_charset():
            return '%s %s' % (charset_bit1_to_str(self.content), self.repr_minmax())
        else:
            return ''



# 函数： _make_syntax_tree
# 功能： 以 root 为根节点，递归建立语法树
# 参数： syntax_items: 正则表达式语法元素列表（反向）。
#        root: 根节点，代表当前子表达式的根节点
#                        若为 None 代表要建立根节点
#        node: 当前节点，若为 None 代表要建立一个新链
#                        若不为 None ，则它是一个叶子节点 ，新建的节点要挂在 node.next 上，其中 node 是 root.content 下的一个节点
# 返回： 新根节点
def _make_syntax_tree(syntax_items, root=None, node=None):
    
    if bool(syntax_items):
        item = syntax_items.pop()  # 拿出一个语法元素
    else:
        item = ')'
    
    if type(item) == str and item == '(' or type(item) == int:
        if type(item) == int:                                      # 若遇到字符集
            n_node = SyntaxNode(item)                              #    则建立一个简单节点 n_node
        else:                                                      # 若遇到连词 (
            n_node = _make_syntax_tree(syntax_items)               #    建立子表达式集 n_node ，遇到配对的 ) 会递归结束
        
        # 处理计数约束
        while bool(syntax_items):
            minmax = syntax_items.pop()                            # 拿出一个语法元素
            if type(minmax) != tuple:                              # 若不是计数约束
                syntax_items.append(minmax)                        #   退回该语法元素
                break
            n_node = SyntaxNode([n_node], minmax)                  #   套娃一层语法节点，再把新的计数约束加上去
        
        # 若待拼接的 n_node 不是空链，就执行拼接，并摸到拼接后的最后一个节点（叶子节点）
        if n_node is not None:
            if node is None:                                       #    若 node 是 None
                node = n_node                                      #       则新建子链
                if root is None:
                    root = SyntaxNode()
                root.add_sub_node(node)                            #       挂在 root 下面
            else:                                                  #    若 node 已经存在
                node.next = n_node                                 #       挂在 node 后面
            node = n_node.seek2leaf()                              #    摸到后面
        
        # 继续在 node 后面建立语法链
        root = _make_syntax_tree(syntax_items, root, node)
    
    elif type(item) == str:                                        #
        if   item == '|':                                          # 对于连词 |
            root = _make_syntax_tree(syntax_items, root)
        elif item == ')':                                          # 对于连词 )
            pass
        else:
            raise Exception('undefined item from regex_parser')
    
    elif type(item) == tuple:                                      # 对于本不该在此出现的计数约束
        root = _make_syntax_tree(syntax_items, root, node)         #   忽略它，继续在 node 后面建立语法链
    
    else:
        raise Exception('undefined item from regex_parser')
    
    return None if root is None else root.simplify()               #     化简 并 返回根节点



# 函数： build_syntax_tree
# 功能： 以 regex(str) 为正则表达式，建立语法树
# 返回： 语法树的根节点 root
def build_syntax_tree(regex):
    syntax_items = [syntax_item for syntax_item in regex_parser(regex)]
    syntax_items.reverse()
    root = _make_syntax_tree(syntax_items)
    assert not root is None, 'empty regex'
    return root



# 函数： show_syntax_tree
# 功能： 打印以 node 为根节点的语法树
#        兼具语法树检查的工程（通过 assert 检查正常算法下不会产生的问题）
def show_syntax_tree(node, depth=0, number=0):
    assert not node is None                                       # ***ASSERT: 正常的算法是不会导致 node=None 的
    number_marker = ' %2d:' % number if number > 0 else '    '
    while not node is None:
        assert node.is_sub_regexs() or node.is_charset()          # ***ASSERT: 正常的算法下, node 要么是 子表达式集，要么是 字符集
        print('    ' * depth, end=number_marker)
        number_marker = '    '
        print(node)
        if node.is_sub_regexs():
            for ii, subnode in enumerate(node.content):
                show_syntax_tree(subnode, depth+1, ii+1)
        node = node.next




if __name__ == '__main__':
    
    # 解析命令行参数
    (REGEX_FNAME,), _ = argv_parse(['.re'])
    if REGEX_FNAME == '':
        print('Usage: python %s <输入正则表达式文件(.re)>' % sys.argv[0])
        exit(-1)
    
    # 对逐个正则表达式打印语法树
    for regex_no, regex in enumerate(open(REGEX_FNAME, 'rt').read().split('\n')):
        if len(regex) <= 0:
            continue
        
        print('')
        print('------ regex#%d : %s' % (regex_no, regex))
        
        root = build_syntax_tree(regex)
        show_syntax_tree(root)
        print('')






