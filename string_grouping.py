# -*- coding:utf-8 -*-
# Python3



def string_similarity(str1, str2):
    length = min(len(str1), len(str2))
    for ii in range(length):
        if str1[ii] != str2[ii]:
            return ii
    return length



def string_div2(strings, min_size):     # return: gsmall, glarge
    assert 2 * min_size <= len(strings)
    
    strings.sort()
    
    sims = [0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF] * len(strings)
    for ii in range(1, len(strings)):
        sims[ii] = string_similarity(strings[ii-1], strings[ii])
    
    min_sim = min(sims)
    divl = 0
    for div in range(1, len(strings)):
        if sims[div] == min_sim:
            divl = div
            if div >= min_size and (len(strings)-div) >= min_size:
                gsmall, glarge = strings[:divl], strings[divl:]
                if len(gsmall) > len(glarge):
                    gsmall, glarge = glarge, gsmall
                return gsmall, glarge
    
    gsmall, glarge = strings[:divl], strings[divl:]
    if len(gsmall) > len(glarge):
        gsmall, glarge = glarge, gsmall
    
    gt, glarge = string_div2(glarge, min_size-len(gsmall))
    gsmall += gt
    if len(gsmall) > len(glarge):
        gsmall, glarge = glarge, gsmall
    
    return gsmall, glarge



def string_group(strings, min_size, max_size):
    assert 2*min_size <= max_size
    if len(strings) > max_size:
        large_groups = [strings]
        small_groups = []
    else:
        large_groups = []
        small_groups = [strings]
    while bool(large_groups):
        group0 = large_groups.pop()
        gsmall, glarge = string_div2(group0, min_size)
        if len(gsmall) > max_size:
            large_groups.append(gsmall)
        else:
            small_groups.append(gsmall)
        if len(glarge) > max_size:
            large_groups.append(glarge)
        else:
            small_groups.append(glarge)
    return small_groups







