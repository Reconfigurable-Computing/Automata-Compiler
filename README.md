# Automata Compiler &  Automata Processor's HDL Generator

(updating in progress ...)

本库持续更新，最终的目标是：

- 功能完善、代码易读的**自动机编译器**：从正则表达式集开始，能生成各种典型的自动机模型，用SOTA的方法对它们压缩。最后能绘图、导出文本格式的自动机结构描述文件。
- **自动机处理器的HDL代码生成器**：生成低资源量、高性能的自动机处理器，可部署于 FPGA 。



## 安装依赖

本库使用 Python 3 编写，目前依赖于：

- Python 3.9
- Graphviz 2.47



## 当前版本(2020/8/24)

### 一、提供 同构NFA 的生成和绘图功能：

例如运行以下命令，意为用正则表达式文件 `rules2/test1.re` 生成 同构NFA ，并绘图生成 `test1.gv.pdf` 。

```powershell
python nfa.py rules2/test1.re test1.gv
```

> 注：如果不加 xxx.gv 参数，代表只生成NFA，不绘图。大型NFA的生成效率很高，但绘图非常慢。绘图仅仅适用于小型NFA

### 二、提供 multi-DFA 探索功能

例如运行以下命令，意为用正则表达式文件 `rules/bro227.re` 探索 multi-DFA 方案。每个DFA的状态数不超过它对应的NFA的状态数的2.5倍，且 multi-DFA 组数最多为 2 。

```powershell
python dfa_multi.py rules/bro227.re 2.5 2
```

当程序探索出 multi-DFA 方案后，会报告结果如下，我们可以看到产生了两个分组，并报告了每个分组对应的正则表达式数量、 NFA 状态数、和转化为 DFA 的状态数。另外，还有少数的正则表达式被放在了额外的 NFA group 中，意为这些正则表达式生成DFA后会发生状态爆炸，代价较大，建议使用 NFA 处理。

```
-------- summary : 2 groups --------
DFA group#0:  regex#169  NFA#S=1526  DFA#S=3777
DFA group#1:  regex#47  NFA#S=626  DFA#S=1518
DFA groups total:  regex#216  NFA#S=2152  DFA#S=5295
NFA group:  <NFA: 11 rules, 968 stats, 1233 trans, homo=True>
```

最后，程序会提示我们输入一个输出文件名，我们输入后，以上分组方案会被保存下来：

```
请指定输出目录名（回车放弃）：bro227
```

