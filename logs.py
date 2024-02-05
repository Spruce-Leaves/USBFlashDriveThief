import time as t

class logs():
    def __init__(self):
        self.buffer = []

    def addBufferLog(self, logStr:str, time:bool=False):
        if logStr == False:
            pass
        else:
            if time:
                logStr = t.strftime("%H:%M:%S") + " " + logStr
            self.buffer.append(logStr)
            return None
    
    def addBufferLogs(self, *logList, time:bool=False):
        if len(logList) == 0:
            pass
        elif len(logList) == 1:
            self.addBufferLog(logList[0], time)
        else:
            newLogs = []
            logList[0] = t.strftime("%H:%M:%S") + " " + logList[0]
            for i in logList[1:]:
                newLogs.append(" " * 15 + i)
            newLogs = "\n".join(newLogs)
            self.buffer.append(newLogs)

    def delBufferlog(self, logIndex=-1):
        backValue = self.buffer.pop(logIndex)
        return backValue
    
    def delBufferlogs(self, start:int=-1, end:int=-1, step:int=-1):
        offset = 0
        bufferValueList = []
        for i in range(min(start, end), max(start, end), abs(step)):
            backValue = self.buffer.pop(i - offset)
            bufferValueList.append(backValue)
        return bufferValueList
    
    def clearBuffer(self):
        self.buffer.clear()
        return None
    
    def outputBufferLog(self, logIndex:int=-1):
        print(self.buffer[logIndex])

    def outputBufferLogs(self, strList:list=[]):
        strLen = 0
        for s in strList:
            strLen += len(s)

        for l in self.buffer:
            print(" " * strLen, l)

    def log(self, logStr:str="", time:bool=False):
        if time:
            logStr = t.strftime("%H:%M:%S") + " " + logStr
        else:
            pass
        print(logStr)

    def logs(self, *logList, time:bool=False):
        if len(logList) == 0:
            pass
        elif len(logList) == 1:
            self.addBufferLog(logList[0], time)
        else:
            newLogs = []
            logList[0] = t.strftime("%H:%M:%S") + " " + logList[0]
            for i in logList[1:]:
                newLogs.append(" " * 15 + i)
            newLogs = "\n".join(newLogs)

    