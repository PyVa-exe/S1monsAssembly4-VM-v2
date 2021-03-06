"""
Acc - Accumolator
Reg - Register
mem - Memory

16-Bit Maschine

set attr - set attr into Reg

add none - Acc = Acc + Reg
sub none - Acc = Acc - Reg
shg none - Acc = Acc shifted greater
shs none - Acc = Acc shifted smaller

lor none - Acc = Acc (logical or) Reg
and none - Acc = Acc (logical and) Reg
xor none - Acc = Acc (logical xor) Reg
not none - Acc = Acc (logical not)

lDA attr - Load mem at attr into Acc
lDR attr - Load mem at attr into Reg
sAD attr - Save Acc into mem at attr
sRD attr - Save Reg into mem at attr

lPA atrr - Load mem pointed to by mem at attr into Acc
lPR atrr - Load mem pointed to by mem at attr into Reg
sAP atrr - Save Acc into mem pointed to by mem at attr
sRP atrr - Save Reg into mem pointed to by mem at attr

out attr - outputs mem at attr
inp attr - inputs  mem at attr

lab attr - define lable
got attr - goto attr
jm0 attr - goto attr if Acc = 0
jmA attr - goto attr if Acc = Reg

jmG attr - goto attr if Acc > Reg (jmG for jump great)
jmL attr - goto atrr if Acc < Reg (jmL for jump less)

jmS attr - goto attr as subroutine (pc gets push to stack)
ret none - return from subroutine (stack gets pop to pc)

pha none - push Acc to stack
pla none - pull from stack to Acc


brk none - stops programm
clr none - clears Reg and Acc

putstr none - print the Acc as ascii


ahm none - allocate a number of word given by the Reg and put a pointer to the base into the Acc
fhm none - free a number of word given by the Reg at the address given by the Acc


plugin attr - runs plugin with name of attr


"""

import time
import glob

class cInt:
    def __init__(self, xInt = 0, xIntLimit = 65535):
        self.xInt = xInt
        self.xIntLimit = xIntLimit
        
        
    def Set(self, xNew):
        self.xInt = int(xNew) % self.xIntLimit
        
    def Add(self, xValue):
        self.Set(self.xInt + int(xValue))
        
        
    def Sub(self, xValue):
        self.Set(self.xInt - int(xValue))

    def __int__(self):
        return self.xInt
    
    
class cLine:
    def __init__(self, xInst = "", xAttr = None):
        self.xInst = xInst
        self.xAttr = xAttr
        
    def __str__(self):
        return "{: <10}{}".format(str(self.xInst), str(self.xAttr))
 
class cMain:
    def __init__(self):
        self.xFile = ""
        
        self.xBitSize = 16
        self.xIntLimit = 2 ** self.xBitSize 
        
        self.xReg = cInt(0, self.xIntLimit)
        self.xAcc = cInt(0, self.xIntLimit)
        
        #just to avoid confusion:
        #the heap is part of the memory and in this case it's the top half
        self.xHeapStartAddress = self.xIntLimit // 2        
        self.xHeapSize = self.xIntLimit - self.xHeapStartAddress
        
        #memory addresses allocated on the heap
        self.xHeapAlloc = [] 
        
        self.xMem = [cInt(0, self.xIntLimit) for i in range(self.xIntLimit)]
        
        self.xStack = []
                
        self.xProgrammIndex = 0
        self.xLables = {}
        
        self.xTotalIndex = 0

        #assign a pointer to the memory and stack to the plugin env
        #this work because when you copy a list in python, it will just copy a pointer to that list, which can also be modified
        self.xPluginEnv = {}
        self.xPluginEnv['mem']   = self.xMem
        self.xPluginEnv['stack'] = self.xStack
                
                                                


    
    def Structuring(self, xRawSource):
        #this function will take in the raw source and make it into a structure
        xLineStructureBuffer = []
        xLineIndex = 0
        xLineOffset = 0
        for xLineIterator in [x.strip().replace("  ", " ").split(" ") for x in xRawSource.split("\n") if x.replace(" ", "") != "" and x.strip()[0] != '"']:            
            xInst = xLineIterator[0]
            xAttr = xLineIterator[1] if len(xLineIterator) > 1 else None
            
            if xInst == "lab":
                if not xAttr is None:
                    self.xLables[xAttr] = str(xLineIndex - xLineOffset)
                    xLineOffset += 1
                
                else:
                    raise _Error("Attribute Error: " + " ".join(xLineIterator))
                
                
            else:
                xLineStructureBuffer.append(cLine(xInst = xInst, xAttr = xAttr))
        
            xLineIndex += 1
        
        return xLineStructureBuffer
        
    def Interpret(self):
        self.xLineStructures = self.Structuring(self.xFile)
                
        try:
            while self.xProgrammIndex < len(self.xLineStructures):
                                
                
                
                xLine = self.xLineStructures[self.xProgrammIndex]
                
                xInst = xLine.xInst
                xAttr = xLine.xAttr
                
                
                if xPrintAll:
                    print("{xCycleIndex: <10}{xInst: <10}:{xAttr}".format(xInst = xInst, xAttr = xAttr, xCycleIndex = self.xTotalIndex))
                                
                #execute inst
                if xInst == "set":
                    self.xReg.Set(int(xAttr))
                    
                elif xInst == "add":
                    self.xAcc.Add(self.xReg)
                
                elif xInst == "sub":
                    self.xAcc.Sub(self.xReg)
                
                elif xInst == "shg":
                    self.xAcc.Set(int(self.xAcc) * 2)
                    
                elif xInst == "shs":
                    self.xAcc.Set(int(self.xAcc) // 2)
                
                elif xInst == "lor":
                    self.xAcc.Set(int(self.xAcc) | int(self.xReg))
    
                elif xInst == "and":
                    self.xAcc.Set(int(self.xAcc) & int(self.xReg))
    
                elif xInst == "xor":
                    self.xAcc.Set(int(self.xAcc) ^ int(self.xReg))
    
                elif xInst == "not":
                    xAccBin = bin(int(self.xAcc))[2:]
                    xFixLenAccBin = "0" * (self.xBitSize - len(xAccBin)) + xAccBin
                    
                    
                    xInverted = []
                    for xI in xFixLenAccBin:
                        if xI == "0":
                            xInverted.append("1")
                        
                        elif xI == "1":
                            xInverted.append("0")

                    self.xAcc.Set(int("".join(xInverted), 2))
    
                    
            
                elif xInst == "lDA":
                    self.xAcc.Set(int(self.xMem[int(xAttr)]))
                
                elif xInst == "lDR":
                    self.xReg.Set(int(self.xMem[int(xAttr)]))
                
                elif xInst == "sAD":
                    self.xMem[int(xAttr)].Set(self.xAcc)
                
                elif xInst == "sRD":
                    self.xMem[int(xAttr)].Set(self.xReg)
     
                elif xInst == "lPA":
                    self.xAcc.Set(int(self.xMem[int(self.xMem[int(xAttr)])]))
                
                elif xInst == "lPR":
                    self.xReg.Set(int(self.xMem[int(self.xMem[int(xAttr)])]))
    
                elif xInst == "sAP":
                    self.xMem[int(self.xMem[int(xAttr)])].Set(int(self.xAcc))
                
                elif xInst == "sRP":
                    self.xMem[int(self.xMem[int(xAttr)])].Set(int(self.xReg))
    
                
                elif xInst == "out":
                    print(int(self.xMem[int(xAttr)]), file = xStdOut)
                
                elif xInst == "inp":
                    xInput = input(">>>")
                    self.xMem[int(xAttr)].Set(0 if xInput == "" else int(xInput))
                
                elif xInst == "got":
                    self.xProgrammIndex = int(self.xLables[str(xAttr)])
                    continue
                
                elif xInst == "jm0":
                    if int(self.xAcc) == 0:
                        self.xProgrammIndex = int(self.xLables[str(xAttr)])
                        continue
                    
                    
                elif xInst == "jmA":
                    if int(self.xAcc) == int(self.xReg):
                        self.xProgrammIndex = int(self.xLables[str(xAttr)])
                        continue
                  
                elif xInst == "jmG":
                    if int(self.xAcc) > int(self.xReg):
                        self.xProgrammIndex = int(self.xLables[str(xAttr)])
                        continue
                
                elif xInst == "jmL":
                    if int(self.xAcc) < int(self.xReg):
                        self.xProgrammIndex = int(self.xLables[str(xAttr)])
                        continue
    
                        
                elif xInst == "brk":
                    break
                    
                elif xInst == "clr":
                    self.xReg.Set(0)
                    self.xAcc.Set(0)
                
                elif xInst == "jmS":
                    self.xStack.append((self.xProgrammIndex + 1) * 2)
                    self.xProgrammIndex = int(self.xLables[str(xAttr)])
                    continue
                    
                    
                elif xInst == "ret":
                    if len(self.xStack) != 0:
                        self.xProgrammIndex = int(self.xStack.pop() / 2)
                        continue
                        
                elif xInst == "pha":
                    self.xStack.append(int(self.xAcc))
                    
                elif xInst == "pla":
                    if len(self.xStack) != 0:
                        self.xAcc.Set(int(self.xStack.pop()))
                
                elif xInst == "putstr":
                    print(chr(int(self.xAcc)), end = "", flush = True, file = xStdOut)
                    
                elif xInst == "ahm":
                    xAllocSize = int(self.xReg)
                    
                    #find the correct number of word in a row that are free
                    xBasePointer = None
                    for xHeapIndex in range(self.xHeapStartAddress, self.xHeapStartAddress + self.xHeapSize):
                        #terminate the loop if the xHeapIndex plus the size that the memory row need to by is greater than the heap itself
                        #because any check would be out of range and thus useless anyway
                        if xHeapIndex + xAllocSize > self.xHeapStartAddress + self.xHeapSize:
                            break

                        #otherwise check for a matching row
                        if all([xHeapIndex + xCheckIndex not in self.xHeapAlloc for xCheckIndex in range(xAllocSize)]):
                            xBasePointer = xHeapIndex
                            break
                    
                    if xBasePointer is None:
                        print("Program out of heap memory", file = StdOut)
                        exit()
                        
                    else:
                        for xAddrIndex in range(xBasePointer, xBasePointer + xAllocSize):
                            #append all the memory addresses to the alloc list, in order for them to properly freed 
                            self.xHeapAlloc.append(xAddrIndex)
                            
                            #and reset the address, just for safety
                            self.xMem[xAddrIndex].Set(0)
                        
                        #override the Acc to return the memory address to the user
                        self.xAcc.Set(xBasePointer)
                                                
                        
                elif xInst == "fhm":
                    xFreeSize = int(self.xReg)
                    xFreeBase = int(self.xAcc)
                    
                    for xFreeAddrIndex in range(xFreeBase, xFreeBase + xFreeSize):
                        if xFreeAddrIndex in self.xHeapAlloc: 
                            self.xHeapAlloc.remove(xFreeAddrIndex)
                        
                        self.xMem[xFreeAddrIndex].Set(0)
                        
                
                elif xInst == "plugin":
                    try:
                        xPluginName = xAttr.split("::")[0]
                        xMethodName = xAttr.split("::")[1]
                        
                        exec(str(xPluginName) + "." + str(xMethodName) + '(self.xPluginEnv)')

                    except NameError as E:
                        pass
                    
                    
                else:
                    print("Invaild command: " + str(xInst))
                    exit()
                
                self.xProgrammIndex += 1
                self.xTotalIndex += 1

        except KeyboardInterrupt:
            pass
        
        #print("Program took " + str(self.xTotalIndex) + " Cycles to complete")
                        
        
if __name__ == '__main__':
    import sys, os
    xArgv = sys.argv
    xPath = None
    
    if "--help" in xArgv:
        print("""
--help            display help
--file            input file
--stdout          redirect stdout
--PrintAll        print all executed instructions
--PluginPath      path to plugin file
        """)
        exit()
    
    
    try:
        xPath = xArgv[xArgv.index("--file") + 1]
        xFile = open(xPath, "r").read()
        
    except Exception:
        print("Error while loading file")
        exit()


        
    xStdOut = sys.stdout
    try:
        xStdOutPath = xArgv[xArgv.index("--stdout") + 1]
        xStdOut = open(xStdOutPath, "w")

        print("Writing to file with path: " + str(xStdOutPath))        
    except Exception: pass



    xPLocals  = {}
    xPGlobals = {}


    if "--PluginPath" in xArgv:
        try:            
            xPluginPath = xArgv[xArgv.index("--PluginPath") + 1]
            xPluginPaths = glob.glob(xPluginPath + "\\*.py")
            
            for xPathIter in xPluginPaths:
                xFileHandleIter = open(xPathIter)
                xFileHandle     = xFileHandleIter.read()
                xFileHandleIter.close()
                
                xPluginName = xPathIter.split("\\")[-1].split(".")[0]
                
                exec(xFileHandle, globals(), locals())

    
                
        except Exception as E:
            print("Error while loading Plugins:")
            print(E)
    
    
    xPrintAll = "--PrintAll" in xArgv
        
    cM = cMain()
    cM.xFile = xFile    
    
    try:
        cM.Interpret()
                
    except KeyError:
        print("Error: label not found\n    {}".format(str(cM.xLineStructures[cM.xProgrammIndex])))