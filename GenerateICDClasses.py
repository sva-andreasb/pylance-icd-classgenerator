'''
generates Folder Structure for pylance

'''

import os
import shutil
import zipfile
import re
icdLocation = "C:\\IBM\\SMP"
jdkHierarchy = "Class Hierarchy (Java Platform SE 8 ).html"

shutil.rmtree(os.path.join(os.getcwd(),"classes"), ignore_errors=True)

def get_java_classname(file_name, baselocation):
    '''
    splits path into classpath and classname
    '''
    parts = file_name.split(baselocation+os.path.sep)[1].split(os.path.sep)
    returnpath = ''
    returnname = ''
    for part in parts:
        if '.class' in part:
            returnname = part.split('.class')[0] +".py"
        else:
            if returnpath:
                returnpath = returnpath + os.path.sep + part
            else:
                returnpath = part
    return returnpath, returnname
def makeDir(filename,location):
    classpath, classname = get_java_classname(filename, location)
    newPath = os.path.join(os.getcwd(),"classes",classpath)
    try:
        os.makedirs(newPath, exist_ok=True)
        with open(os.path.join(newPath,classname), "w") as f:
            #print(os.path.join(newPath,classname))
            f.write("")
            f.close()
    except:
        print('error on ' + str(os.path.join(newPath,classname)))
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
def get_jar_classes(jar_file):
    classes = []
    """prints out .class files from jar_file"""
    zf = zipfile.ZipFile(jar_file, 'r')
    try:
        lst = zf.infolist()
        for zi in lst:
            fn = zi.filename
            if fn.endswith('.class'):
                classes.append(str(os.path.sep).join(fn.split('/')))
    finally:
        zf.close()
    return classes


classDirs = []
classDirs.append(os.path.join(icdLocation,"maximo", "applications", "maximo", "businessobjects", "classes")) classDirs.append(os.path.join(icdLocation,"maximo", "applications", "maximo", "maximouiweb", "webmodule","WEB-INF","classes")) classDirs.append(os.path.join(icdLocation,"maximo", "applications", "maximo", "commonweb", "classes")) libDir = os.path.join(icdLocation,"maximo", "applications", "maximo", "lib")

i = 0
x = 0
with open(os.path.join(os.getcwd(),jdkHierarchy),"r") as f:
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

for classDir in classDirs:
    # r=root, d=directories, f = files
    for r, d, f in os.walk(classDir):
        for filename in f:
            if '.class' in filename:
                i += 1
                x += 1
                if i == 1000:
                    print(x)
                    i=0
                makeDir(os.path.join(r,filename),classDir)
for r, d, f in os.walk(libDir):
    for filename in f:
        if '.jar' in filename:
            classes = get_jar_classes(os.path.join(r,filename))
            for classe in classes:
                i += 1
                x += 1
                if i == 1000:
                    print(x)
                    i=0
                makeDir(os.path.join(r,classe),libDir)
print(x)