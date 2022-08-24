# -*- coding:utf-8 -*-
# Python3


# 类 : dual_key_dict
# 功能 : 双键字典，具有两个键 keya 和 keyb 共同组成键对儿 (keya, keyb) , 任意 (keya, keyb) 都能对应一个 item 。
#        与普通字典不同的是，指定 keya , 它能以 O(1) （哈希查询）的复杂度给出所有包含 keya 的键对儿 (keya, keyb)
#                      同理，指定 keyb , 它能以 O(1) （哈希查询）的复杂度给出所有包含 keyb 的键对儿 (keya, keyb)
class dual_key_dict():

    def __init__(self):
        self.a2b = dict()
        self.b2a = dict()

    # 方法 : pop_pair
    # 功能 : 指定键对 key_pair （key_pair 必须是二元组），弹出它
    # 返回 : item
    def pop_pair(self, key_pair:tuple):
        keya, keyb = key_pair
        item = None
        if keya in self.a2b:
            keya2b = self.a2b[keya]
            if keyb in keya2b:
                item = keya2b.pop(keyb)
                if len(keya2b) <= 0:
                    self.a2b.pop(keya)
        if keyb in self.b2a:
            a2keyb = self.b2a[keyb]
            if keya in a2keyb:
                item = a2keyb.pop(keya)
                if len(a2keyb) <= 0:
                    self.b2a.pop(keyb)
        return item
    
    # 方法 : pop_one_pair
    # 功能 : 弹出其中一个键对（不指定删除哪个键对，所以它会删除任意一个）
    # 返回 : 若里面有，则弹出成功，返回 keya, keyb, item
    #        若里面没有，则弹出失败，返回 None
    def pop_one_pair(self):
        for keya in self.a2b:
            for keyb in self.a2b[keya]:
                return keya, keyb, self.pop_pair((keya, keyb))
        return None
    
    def rm_keya(self, keya):
        if keya in self.a2b:
            for keyb in self.a2b.pop(keya):
                self.pop_pair((keya, keyb))
    
    def rm_keyb(self, keyb):
        if keyb in self.b2a:
            for keya in self.b2a.pop(keyb):
                self.pop_pair((keya, keyb))
    
    def rm_key_both(self, key):
        self.rm_keya(key)
        self.rm_keyb(key)
    
    def __setitem__(self, key_pair:tuple, item):
        keya, keyb = key_pair
        if not keya in self.a2b:
            self.a2b[keya] = dict()
        self.a2b[keya][keyb] = item
        if not keyb in self.b2a:
            self.b2a[keyb] = dict()
        self.b2a[keyb][keya] = item
    
    def __getitem__(self, key_pair:tuple):
        keya, keyb = key_pair
        if keya in self.a2b:
            if keyb in self.a2b[keya]:
                return self.a2b[keya][keyb]
        return None
    
    def __contains__(self, key_pair:tuple):
        keya, keyb = key_pair
        if keya in self.a2b:
            if keyb in self.a2b[keya]:
                return True
        return False
    
    def __bool__(self):
        return len(self.a2b) > 0
    
    def __len__(self):
        length = 0
        for keya in self.a2b:
            length += len(self.a2b[keya])
        return length
    
    def keya_dict(self, keya):
        if keya in self.a2b:
            return dict(self.a2b[keya])
        else:
            return dict()
    
    def keyb_dict(self, keyb):
        if keyb in self.b2a:
            return dict(self.b2a[keyb])
        else:
            return dict()
    
    def all_keya(self):
        return set(self.a2b)
    
    def all_keyb(self):
        return set(self.b2a)
    
    def tolist(self):
        return [ (keya, keyb, self.a2b[keya][keyb])  for keya in self.a2b  for keyb in self.a2b[keya] ]
    
    def self_check(self):
        for keya in self.a2b:
            if len( self.a2b[keya] ) <= 0:
                raise Exception('Error: a2b[%d] is empty' % keya )
            for keyb in self.a2b[keya]:
                if self.a2b[keya][keyb] != self.b2a[keyb][keya]:
                    raise Exception('Error: %d->%d != %d<-%d' % (keya, keyb, keyb, keya) )
        for keyb in self.b2a:
            if len( self.b2a[keyb] ) <= 0:
                raise Exception('Error: b2a[%d] is empty' % keyb )
            for keya in self.b2a[keyb]:
                if self.b2a[keyb][keya] != self.a2b[keya][keyb]:
                    raise Exception('Error: %d<-%d != %d->%d' % (keyb, keya, keya, keyb) )




