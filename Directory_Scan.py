from pathlib import Path
import multiprocessing
import time
import datetime
import math
import os
import sys
import getpass
import socket
import argparse
import subprocess

# 写在前面
# pathlib 除了官方文档，推荐这几个网址学习
# https://www.cnblogs.com/poloyy/p/12435628.html
# https://zhuanlan.zhihu.com/p/87940289
# https://zhuanlan.zhihu.com/p/139783331
# https://zhuanlan.zhihu.com/p/430823972
# https://zhuanlan.zhihu.com/p/56909212
# https://zhuanlan.zhihu.com/p/475661402


'''
st_mode: inode 保护模式
st_ino: inode 节点号。
st_dev: inode 驻留的设备。
st_nlink: inode 的链接数。
st_uid: 所有者的用户ID。
st_gid: 所有者的组ID。
st_size: 普通文件以字节为单位的大小；包含等待某些特殊文件的数据。
st_atime: 上次访问的时间。
st_mtime: 最后一次修改的时间。
st_ctime: 由操作系统报告的"ctime"。在某些系统上（如Unix）是最新的元数据更改的时间，在其它系统上（如Windows）是创建时间（详细信息参见平台的文档）。
'''

#################start Judge the system platform start#################


def obtain_platform():
    '''
    Determine the current system
    '''
    #import sys
    platform_flag = 'win'
    if sys.platform.startswith("win"):
        platform_flag = 'win'
        #print("当前系统是Windows")
    elif sys.platform.startswith("linux"):
        platform_flag = 'linux'
        #print("当前系统是Linux")
    elif sys.platform.startswith("darwin"):
        platform_flag = 'darwin(Mac OS)'
        #print("当前系统是Mac OS")
    else:
        #print("当前系统是其他操作系统")
        platform_flag = 'other unknown operating systems'
    print("The current system is " + platform_flag)
    return platform_flag

#################end    Judge the system platform    end#################




#######################start  file  stat_time  start#######################
#####
####
###

def get_file_UTC_Timestamp(file_path):
    '''
    获得文件的两种时间戳；用于转换和计算
    #https://www.cnblogs.com/pal-duan/p/10568829.html
    flag='g'   GMT 格林尼治标准时间  缩写 UTC 英法妥协缩写 time.gmtime()  #huawei cloud 用的是这个，所以和本地时间差了 8h
    flag='l'  time.localtime() 本机本地时间
    modifiedTime os.stat(file).st_mtime
    createdTime  os.stat(file).st_ctime
    #时间戳之间没有差异
    '''
    #from pathlib import Path
    stat_result=Path(file_path).stat()
    createdTimeStamp = Timestamp_local2utc(stat_result.st_ctime)
    modifiedTimeStamp = Timestamp_local2utc(stat_result.st_mtime)
    # createdTimeStamp = Timestamp_local2utc(os.stat(file_path).st_ctime)
    # modifiedTimeStamp = Timestamp_local2utc(os.stat(file_path).st_mtime)
    #主要检查修改时间
    return createdTimeStamp, modifiedTimeStamp
 
 
def convert_time2Timestamp(time_str, UTC_FORMAT="%Y-%m-%dT%H:%M:%SZ"):
    '''
    2021-03-19T21:37:25Z
    2021-03-26T20:44:31Z
    #UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ" #huawei cloud
    #LOCAL_FORMAT = "%Y-%m-%d %H:%M:%S"
    #huawei cloud  使用的是 UTC GMT 格林尼治标准时间
    #本地时间戳 进行修改
    #https://blog.csdn.net/weixin_34080951/article/details/94101201
    #https://www.cnblogs.com/jfl-xx/p/8024596.html
    '''
    timeArray = time.strptime(time_str, UTC_FORMAT)
    timeStamp = time.mktime(timeArray)
    return timeStamp
 
 
 
def Timestamp_local2utc(local_stamp):
    '''
    local_stamp 来自本地时间转换
    根据时区与 UTC 时区的 时间偏移offset  ，计算utc 时区的时间戳

    import datetime
    timestamp = 1687565839  # 时间戳，单位为s
    utc_time = datetime.datetime.utcfromtimestamp(timestamp)  # 将时间戳转换为UTC时间
    # 将UTC时间转换为北京时间
    beijing_timezone = datetime.timezone(datetime.timedelta(hours=8))
    beijing_time = utc_time.astimezone(beijing_timezone)
    print(f"从时间戳{timestamp}转换得到的时间为：{beijing_time}")
    # 从时间戳1687565839转换得到的时间为：2023-06-24 08:17:19+08:00
    # https://www.zhihu.com/question/608209144/answer/3087188010

    '''
    now_stamp = time.time()
    #offset,看下 时间戳之间的偏移 是否是一个时区
    local_time = time.mktime(time.localtime(now_stamp))
    utc_time = time.mktime(time.gmtime(now_stamp))
    #print(local_time)
    #print(utc_time)
    offset = utc_time - local_time
    #print('offset', offset)
    if utc_time == local_time:
        return local_stamp
    else:
        utc_stamp = local_stamp + offset
        return utc_stamp

def TimeStamp2TimeStr(TimeStamp,FormatStr="%Y-%m-%d %H:%M:%S",TimeOffset_h=8):
    '''
    将UTC时间转换为北京时间(UTC时间8小时偏移)
    Dependence:import datetime
    '''

    utc_time = datetime.datetime.utcfromtimestamp(TimeStamp)  # 将时间戳转换为UTC时间
    # 将UTC时间转换为北京时间 TimeOffset_h = 8
    OffsetTimeZone = datetime.timezone(datetime.timedelta(hours=TimeOffset_h))
    NewTimeStamp = utc_time.astimezone(OffsetTimeZone)
    #print(f"从时间戳{TimeStamp}转换得到的时间为：{NewTimeStamp}")
    # 从时间戳1687565839转换得到的时间为：2023-06-24 08:17:19+08:00
    # https://www.zhihu.com/question/608209144/answer/3087188010
    FormattedTime = NewTimeStamp.strftime(FormatStr)
    return FormattedTime

###
####
#####
#######################end  file  stat_time  end#######################


######################begin       file size          begin#####################
#https://blog.csdn.net/w55100/article/details/92081182
 
#a ^ x = b
#x = lgb ÷lga = log（以a为底）b的对数
#https: // zhidao.baidu.com/question/750931419356209332.html
 
 
def convertSizeUnit(sz, source='B', target='AUTO', return_unit=False):
    '''
    文件大小指定单位互转，自动则转换为最大的适合单位
    '''
    #target=='auto' 自动转换大小进位,大于1024 就进位；对于不能进位的返回原始大小和单位
    #return_unit 是否返回 单位
    source = source.upper()
    target = target.upper()
    return_unit = bool(return_unit)
    unit_lst = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'AUTO']
    unit_dic = {'B': 0, 'KB': 1, 'MB': 2,
                'GB': 3, 'TB': 4, 'PB': 5, 'AUTO': -1}
    source_index = unit_dic[source]
    target_index = unit_dic[target]
    index = math.log(sz, 1024)  # 计算数字中有几个1024 相乘过；或者说可以被几个1024 除掉

    # initialization
    target_unit = target
    result_sz = 0

    if target == 'AUTO':
        if index < 1:  # source 比 target 还大，不能进位，自动就返回原始的
            return sz, source
        unit_index = int(index)
        # 得到的 可 进位的数字+原始的 index;或者真正的单位
        target_unit = unit_lst[unit_index+source_index]
        result_sz = sz/1024**(unit_index)  # 进位
 
    else:  # 非自动
        if index < 1:  # source 的单位比 target 还大
            cmp_level = source_index-target_index  # 差距
            result_sz = sz*1024**cmp_level  # 退位，乘以1024
        else:  # source 的单位比 target 小
            cmp_level = target_index - source_index  # 差距
            result_sz = sz/1024**cmp_level  # 进位 ，除以1024
    if return_unit:
        return result_sz, target_unit
    else:
        return result_sz
         
 
 
def getFileSize(file_path, target='KB'):
    '''
    获取文件大小，target指定文件大小单位
    '''
    #from pathlib import Path
    stat_result=Path(file_path).stat()
    sz =stat_result.st_size
    #sz = os.path.getsize(file_path)

    # initialization
    result_sz = 0 
    if target == 'B':
        result_sz = sz
    else:
        new_sz, size_unit = convertSizeUnit(sz, source='B', target=target, return_unit=True)
        if size_unit == 'B': # 未能转成功
            result_sz = new_sz
        else:
            result_sz = float('{:.2f}'.format(new_sz)) #
    return result_sz
 
 
def getdirsize(dir, target='B'):
    '''
    获取目录文件总大小，target指定文件大小单位
    '''
    size = 0
    # for root, dirs, files in os.walk(dir):
    #     # print("当前目录为：", root)
    #     # print("当前目录下的子目录有：", dirs)
    #     # print("当前目录下的文件有：", files)
    #     size += sum([getFileSize(os.path.join(root, name), target=target) for name in files])

    target_path=Path(dir)
    for child in target_path.rglob("*"):
        if child.is_dir() or child.is_symlink():
            continue
        size += getFileSize(child, target=target)

    return size
 
######################end       file size          end#####################

###################    目录扫描   #######################
 
def GetFolderCatalogPath(pwd):
    '''
    获取目录下文件夹全路径，返回列表
    param: str  "pwd"
    return:list [ str ]
    '''
    catalog_lst=[]
    target_path=Path(pwd)
    #dirname = child.parent
    #dirname=target_path
    for child in target_path.iterdir():
        if child.is_symlink():
            pass
        elif child.is_dir():
            #对于空文件夹跳过
            if not os.listdir(str(child)):
                print("empty directory: "+str(child))
                continue
            catalog_lst.append(child)
        elif child.is_file():
            pass
    return catalog_lst
 
def GetFolderCatalogName(pwd):
    '''
    获取目录下文件夹名称，返回列表
    param: str  "pwd"
    return:list [ str ]
    '''
    catalog_lst=[]
    target_path=Path(pwd)
    #dirname = child.parent
    #dirname=target_path
    for child in target_path.iterdir():
        if child.is_symlink():
            pass
        elif child.is_dir():
            #对于空文件夹跳过
            if not os.listdir(str(child)):
                print("empty directory: "+str(child))
                continue
            catalog_lst.append(child.name)
        elif child.is_file():
            pass
    return catalog_lst
 
 
def GetAllFilePaths(pwd,wildcard='*'):
    '''
    获取目录下文件全路径，通配符检索特定文件名，返回列表
    param: str  "pwd"
    return:dirname pathlab_obj
    return:list [ str ]
    #https://zhuanlan.zhihu.com/p/36711862
    #https://www.cnblogs.com/sigai/p/8074329.html
    '''
    files_lst = []
    target_path=Path(pwd)
    for child in target_path.rglob(wildcard):
        if child.is_symlink():
            pass
        elif child.is_dir():
            pass
        elif child.is_file():
            #files_lst.append(str(child))
            files_lst.append(child)
    return files_lst
 
 
def GetAllFileNames(pwd):
    '''
    获取目录下所有文件名，返回列表
    param: str  "pwd"
    return:dirname pathlab_obj
    return:list [ str ]
    #https://zhuanlan.zhihu.com/p/36711862
    #https://www.cnblogs.com/sigai/p/8074329.html
    '''
    files_lst = []
    #字符串路径 工厂化为 pathlib 对象，可使用pathlib 对象的方法(函数)/属性(私有变量)
    target_path = Path(pwd)
    for child in target_path.rglob('*'):
        if child.is_symlink():
            pass
        elif child.is_dir():
            pass
        elif child.is_file():
            #child完整路径,child.relative_to(pwd) 相对于pwd的相对路径，其实就是文件名;可以通过child.name获得
            files_lst.append(child.relative_to(pwd))
            #print(child.relative_to(pwd))
    return files_lst


def decide_subdirectory(parent_directory,check_directory):
    '''
    检查是否是子目录或者相同目录
    decide_subdirectory(parent_directory,check_directory)
    abs_parent_directory = Path(parent_directory).resolve()
    abs_check_directory = Path(check_directory).resolve()
    '''
    abs_parent_directory = Path(parent_directory).resolve()
    abs_check_directory = Path(check_directory).resolve()
    return abs_parent_directory == abs_check_directory or abs_parent_directory in abs_check_directory.parents

def iterate_path(root_path,whitelist,max_depth=1):
    '''
    指定深度，获得目录下所有path
    whitelist  path_obj
    '''
    # iterdir 只扫描当前1级目录
    for child_path in root_path.iterdir():
        path_depth = len(child_path.relative_to(root_path).parts)
        if child_path.is_dir() and not child_path.is_symlink() and path_depth < max_depth :
            child_max_depth = max_depth - 1
            # 过滤白名单的路径
            if len(whitelist) > 0:
                if child_path in whitelist:
                    continue
                # set() 有交集形同内容，则认为有重复，去掉
                elif len(list(whitelist.intersection(child_path.parents)))>0:
                    continue
            yield from iterate_path(child_path,whitelist,max_depth=child_max_depth)
        elif child_path.is_file()  and not child_path.is_symlink():
            # 过滤白名单的路径
            if len(whitelist) > 0:
                if child_path.parent in whitelist:
                    continue
                # set() 有交集形同内容，则认为有重复，去掉
                elif len(list(whitelist.intersection(child_path.parents)))>0:
                    continue
            yield child_path
        
        # yield child_path

def  get_file_info(target_path,whitelist,platform):
    '''
    文件名，文件上级目录，创建时间，修改时间，文件大小bit
    '''
    file_info_lst = []
    if target_path.is_file() and not target_path.is_symlink():
        FileName = target_path.name
        ParentOfDirectory = target_path.parent
        createdTimeStamp, modifiedTimeStamp = get_file_UTC_Timestamp(target_path)
        CreatedTime = TimeStamp2TimeStr(createdTimeStamp)
        ModifiedTime = TimeStamp2TimeStr(modifiedTimeStamp)
        FileSizeBit = getFileSize(target_path, target='B')
        owner = get_file_owner(target_path,platform)
        
        # 过滤白名单的路径
        if len(whitelist)>0:
            # 存在重复的
            if len(set(target_path.parents).intersection(whitelist))>0:
                #print(len(set(target_path.parents).intersection(whitelist)))
                pass
            else:
                file_info_lst.append([FileName,ParentOfDirectory,owner,CreatedTime,ModifiedTime,FileSizeBit])
        else:
            file_info_lst.appen([FileName,ParentOfDirectory,owner,CreatedTime,ModifiedTime,FileSizeBit])
        #print(file_info_lst)
        #print(f"文件: {target_path.name}")
    elif target_path.is_dir() and not target_path.is_symlink():
        for item in target_path.iterdir():
            if  item.is_symlink():
                continue
            elif item.is_file():
                # 过滤白名单的路径
                if len(whitelist)>0:
                    # set() 有交集内容，则认为有重复；白名单过滤
                    if len(set(target_path.parents).intersection(whitelist))>0:
                            continue
                FileName = item.name
                ParentOfDirectory = item.parent # pathlab 
                createdTimeStamp, modifiedTimeStamp = get_file_UTC_Timestamp(item)
                CreatedTime = TimeStamp2TimeStr(createdTimeStamp)
                ModifiedTime = TimeStamp2TimeStr(modifiedTimeStamp)
                FileSizeBit = getFileSize(item, target='B')
                owner = get_file_owner(target_path,platform)
                file_info_lst.append([FileName,ParentOfDirectory,owner,CreatedTime,ModifiedTime,FileSizeBit])
                #print(f"文件: {item.name}")
            elif item.is_dir():
                continue
                DirectoryName = item.name
                print(f"目录: {item.name}")
            pass
    return file_info_lst

def get_file_owner(ObjectPath,platform='win'):
    '''
    pip install pywin32
    ObjectPath :Path(file_path) # pathlab
    '''
    if platform == 'win':
        # import win32api
        # import win32con
        # CurrentUserName = win32api.GetUserNameEx(win32con.NameSamCompatible)
        # import getpass
        # CurrentUserName = getpass.getuser()
        import win32security
        sd = win32security.GetFileSecurity (str(ObjectPath), win32security.OWNER_SECURITY_INFORMATION)
        owner_sid = sd.GetSecurityDescriptorOwner ()
        name, domain, type = win32security.LookupAccountSid (None, owner_sid)
        owner = name
    else:
        owner = ObjectPath.owner()
    return owner
    
##################end   目录扫描  end######################

def get_args():
    parser = argparse.ArgumentParser(
        description=" Directory Scan ", usage="python3 %(prog)s [options]")
    # 扫描的目标目录
    parser.add_argument(
        "-d","--directory", help="The target directory to be scanned;default: current working directory.", default=Path.cwd(), metavar="DIR")
    # 初始的扫描深度，用于拆分任务 max_scan_depth
    parser.add_argument(
        "-s","--split", help="The depth of the directory task split;[default: %(default)s]", type=int,  default=3, metavar="INT")
    # Top 最大的前N文件  TOPNUMBER
    parser.add_argument(
        "-n","--number", help="Sort by file size, and enter the first %(default)s file information;[default: %(default)s]", type=int,  default=20, metavar="INT")
    # 输出目录最大深度 MAXDEPTH
    parser.add_argument(
        "-m","--maximum_depth", help='Only the maximum depth relative to the scanned directory is output;[default: %(default)s]', type=int, default=1, metavar="INT")
    # 白名单目录
    parser.add_argument(
        "-w",'--whitelist', help='Whitelist of directories/files, which does not count files or directories;[default: %(default)s]', type=str, default="WhiteList.txt", metavar="FILE")
    parser.add_argument(
        "-p","--process_num", help='Number of multi-process processes;[default: %(default)s]', type=int, default=4, metavar="INT")
    parser.add_argument(
        "-o","--outdir", help="The directory of the result output;default: current working directory.",default=Path.cwd(), metavar="DIR")

    if len(sys.argv) < 1:
        parser.print_help()
        sys.exit()
    else:
        args = parser.parse_args()

    return args


def main():
    script_path =Path(__file__)
    script_dir = Path(script_path).parent
    #print(script_dir)
    current_dir = Path.cwd()

    ################start Read the parameters start################
    args = get_args()
    input_directory = args.directory
    max_split_depth = args.split
    TOPNUMBER = args.number
    MAXDEPTH = args.maximum_depth
    whitelist_file = args.whitelist
    PROCESS_NUM = args.process_num
    outdir = Path(args.outdir)
    ################end Read the parameters end################

    #################start Information Collection start#################
    # import getpass
    # import socket

    User_Name = getpass.getuser()
    host_Name = socket.gethostname()
    current_ip = socket.gethostbyname(host_Name)
    print(f'Current Program Executor: {User_Name}')
    print(f'Host Name: {host_Name}')
    print(f'Current IP: {current_ip}')
    #################end  Information Collection  end#################

    #global platform 
    platform = obtain_platform()

    root_path = Path(input_directory).resolve() # 转为绝对路径 

    ## 读取白名单文件
    WhiteList_lst = set() # pathlib object
    whitelist_file_obj = Path(whitelist_file).resolve()
    if whitelist_file_obj.exists() and whitelist_file_obj.is_file():
        with open(whitelist_file,mode='rt',encoding='utf-8') as fh:
            for line in fh:
                path_obj = Path(line.strip())
                if decide_subdirectory(root_path,path_obj):
                    WhiteList_lst.add(path_obj)
    
    path_tasks = []
    for path in iterate_path(root_path,WhiteList_lst,max_split_depth):
        #print(path.stat().st_gid)
        #print(path.stat().st_ctime)
        path_tasks.append((path,WhiteList_lst,platform))
        #print(path)
        #print(get_file_UTC_Timestamp(path))
        #print(path.parent)

    # print(a.stat().st_size)
    '''
    st_mode: inode 保护模式
    st_ino: inode 节点号。
    st_dev: inode 驻留的设备。
    st_nlink: inode 的链接数。
    st_uid: 所有者的用户ID。
    st_gid: 所有者的组ID。
    st_size: 普通文件以字节为单位的大小；包含等待某些特殊文件的数据。
    st_atime: 上次访问的时间。
    st_mtime: 最后一次修改的时间。
    st_ctime: 由操作系统报告的"ctime"。在某些系统上（如Unix）是最新的元数据更改的时间，在其它系统上（如Windows）是创建时间（详细信息参见平台的文档）。
    '''

    # PROCESS_NUM = 4
    # start = time.time()
    infos = []
    with multiprocessing.Pool(PROCESS_NUM) as pool:
        # prime 返回值
        # pool.map() 返回返回值的 列表，函数，参数列表 【(),()】
        # Pool.starmap()就像是一个接受参数的Pool.map()版本
        # results = pool.map(howmany_within_range_rowonly,[row for row in data])
        # results = pool.starmap(howmany_within_range, [(row, 4, 8) for row in data])
        # https://blog.csdn.net/wei18791957243/article/details/108733719
        infos = [info for 
                  n, info in enumerate(pool.starmap(get_file_info,path_tasks))
                  if info]
    # print(f"Took {time.time() - start } seconds")
    # print(f"Got {len(primes)} primes")
    result_info =[]
    for inf in infos:
        #print(inf)
        result_info = result_info + inf
    #print(result_info)
    
    # 按照目录统计大小
    
    '''
    file_info_lst.append([FileName,ParentOfDirectory,CreatedTime,ModifiedTime,FileSizeBit])
    '''
    UserOccupancySize_dic = {} # 存储用户总文件占用*****
    directory_info_dic = {} # 目录下有文件的目录单独总大小
    for info_lst in  result_info:
        FileName,ParentOfDirectory,owner,CreatedTime,ModifiedTime,FileSizeBit = info_lst
        if owner not in UserOccupancySize_dic:
            UserOccupancySize_dic[owner] = FileSizeBit
        else:
            UserOccupancySize_dic[owner] += FileSizeBit

        if ParentOfDirectory not in directory_info_dic:
            CatalogLevel = len(Path(ParentOfDirectory).relative_to(root_path).parts)# 相对而言 1 只有目标目录下一层
            #CatalogLevel = len(Path(ParentOfDirectory).parts)
            createdTimeStamp, modifiedTimeStamp = get_file_UTC_Timestamp(ParentOfDirectory)
            CreatedTime = TimeStamp2TimeStr(createdTimeStamp)
            ModifiedTime = TimeStamp2TimeStr(modifiedTimeStamp)
            owner = get_file_owner(ParentOfDirectory,platform)
            #print(ParentOfDirectory)
            directory_info_dic[ParentOfDirectory] = [CatalogLevel,owner,CreatedTime,ModifiedTime,FileSizeBit]
            #                                             0         1        2           3            4           5
            #print(directory_info_dic[ParentOfDirectory])
        else:
            directory_info_dic[ParentOfDirectory][-1] += FileSizeBit 
    #print(directory_info_dic.keys())

    # 更新所有层目录级的总大小
    for dir_obj in directory_info_dic:
        Dir_Depth = len(dir_obj.relative_to(root_path).parts)# 
        CatalogLevel,owner,CreatedTime,ModifiedTime,FileSizeBit = directory_info_dic[ParentOfDirectory]
        if Dir_Depth == 1:
            continue
        else:# 取所有上级，只要深度大于1,主目录下所有文件都统计
            for tmp_depth in range(Dir_Depth,1,-1): #2,则循环一次
                dir_obj = Path(dir_obj.parent)
                if dir_obj not in directory_info_dic:
                    createdTimeStamp, modifiedTimeStamp = get_file_UTC_Timestamp(dir_obj)
                    CreatedTime = TimeStamp2TimeStr(createdTimeStamp)
                    ModifiedTime = TimeStamp2TimeStr(modifiedTimeStamp)
                    owner = get_file_owner(dir_obj,platform)
                    directory_info_dic[dir_obj] = [tmp_depth,owner,CreatedTime,ModifiedTime,FileSizeBit]
                else:
                    directory_info_dic[dir_obj][-1] += FileSizeBit 
    
    # 按照深度排序，输出所有目录 # directory_info_dic
    # CatalogLevel,owner,CreatedTime,ModifiedTime,FileSizeBit = directory_info_dic[ParentOfDirectory]
    # MAXDEPTH = 5
    # CatalogLevel 升序,FileSizeBit 降序
    sorted_directory_lst = sorted(directory_info_dic.keys(), key=lambda key:(directory_info_dic[key][0],-directory_info_dic[key][-1]), reverse=False)
    header_str = 'CatalogLevel\tOwner\tCreatedTime\tModifiedTime\tDirectorySize\tSizeUnit\tDirectory\n'
    Directory_stat_file = Path.joinpath(outdir, "DirectorySizeStatistics.xls")
    with open(Directory_stat_file,mode='wt',encoding='utf-8') as dir_stat_out:
        dir_stat_out.write(header_str)
        for directory_obj in sorted_directory_lst:
            CatalogLevel,owner,CreatedTime,ModifiedTime,FileSizeBit = directory_info_dic[directory_obj]
            if CatalogLevel >MAXDEPTH:
                break
            DirectorySize,SizeUnit = convertSizeUnit(FileSizeBit, source='B', target='AUTO', return_unit=True)
            dir_stat_out.write('\t'.join([str(CatalogLevel),owner,CreatedTime,ModifiedTime,str(DirectorySize),SizeUnit,str(directory_obj)])+'\n')
    # 按照文件大小排序，输出top20大小的文件 # result_info
    #TOPNUMBER = 20
    sorted_result_info =  sorted(result_info, key=lambda x:x[-1], reverse=True)
    TheLargestTop_file = Path.joinpath(outdir, "TheLargestTop."+str(TOPNUMBER)+".files.tsv")
    with open(TheLargestTop_file,mode='wt',encoding='utf-8') as largest_out:
        header_str = 'FileName\tParentOfDirectory\tOwner\tCreatedTime\tModifiedTime\tFileSizeBit\tSizeUnit\n'
        largest_out.write(header_str)
        for info in sorted_result_info[0:TOPNUMBER]:
            FileName,ParentOfDirectory,owner,CreatedTime,ModifiedTime,FileSizeBit = info
            FileSize,SizeUnit = convertSizeUnit(FileSizeBit, source='B', target='AUTO', return_unit=True)
            largest_out.write('\t'.join([FileName,str(ParentOfDirectory),owner,CreatedTime,ModifiedTime,str(FileSize),SizeUnit])+'\n')


    # 用户文件占用总大小排序，输出所有用户的占用空间 # UserOccupancySize_dic
    
    sorted_user_lst = sorted(UserOccupancySize_dic.keys(), key=lambda user:UserOccupancySize_dic[user], reverse=True)
    Disk_Usage_file = Path.joinpath(outdir, "Disk_Usage.User.tsv")
    with open(Disk_Usage_file,mode='wt',encoding='utf-8') as user_out:
        header_str = 'User\tStorageSpaceOccupation\tSizeUnit\n'
        user_out.write(header_str)
        for user in sorted_user_lst:
            SizeBit = UserOccupancySize_dic[user]
            OccupancySize,SizeUnit = convertSizeUnit(SizeBit, source='B', target='AUTO', return_unit=True)
            user_out.write('\t'.join([user,str(OccupancySize),SizeUnit])+'\n')
    
if __name__ == "__main__":
    if sys.version[0] == "3":
        start_time = time.perf_counter()
    else:
        start_time = time.clock()
    main()
    if sys.version[0] == "3":
        end_time = time.perf_counter()
    else:
        end_time = time.clock()
    print("%s %s %s\n" % ("main()", "use", str(
        datetime.timedelta(seconds=end_time - start_time))))
