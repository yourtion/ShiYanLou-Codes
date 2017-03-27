#-*- coding=utf8 -*-
#!/usr/bin/python
import sys
import six

class HuffNode(object):
    """
    定义一个HuffNode虚类，里面包含两个虚方法：
    1. 获取节点的权重函数
    2. 获取此节点是否是叶节点的函数
    """
    def get_wieght(self):
        """
        获取节点的权重函数
        """
        raise NotImplementedError("The Abstract Node Class doesn't define 'get_wieght'")

    def isleaf(self):
        """
        获取此节点是否是叶节点的函数
        """
        raise NotImplementedError("The Abstract Node Class doesn't define 'isleft'")

class LeafNode(HuffNode):
    """
    树叶节点类
    """
    def __init__(self, value=0, freq=0):
        super(LeafNode, self).__init__()
        self.value = value
        self.wieght = freq

    def isleaf(self):
        """
        基类的方法，返回True，代表是叶节点
        """
        return True

    def get_wieght(self):
        """
        基类的方法，返回对象属性 weight，表示对象的权重
        """
        return self.wieght

    def get_value(self):
        """
        获取叶子节点的 字符 的值
        """
        return self.value

class IntlNode(HuffNode):
    """
    中间节点类
    """
    def __init__(self, left_child=None, right_child=None):
        """
        初始化 中间节点 需要初始化的对象参数有 ：left_child, right_chiled, weight
        """
        super(IntlNode, self).__init__()
        self.wieght = left_child.get_wieght() + right_child.get_wieght()
        self.left_child = left_child
        self.right_child = right_child

    def isleaf(self):
        """
        基类的方法，返回False，代表是中间节点
        """
        return False

    def get_wieght(self):
        """
        基类的方法，返回对象属性 weight，表示对象的权重
        """
        return self.wieght

    def get_left(self):
        """
        获取左子节点
        """
        return self.left_child

    def get_right(self):
        """
        获取右子节点
        """
        return self.right_child

class HuffTree(object):
    """
    HuffTree
    """
    def __init__(self, flag, value=0, freq=0, left_tree=None, right_tree=None):
        super(HuffTree, self).__init__()
        if flag == 0:
            self.root = LeafNode(value, freq)
        else:
            self.root = IntlNode(left_tree.get_root(), right_tree.get_root())

    def get_root(self):
        """
        获取 huffman tree 的根节点
        """
        return self.root

    def get_wieght(self):
        """
        获取这个huffman树的根节点的权重
        """
        return self.root.get_wieght()

    def traverse_huffman_tree(self, root, code, char_freq):
        """
        利用递归的方法遍历 huffman_tree，并且以此方式得到每个 字符 对应的 huffman 编码
        保存在字典 char_freq 中
        """
        if root.isleaf():
            char_freq[root.get_value()] = code
            print("it = %d/%c and freq = %d code = %s")%(root.get_value(), chr(root.get_value()), root.get_wieght(), code)
            return None
        else:
            self.traverse_huffman_tree(root.get_left(), code+'0', char_freq)
            self.traverse_huffman_tree(root.get_right(), code+'1', char_freq)

def build_huffman_tree(list_hufftrees):
    """
    构造huffman树
    """
    while len(list_hufftrees) > 1:
        # 1. 按照 weight 对 huffman 树进行从小到大的排序
        list_hufftrees.sort(key=lambda x: x.get_wieght())

        # 2. 挑出weight 最小的两个huffman编码树
        temp1 = list_hufftrees[0]
        temp2 = list_hufftrees[1]
        list_hufftrees = list_hufftrees[2:]

        # 3. 构造一个新的huffman树
        newd_hufftree = HuffTree(1, 0, 0, temp1, temp2)

         # 4. 放入到数组当中
        list_hufftrees.append(newd_hufftree)

    # 5. 数组中最后剩下来的那棵树，就是构造的Huffman编码树
    return list_hufftrees[0]

def compress_test(inputfile):
    """
    测试压缩
    """
    #1. 以二进制的方式打开文件
    f = open(inputfile, 'rb')
    filedata = f.read()
    # 获取文件的字节总数
    filesize = f.tell()

    # 2. 统计 byte的取值［0-255］ 的每个值出现的频率
    # 保存在字典 char_freq中
    char_freq = {}
    for x in range(filesize):
        tem = six.byte2int(filedata[x])
        if tem in char_freq.keys():
            char_freq[tem] = char_freq[tem] + 1
        else:
            char_freq[tem] = 1

    # 输出统计结果
    for tem in char_freq.keys():
        print tem,' : ',char_freq[tem]

    # 3. 开始构造原始的huffman编码树 数组，用于构造Huffman编码树
    list_hufftrees = []
    for x in char_freq.keys():
        # 使用 HuffTree的构造函数 定义一棵只包含一个叶节点的Huffman树
        tem = HuffTree(0, x, char_freq[x], None, None)
        # 将其添加到数组 list_hufftrees 当中
        list_hufftrees.append(tem)

    # 5. 构造huffman编码树，并且获取到每个字符对应的 编码并且打印出来
    tem = build_huffman_tree(list_hufftrees)
    tem.traverse_huffman_tree(tem.get_root(), '', char_freq)

def compress(inputfilename, outputfilename):
    """
    压缩
    """
    f = open(inputfilename, 'rb')
    filedata = f.read()
    filesize = f.tell()

    char_freq = {}
    for x in range(filesize):
        tem = six.byte2int(filedata[x])
        if tem in char_freq.keys():
            char_freq[tem] = char_freq[tem] + 1
        else:
            char_freq[tem] = 1

    for tem in char_freq.keys():
        print tem, ' : ', char_freq[tem]

    list_hufftrees = []
    for x in char_freq.keys():
        tem = HuffTree(0, x, char_freq[x], None, None)
        list_hufftrees.append(tem)

    length = len(char_freq.keys())
    output = open(outputfilename, 'wb')

    a4 = length&255
    length = length>>8
    a3 = length&255
    length = length>>8
    a2 = length&255
    length = length>>8
    a1 = length&255
    output.write(six.int2byte(a1))
    output.write(six.int2byte(a2))
    output.write(six.int2byte(a3))
    output.write(six.int2byte(a4))

    for x in char_freq.keys():
        output.write(six.int2byte(x))
        temp = char_freq[x]
        a4 = temp&255
        temp = temp>>8
        a3 = temp&255
        temp = temp>>8
        a2 = temp&255
        temp = temp>>8
        a1 = temp&255
        output.write(six.int2byte(a1))
        output.write(six.int2byte(a2))
        output.write(six.int2byte(a3))
        output.write(six.int2byte(a4))

    tem = build_huffman_tree(list_hufftrees)
    tem.traverse_huffman_tree(tem.get_root(), '', char_freq)

    code = ''
    for i in range(filesize):
        key = six.byte2int(filedata[i])
        code = code + char_freq[key]
        out = 0
        while len(code)>8:
            for x in range(8):
                out = out<<1
                if code[x] == '1':
                    out = out | 1
            code = code[8:]
            output.write(six.int2byte(out))
            out = 0
    
    output.write(six.int2byte(len(code)))
    out = 0
    
    for i in range(len(code)):
        out = out<<1
        if code[i] == '1':
            out = out | 1
    for i in range(8-len(code)):
        out = out<<1
    
    output.write(six.int2byte(out))
    output.close()

def decompress(inputfilename, outputfilename):
    """
    解压
    """
    f = open(inputfilename, 'rb')
    filedata = f.read()
    filesize = f.tell()

    a1 = six.byte2int(filedata[0])
    a2 = six.byte2int(filedata[1])
    a3 = six.byte2int(filedata[2])
    a4 = six.byte2int(filedata[3])
    j = 0
    j = j | a1
    j = j << 8
    j = j | a2
    j = j << 8
    j = j | a3
    j = j << 8
    j = j | a4
    leaf_node_size = j

    char_freq = {}
    for i in range(leaf_node_size):
        c = six.byte2int(filedata[4+i*5+0])

        a1 = six.byte2int(filedata[4+i*5+1])
        a2 = six.byte2int(filedata[4+i*5+2])
        a3 = six.byte2int(filedata[4+i*5+3])
        a4 = six.byte2int(filedata[4+i*5+4])
        j = 0
        j = j | a1
        j = j << 8
        j = j | a2
        j = j << 8
        j = j | a3
        j = j << 8
        j = j | a4
        print c, j
        char_freq[c] = j

    list_hufftrees = []
    for x in char_freq.keys():
        tem = HuffTree(0, x, char_freq[x], None, None)
        list_hufftrees.append(tem)
    tem = build_huffman_tree(list_hufftrees)
    tem.traverse_huffman_tree(tem.get_root(), '', char_freq)

    output = open(outputfilename, 'wb')
    code = ''
    currnode = tem.get_root()
    for x in range(leaf_node_size*5+4, filesize):
        c = six.byte2int(filedata[x])
        for i in range(8):
            if c&128:
                code = code + '1'
            else:
                code = code + '0'
            c = c << 1

        while len(code) > 24:
            if currnode.isleaf():
                tem_byte = six.int2byte(currnode.get_value())
                output.write(tem_byte)
                currnode = tem.get_root()

            if code[0] == 1:
                currnode = currnode.get_right()
            else:
                currnode = currnode.get_left()
            code = code[1:]

    sub_code = code[-16:-8]
    last_length = 0
    for i in range(8):
        last_length = last_length << 1
        if sub_code[i] == '1':
                last_length = last_length | 1
    code = code[:-16] + code[-8:-8+last_length]

    while len(code) > 0:
        if currnode.isleaf():
            tem_byte = six.int2byte(currnode.get_value())
            output.write(tem_byte)
            currnode = tem.get_root()

        if code[0] == '1':
            currnode = currnode.get_right()
        else:
            currnode = currnode.get_left()
        code = code[1:]

    if currnode.isleaf():
        tem_byte = six.int2byte(currnode.get_value())
        output.write(tem_byte)
        currnode = tem.get_root()

    output.close()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "please input flag(0|1) inputfilename outputfilename"
        exit(0)
    else:
        FLAG = sys.argv[1]
        INPUTFILE = sys.argv[2]
        OUTPUTFILE = sys.argv[3]

    if FLAG == '0':
        print 'compress file'
        compress(INPUTFILE, OUTPUTFILE)
    elif FLAG == '1':
        print 'decompress file'
        decompress(INPUTFILE, OUTPUTFILE)
    else:
        if FLAG == 'test':
            if INPUTFILE == 'compress':
                compress_test(OUTPUTFILE)

