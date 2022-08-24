
import sys


# 函数 : argv_parse
# 功能 : 命令行参数解析，按后缀筛选字符串，同时保存数字到数组
def argv_parse(strs_suffix, sys_argv = ''):
    if sys_argv == '':
        sys_argv = sys.argv
    argv_strs = [''] * len(strs_suffix)
    argv_nums = []
    for argv in sys_argv:
        try:
            num = float(argv)
            argv_nums.append(num)
            continue
        except:
            pass
        for i_suffix, suffix in enumerate(strs_suffix):
            if argv.endswith(suffix):
                argv_strs[i_suffix] = argv
                continue
    return argv_strs, argv_nums
