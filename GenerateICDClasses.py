'''
generates Folder Structure for pylance

'''

import os
import shutil
import re
import itertools

import subprocess
import concurrent.futures

TIMEOUT = 180

icdLocation = "/opt/IBM/SMP"
jdkHierarchy = "Class Hierarchy (Java Platform SE 8 ).html"

toDecompile = []

class Decompile(object):
    x = itertools.count()
    packre = re.compile("package ([\w\.]+);")
    classre = re.compile("public .*class (\w*)")
    interfacere = re.compile("public interface (\w*)")
    constantre = re.compile(".*public static final ([\w\[\]<>,]+ )(\w+) = \"*(.*)\"*;")
    functionre = re.compile(".*(public (?:[\w\[\]<>,]+ )*(\w*)\(.*\))(?: throws .*)* {")
    def __init__(self, filepath):
        self.jar = filepath
        self.process = None
        self.interrupt = False
        self.id = next(Decompile.x)
    def __call__(self):
        #print('decompiling ' + item)
        print(str(self.id) + " launched processes - " + str(self.jar.split(os.path.sep)[-1]))
        try:
            #self.process = subprocess.run(['java', '-jar','cfr-0.152.jar',self.jar], stdout=subprocess.PIPE, stderr=subprocess.PIPE,timeout=TIMEOUT, preexec_fn = os.setsid)
            self.temppath = os.path.join(os.getcwd(),"temp",self.jar.split(icdLocation+os.path.sep)[1]+".txt")
            if not os.path.exists(self.temppath):
                print(str(self.id) + " starting decompiler")
                os.makedirs(os.path.dirname(self.temppath), exist_ok=True)
                with open(self.temppath,"w") as outfile:
                    self.process = subprocess.run(['java', '-jar','procyon-decompiler-0.6.0.jar',self.jar], stdout=outfile, stderr=subprocess.PIPE,timeout=TIMEOUT, preexec_fn = os.setsid)
                    outfile.close()
                print(str(self.id) + " finished decompiler")
        except subprocess.TimeoutExpired:
            return "Timeout reached for " + self.jar
        except Exception as err:
            print("Exception " + str(type(err)) + ": ", err)
        #text = self.process.stdout.decode('utf-8')
        #return self.parseJar(text)
        return self.parseJar()
    def parseJar(self,text=""):
        #print(text)
        #packages["org.apache.tools.ant"]["AntClassLoader"]["function"][]
        packages = {}
        curPackage = ""
        curClass = ""
        print(str(self.id) + " parsing file")
        with open(self.temppath,"r") as infile:
            #for line in text.splitlines():
            for line in infile.readlines():
                if self.interrupt:
                    break
                #print(line)
                packmatch = self.packre.match(line)
                if packmatch:
                    curPackage = packmatch.group(1)
                    curClass = ""
                    #print("current Package is " + curPackage)
                    if curPackage not in packages:
                        packages[curPackage] = {}
                classmatch = self.classre.match(line)
                if classmatch:
                    curClass = classmatch.group(1)
                    #print("current class is " + curPackage + "." + curClass)
                    if curClass not in packages[curPackage]:
                        packages[curPackage][curClass] = {"function":{},"constants":{}}
                interfacematch = self.interfacere.match(line)
                if interfacematch:
                    curClass = interfacematch.group(1)
                    #print("current class is " + curPackage + "." + curClass)
                    if curClass not in packages[curPackage]:
                        packages[curPackage][curClass] = {"function":{},"constants":{}}
                if curPackage != "" and curClass != "":
                    #print('searching function in line ' + line)
                    functionmatch = self.functionre.match(line)
                    if functionmatch:
                        #print('found function ' + functionmatch.group(1))
                        function = functionmatch.group(2)
                        if function not in packages[curPackage][curClass]["function"]:
                            packages[curPackage][curClass]["function"][function] = []
                        packages[curPackage][curClass]["function"][function].append(functionmatch.group(1))
                    constantmatch = self.constantre.match(line)
                    if constantmatch:
                        constant = constantmatch.group(2)
                        packages[curPackage][curClass]["constants"][constant] = constantmatch.group(2) + " = \"" + constantmatch.group(1) + " " + constantmatch.group(3) + "\""
            infile.close()

            print(str(self.id) + " writing out file")
            retPacks = []
            #print(str(packages))
            if not self.interrupt:
                for pack in packages:
                    if pack != '':
                        path = pack.split(".")
                        newPath = os.path.join(os.getcwd(),"classes",*path)
                        os.makedirs(newPath, exist_ok=True)
                        for curclass in packages[pack]:
                            with open(os.path.join(newPath,curclass+".py"), "w") as f:
                                for constant in packages[pack][curclass]["constants"]:
                                    f.write(packages[pack][curclass]["constants"][constant] + "\n")
                                for function in packages[pack][curclass]["function"]:        
                                    f.write("def " + function + "():\n\'\'\'")
                                    for line in packages[pack][curclass]["function"][function]:
                                        f.write(line+"\n")
                                    f.write("\'\'\'\npass\n")
                                f.close()
                                print(str(self.id) + " finished file")
                            retPacks.append(pack+"."+ curclass)
                    else:
                        return str(self.id) + " Could not find pack " + str(packages)
            if retPacks:
                return str(self.id) + " Decompiled Jar " + str(retPacks)
            else:
                targetpath = None
                if "lib/" in self.jar:
                    targetpath = self.jar.split("lib/")[1].split(os.path.sep)
                if "classes/" in self.jar:
                    targetpath = self.jar.split("classes/")[1].split(os.path.sep)
                if targetpath:
                    file = targetpath.pop()
                    newPath = os.path.join(os.getcwd(),"classes",*targetpath)
                    os.makedirs(newPath, exist_ok=True)
                    with open(os.path.join(newPath,file.replace(".class",".py")), "w") as f:
                        f.write("")
                        f.close()
                        print(str(self.id) + " finished empty file")
                return str(self.id) + " Nothing in " + self.jar
    def interrupt(self):
        self.interrupt = True
        try:
            self.process.terminate()
        except AttributeError:
            pass
        print(str(self.id) + " Terminated decompile for " + self.jar)

def makeJavaDir(classpath,classname):
    classpath = (os.path.sep).join(classpath.split("."))
    newPath = os.path.join(os.getcwd(),"classes",classpath)
    try:
        os.makedirs(newPath, exist_ok=True)
        with open(os.path.join(newPath,classname+".py"), "w") as f:
            #print(os.path.join(newPath,classname))
            f.write("")
            f.close()
    except:
        print('error on ' + str(os.path.join(newPath,classname)))

def main():
    #shutil.rmtree(os.path.join(os.getcwd(),"classes"), ignore_errors=True)
    classDirs = []
    classDirs.append(os.path.join(icdLocation,"maximo", "applications", "maximo", "businessobjects", "classes"))
    classDirs.append(os.path.join(icdLocation,"maximo", "applications", "maximo", "maximouiweb", "webmodule","WEB-INF","classes"))
    classDirs.append(os.path.join(icdLocation,"maximo", "applications", "maximo", "commonweb", "classes"))
    libDir = os.path.join(icdLocation,"maximo", "applications", "maximo", "lib")

    i = 0
    x = 0
    with open(os.path.join(os.getcwd(),jdkHierarchy),"r",encoding="iso-8859-15") as f:
        jdkContent = f.read()
        result = re.search("<div class=\"contentContainer\">(.*)</div>",jdkContent,re.DOTALL)
        if result:
            liMatcher = re.compile("<li.*>(.+)<a.*><span.*>(.+)</span></a>")
            for line in result.group(1).split("\n"):
                lineresult = liMatcher.match(line)
                if lineresult:
                    makeJavaDir(lineresult.group(1),lineresult.group(2))
                    i += 1
                    x += 1
                    if i == 1000:
                        print(x)
                        i=0
        f.close()
    print("java", x)

    for classDir in classDirs:
        # r=root, d=directories, f = files
        for r, d, f in os.walk(classDir):
            for filename in f:
                if '.class' in filename and not ('Stub.' in filename or 'Remote.' in filename):
                    target = r.split(classDir+os.path.sep)[1].split(os.path.sep)
                    finalpath = os.path.join(os.getcwd(),"classes",*target,filename.replace(".class",".py"))
                    if not os.path.exists(finalpath):
                        toDecompile.append(os.path.join(r,filename))
                    #else:
                    #    print('file ' + finalpath + ' already exists')
                    i += 1
                    x += 1
                    if i == 1000:
                        print(x)
                        i=0
                    else:
                        print("file " + os.path.join(r,filename) + " took to long, ignoring")
    print("classes", x, len(toDecompile))
    for r, d, f in os.walk(libDir):
        for filename in f:
            if '.jar' in filename:
                toDecompile.append(os.path.join(r,filename))
                i += 1
                x += 1
                if i == 1000:
                    print(x)
                    i=0
    print("libs", x, len(toDecompile))
    #toDecompile.reverse()
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    #with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        tasks = [Decompile(jar) for jar in toDecompile]
        '''for task in tasks:
            task()'''
        for task, future in [(i, executor.submit(i)) for i in tasks]:
            try:
                print(future.result(timeout=TIMEOUT))
            except concurrent.futures.TimeoutError:
                if task:
                    print("this took too long... " + task.jar)
                    task.interrupt()
                else:
                    print("No Task found")
            except Exception as e:
                print("Exception " + str(type(e)) + ": ", e)
if __name__ == '__main__':
    main()
