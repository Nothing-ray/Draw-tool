import hashlib  # 计算hash值的库
import re       # 正则表达式库，用来从hash中提取数字
import random   # 随机库，用于生成随机数，用来抽奖，以及给hash迭代加盐
import sys      # 用于解释器和系统环境交互的库

# 导入四个Python自带的标准库，不需要额外下载安装第三方库



# 读取文件的方法，将文件读取，并且返回读取指针
def get_file_content(file_path):
    try: # 建立一个异常处理机制
        # 用UTF-8方法打开文件，返回读取结果
        with open(file_path, 'r', encoding='utf-8') as file_point:
            file_point = file_point.read()
            return file_point
    except FileNotFoundError:# 文件找不到的情况
        print(f"文件未找到: {file_path}")
        sys.exit(1)
    except IOError:# 读取文件失败的情况
        print(f"读取文件失败: {file_path}")
        sys.exit(1)


# 计算hash的方法，输入一段信息
def get_hash256(file_information):
    # 创建一个空白的hash对象
    hash = hashlib.sha256()
    # 用输入的信息计算并且更新hash，编码方式UTF-8
    hash.update(file_information.encode('utf-8'))
    # 输出hash，以16进制形式
    return hash.hexdigest()




# 将hash值的前n位数字输出
def extract_digits(str, n):
    # 用正则表达式提取hash值的所有数据
    digits = re.findall(r'\d', str)
    # 取的种子长度太长，或者hash值是一些非常独特的值的情况
    if len(digits) < n:
        print("哈希值中数字不足以提取所需长度的种子\n")
        print("建议缩短种子长度或者更改文件内容以生成新的hash值\n")
        sys.exit(1)
    # 取出前n位数字
    digits = digits[:n]
    # 将数字列表合并成字符串
    digits_str = ''.join(digits)
    # 字符串转数字
    digits_int = int(digits_str)

    return digits_int



# hash迭代
# 将hash和种子作为输入，每次迭代都先从种子生成一个随机数，
# 将随机数和hash拼接在一起，再次计算hash，进一步混淆
# 重复多次，避免用hash碰撞或者用彩虹表倒推作弊
def hash_iteration(hash_value,seed,n):
    # 设置随机种子
    random.seed(seed)
    # 生成n个随机数作为盐，用来作为干扰
    random_list = [random.random() for _ in range(n)]
    # 设定初始hash，在那之前要把hash值从便于阅读的16进制转换回便于操作的字节对象
    old_hash = bytes.fromhex(hash_value)
    # 创建一个空白的hash对象，每次迭代的时候从此处复制一个新的，比重新创建性能消耗更低
    blank_hash_object = hashlib.sha256()

    for i in range(n):
        # 将hash 和 盐完成拼装
        new_string = old_hash + str(random_list[i]).encode('utf-8')
        # 从空白对象那里复制一个过来用
        new_hash = blank_hash_object.copy()
        # 迭代出新的hash
        new_hash.update(new_string)
        # 更新旧的hash进入下一次迭代,通过将新hash的摘要(实际上的新hash值)
        old_hash = new_hash.digest()
    return new_hash.hexdigest()


# 真正意义上的抽奖函数，前面的所有函数都是为了确保生成的种子真正随机且破解成本高
# 生成一个长度为n的数列（代表抽奖人数）
# 根据随机种子的设置把数列随机打乱，随机打乱数列作为结果
def draw(n,seed):
    # 生成抽奖队列，从1开始排起
    draw_list = list(range(1,1+n))
    # 设置随机种子，确保日后可以复原
    random.seed(seed)
    # 将抽奖队列打乱
    random.shuffle(draw_list)

    return draw_list


def get_int_input():

    while True:
        try:# 建立一个异常处理机制
            # 读取输入的数据
            draw_num_value = input("请输入抽奖人数")
            # 将输入的数据转换为整数
            draw_num_value = int(draw_num_value)
            # 输出
            return draw_num_value
        except ValueError: # 如果在转换整数的过程中出错（输入非整数信息）
            print("请输入一个整数")



# 主函数，整个抽奖流程从这里开始
if __name__ == "__main__":

    # 参数化区，您可以在这里设置一些关键的执行参数

    # 种子的长度，越长的种子安全性越高，这决定了从hash中取多少位
    seed_len = 10
    # 迭代的次数，每次都会把上一次的hash值加上随机数（盐）再次迭代，迭代次数越多暴力破解难度越高
    iteration_num = 10000


    
    # 设置文件路径
    if len(sys.argv) > 1:# 系统传入参数的情况
        # 如果本脚本按照预期的使用方式（被打包为exe可执行程序）则会从系统处接受文件路径
        file_path = sys.argv[1]
    else:# 没有传入的情况
        # 如果您希望直接从脚本执行，则在下面设置文件路径
        file_path = 'demo.txt'



    # 执行区，主要的抽奖流程在这里进行

    
    #获取需要抽奖的数量
    draw_num = get_int_input()



    # 先读取文件
    file = get_file_content(file_path)
    # 初始化hash值，之后进行迭代
    hash_init = get_hash256(file)
    # 初始化seed值，基于之前设置的长度和生成的hash值
    seed_init = extract_digits(hash_init, seed_len)
    # 基于迭代，计算出最终的hash值
    hash_final = hash_iteration(hash_init, seed_init, iteration_num)
    # 计算出最终的随机种子seed
    seed_final = extract_digits(hash_final, seed_len)
    # 现在我们终于可以开始抽奖了，使用最终的种子和抽奖数目进行抽奖。
    draw_list = draw(draw_num, seed_final)
    #输出抽奖结果
    print("\n抽奖结果: {}\n".format(draw_list))
    print("种子长度: {}\n".format(seed_len))
    print("迭代次数: {}\n".format(iteration_num))
    print("最终随机种子: {}\n".format(seed_final))
    print("最终hash值:{}\n".format(hash_final))
    #等待退出
    input("按回车键退出...")




