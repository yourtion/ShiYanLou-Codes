shiyanlou_cs734
===============

实验楼课程: [Python实现Huffman编码解压缩文件](https://www.shiyanlou.com/courses/734) 相关代码

## 文件编码原理

Huffman编码进行文件压缩的原理:

- 步骤1:对需要被压缩的文件以二进制的方式读，然后以byte为单位读取里面的值，然后将其转换为int值，一共有 ［0-255］共256个值，遍历文件的所有byte，统计出现每个值的次数，作为我们后面叶节点里面的weight (权重)；
- 步骤2:使用上面［0-255］每个值及其对应的权重，构造对应的Huffman编码树，然后分配［0-255］中每一个值对应的Huffman编码；
- 步骤3:在压缩文件的开始，将［0-255］及其对应的weight（权重）以二进制的方式保存到压缩文件当中，此举的目的是方便下次解压缩时根据原文件的［0-255］出现的频率去构造相应的Huffman树，然后对压缩文件进行解压缩的操作
- 步骤4:遍历文件的每一个byte，然后以步骤2中生成的Huffman编码，将该字节转换称为Huffman编码对应01组合
- 步骤5:将步骤4中的生成的01组合串，每8位为一个单位，将其转换成为相应的byte，然后以二进制的方式的方式写入到压缩文件当中，这样压缩就完成了！

Huffman编码进行文件解压缩的原理:

- 步骤1:以二进制读的方式，读出压缩文件中保存的被压缩文件中［0-255］每个值出现的频率
- 步骤2:使用上面［0-255］每个值及其对应的权重，构造对应的Huffman编码树，然后分配［0-255］中每一个值对应的Huffman编码；
- 步骤3:接着以二进制的方式读取压缩文件的内容，读出二进制的01串
- 步骤4:使用步骤3读取出来的01串在步骤2中构造的Huffman编码树当中进行解压缩，进行解压缩的方法是：
    - 1.最开始curr指针指向 编码树的root；
    - 2.循环取出01串的首位;
    - 3.如果取出的值是0，curr指向左孩子；
    - 4.如果取出的值是1，curr指向右孩子；
    - 5.判断curr现在所指向的是否是叶节点： 如果是，将该叶节点对应的字符写入到解压缩文件中，并且curr重置为编码树的root 如果不是，继续2，3，4的操作
    - 6.直到01串被取完，此时解压缩工作完毕。
