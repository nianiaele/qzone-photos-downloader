import os
import re
import pymysql
import datetime
import requests
import sys


def readConfiguration():

    with open('configuration2.txt', 'r') as f:
        pzString = f.read()

    print(pzString)

    global timeOutLimit
    global dbHost
    global dbUser
    global dbPasswd
    global dbName
    global dbPort
    global dbCharSet
    global thePath

    timeOutLimitRegex = re.compile(r'(?<=timeOutLimit:)\w+\b')
    dbHostRegex = re.compile(r"(?<=dbhost:)\w+\b")
    dbUserRegex = re.compile(r'(?<=dbuser:)\w+\b')
    dbPasswdRegex = re.compile(r'(?<=dbpasswd:)\w+\b')
    dbRegex = re.compile(r'(?<=db:)\w+\b')
    dbPortRegex = re.compile(r'(?<=port:)\w+\b')
    dbCharSetRegex = re.compile(r'(?<=charset:)\w+\b')
    thePathRegex = re.compile(r"(?<=path:').+\b")

    timeOutLimit = int(timeOutLimitRegex.search(pzString).group())
    dbHost = dbHostRegex.search(pzString).group()
    dbUser = dbUserRegex.search(pzString).group()
    dbPasswd = dbPasswdRegex.search(pzString).group()
    dbName = dbRegex.search(pzString).group()
    dbPort = int(dbPortRegex.search(pzString).group())
    dbCharSet = dbCharSetRegex.search(pzString).group()
    thePath = thePathRegex.search(pzString).group()

def selectFromMysql(id):



    cur = conn.cursor()

    sql = "select id,url,qq_number,is_downloaded from qzone_photo where id="+str(id)

    cur.execute(sql)

    result = cur.fetchone()

    return result

def downloadPhoto(result):


    id = result[0]
    url = result[1]
    qqNumber = result[2]
    isDownloaded = result[3]

    if isDownloaded == b'\x01':
        print("id:"+str(id)+"已被下载过，放弃下载")
        return None

    print('正在下载照片id:' + str(id))

    oneQQPath = thePath+'\\'+str(qqNumber)

    if os.path.isdir(oneQQPath) != True:
        os.makedirs(oneQQPath)

    os.chdir(oneQQPath)

    savePath = oneQQPath+'\\'+str(id)+".jpg"

    photo = requests.get(url,timeout=timeOutLimit)

    with open(savePath, "wb") as f:
        for chunk in photo:
            f.write(chunk)

    gmt_download = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "update qzone_photo set is_downloaded=1, gmt_downloaded ="+str(gmt_download)+" where id="+str(id)
    cur = conn.cursor()
    cur.execute("update qzone_photo set is_downloaded=1, gmt_downloaded =%s where id=%s",(gmt_download,id))

    conn.commit()
    print("照片id："+str(id)+" 下载完成")

    return None


readConfiguration()
print(os.path.exists(thePath))




if __name__ == '__main__':

    if os.path.exists(thePath) != True:
        raise Exception('配置下载路径不存在！')

    os.chdir(thePath)

    startNumber = int(sys.argv[1])
    count = int(sys.argv[2])

    conn = pymysql.connect(host=dbHost, user=dbUser, passwd=dbPasswd,
                           db=dbName, port=dbPort, charset=dbCharSet)

    for i in range(count):
        theId = startNumber+i
        result = selectFromMysql(theId)
        try:
            downloadPhoto(result)
        except requests.exceptions.ConnectionError as e:
            print(e)

    conn.close()


# if os.path.exists(thePath) != True:
#     raise Exception('配置下载路径不存在！')
#
# os.chdir(thePath)
#
#
# conn = pymysql.connect(host=dbHost, user=dbUser, passwd=dbPasswd,
#                        db=dbName, port=dbPort, charset=dbCharSet)
#
# result = selectFromMysql(80544)
# downloadPhoto(result)
#
#
# conn.close()
