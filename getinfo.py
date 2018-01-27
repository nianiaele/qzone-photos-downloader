# -*- coding:utf-8 -*-

import json
import re
import requests
import pymysql
import datetime
import time
import random
import sys



def LongToInt(value):  # 由于int+int超出范围后自动转为long型，通过这个转回来
    if isinstance(value, int):
        return int(value)
    else:
        return int(value & sys.maxint)


def LeftShiftInt(number, step):  # 由于左移可能自动转为long型，通过这个转回来
    # if isinstance((number << step), long):
    #     return int((number << step) - 0x200000000L)
    # else:
        return int(number << step)


def getNewGTK(p_skey, skey, rv2):
    b = p_skey or skey or rv2
    a = 5381
    for i in range(0, len(b)):
        a = a + LeftShiftInt(a, 5) + ord(b[i])
        a = LongToInt(a)
    return a & 0x7fffffff


def getGTK():
    with open("cookie") as f:
        cookieStr = f.read()

    if re.search(r'p_skey=(?P<p_skey>[^;]*)', cookieStr):
        p_skey = re.search(r'p_skey=(?P<p_skey>[^;]*)', cookieStr).group('p_skey')
    else:
        p_skey = None
    if re.search(r'skey=(?P<skey>[^;]*)', cookieStr):
        skey = re.search(r'skey=(?P<skey>[^;]*)', cookieStr).group('skey')
    else:
        skey = None
    if re.search(r'rv2=(?P<rv2>[^;]*)', cookieStr):
        rv2 = re.search(r'rv2=(?P<rv2>[^;]*)', cookieStr).group('rv2')
    else:
        rv2 = None

    return getNewGTK(p_skey, skey, rv2)


def parseUrl2(url2Str,albumInfoDict,qqString):
    theJSON = json.loads(url2Str)
    theDate = theJSON['data']
    thePhotos = theDate['photos']

    photoList = []
    for key, value in thePhotos.items():
        for photoDict in value:

            newPhoto = {}
            Dict1 = photoDict['1']
            newPhoto['url'] = Dict1['url']
            newPhoto['width'] = Dict1['width']
            newPhoto['height'] = Dict1['height']

            newPhoto['picname'] = photoDict['picname']
            newPhoto['likecount'] = photoDict['likecount']
            newPhoto['commentcount'] = photoDict['commentcount']
            newPhoto['uploadTime'] = photoDict['uUploadTime']
            newPhoto['modifytime'] = photoDict['modifytime']
            newPhoto['shoottime'] = photoDict['shoottime']
            newPhoto['albumid'] = albumInfoDict['albumid']
            newPhoto['albumname'] = albumInfoDict['albumname']
            newPhoto['qqnum'] = qqString;

            photoList.append(newPhoto)

    # print(photoList)
    return photoList

# resultDict = parseUrl2(str,albumInfoDict1,qqString1)
# print(resultDict)

def parseUrl1(url1Str):
    theJSON = json.loads(url1Str)
    code = theJSON['code']
    if code !=0:
        print(str(code)+theJSON['message'])

        return code
    try:
        albumList = theJSON['data']['vFeeds']
    except KeyError:
        print("该用户没有相册")
        return -1;


    returnAlbumList = []

    for album in albumList:
        theAlbum = album['pic']
        allowaccess = theAlbum['allow_access']

        #如果相册不让访问，跳过
        if allowaccess == 0:
            continue

        newAlbum = {}
        newAlbum['albumid'] = theAlbum['albumid']
        newAlbum['albumname'] = theAlbum['albumname']
        newAlbum['albumnum'] = theAlbum['albumnum']

        returnAlbumList.append(newAlbum)

    return returnAlbumList

# returnList = parseUrl1(str1)
# print(returnList)

# 得到用于获取相册列表的url1，三个参数，分别为qq号字符串，g_tk字符串，最大显示相册数目
def getUrl1(qqNumber,g_tkStr,countStr=100):
    url = "https://mobile.qzone.qq.com/list?g_tk=237349236&format=json&list_type=album&action=0&res_uin=995878446&count=100"

    tkRegex = re.compile(r'(?<=g_tk=)\w+\b')
    countRegex = re.compile(r'(?<=count=)\w+\b')
    qqNumRegex = re.compile(r'(?<=res_uin=)\w+\b')

    url = tkRegex.sub(str(g_tkStr),url)
    url = countRegex.sub(str(countStr),url)
    url = qqNumRegex.sub(qqNumber,url)

    return url

# strnew = getUrl1('123456','999999999')
# print(strnew)


# 用于得到获取照片url的url2，共四个参数，分别为qq号字符串，g_tk字符串，albumid字符串，ps起始页数，pn最大返回页数
def getUrl2(qqnumber,g_tkStr,albumid,ps,pn=20):

    url = "https://h5.qzone.qq.com/webapp/json/mqzone_photo/getPhotoList2?g_tk=237349236&uin=1136438554&albumid=917cf071-c9fe-4c9d-a871-c48c0199e93b&ps=0&pn=20&password=&password_cleartext=0"

    qqRegex = re.compile(r'(?<=uin=)\w+\b')
    tkRegex = re.compile(r'(?<=g_tk=)\w+\b')
    albumIdRegex = re.compile(r'(?<=albumid=)[\w,-]+\b')
    psRegex = re.compile(r'(?<=ps=)\w+\b')
    pnRegex = re.compile(r'(?<=pn=)\w+\b')


    url = qqRegex.sub(qqnumber,url)
    url = tkRegex.sub(g_tkStr,url)
    url = albumIdRegex.sub(albumid,url)
    url = psRegex.sub(str(ps),url)
    url = pnRegex.sub(str(pn),url)

    return url

# str = getUrl2('9999999','24311111','2342222',42342)
# print(str)

#从cookie文件读取cookie
def get_cookie():
    with open('cookie','r') as f:
        cookies={}
        # line = f.read().split(';')
        for line in f.read().split(';'):
            name,value=line.strip().split('=',1)
            cookies[name]=value
        return cookies



#根据albumDict爬取一个相册的照片,三个参数，第一个是由parseUrl1函数获得的字典，qqnumber是正在采集的qq号，qn是最大每页显示照片数量
def oneAlbum(albumDict,qqnumber,pn=20):

    albumId = albumDict['albumid']
    albumName = albumDict['albumname']
    albumNum = albumDict['albumnum']

    # 照片请求次数
    requestTime = int(albumNum/pn)+1
    if albumNum%pn == 0:
        requestTime = requestTime - 1


    for i in range(requestTime):
        startPage = i*pn

        url2 = getUrl2(qqnumber, str(getGTK()), albumId, startPage, pn=20)

        print('新的照片请求...')
        content = requests.get(url2, headers=headers, cookies=get_cookie(),timeout=timeOutLimit)
        content.raise_for_status()

        try:
            photoList = parseUrl2(content.text, albumDict, qqnumber)
            storeIntoDB(photoList)
        except TypeError as e:
            print(e)




#根据qq号爬取一个人的照片
def oneQQ(qqNumber):

    print('正在采集 qq:'+qqNumber+' ...')

    gtkString = getGTK();

    url1 = getUrl1(qqNumber,gtkString)

    print('新的相册请求...')

    try:
        content = requests.get(url1, headers=headers, cookies=get_cookie(), timeout=timeOutLimit)
		content.raise_for_status()
    except requests.exceptions.ReadTimeout:
        print('相册信息请求超时，qq:'+qqNumber)
        print('放弃采集')
        return -1


    

    try:
        albumList = parseUrl1(content.text)
    except:
        print('url1: '+content.text)
        print('解析url1出现错误，放弃采集')
        return None

    #此处可以增加根据code判断不同问题
    if type(albumList) != list:

        if albumList == -4016:
            raise Exception('该qq号已被暂时查封，请更换qq号')
        elif albumList == -3000:
            raise Exception('模拟登陆失败，请检查cookie配置')

        print('放弃采集,qq:'+qqNumber)
        return

    for albumDict in albumList:
        try:
            oneAlbum(albumDict, qqNumber)
        except requests.exceptions.ReadTimeout:
            print("请求超时")
        # except TypeError as e:
        #     print('类型错误'+e)


    print('qq:'+qqNumber+' 采集完毕')

    return None


def storeIntoDB(photoList):

    conn = pymysql.connect(host=dbHost, user=dbUser, passwd=dbPasswd,
                           db=dbName, port=dbPort, charset=dbCharSet)
    # conn = pymysql.connect(host='localhost', user='root', passwd='123456',
    #                        db='qzone', port=3306, charset='utf8')
    cur = conn.cursor()

    for photo in photoList:
        url = photo['url']
        width = photo['width']
        height = photo['height']
        picname = photo['picname']
        likecount = photo['likecount']
        commentcount = photo['commentcount']
        uploadTime = photo['uploadTime']
        modifytime = photo['modifytime']
        shoottime = photo['shoottime']
        albumid =photo['albumid']
        albumname = photo['albumname']
        qqnum = photo['qqnum']

        gmt_create = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gmt_modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_deleted = 0

        print('照片名称：'+picname+' 正在插入数据库...')
        cur.execute("insert into qzone_photo (url,width,height,pic_name,liked_count,comment_count,upload_time,"
                    "modify_time,shoot_time,album_id,album_name,qq_number,gmt_create,gmt_modified,is_deleted )"
                    "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (url,width,height,picname,likecount,commentcount,uploadTime,modifytime,shoottime,albumid,
                     albumname,qqnum,gmt_create,gmt_modified,is_deleted))
        conn.commit()

    conn.close()

def readConfiguration():

    with open('configuration1.txt', 'r') as f:
        pzString = f.read()

    print(pzString)

    global timeOutLimit
    global maxSleepTime
    global dbHost
    global dbUser
    global dbPasswd
    global dbName
    global dbPort
    global dbCharSet
    global headers

    timeOutLimitRegex = re.compile(r'(?<=timeOutLimit:)\w+\b')
    maxSleepTimeRegex = re.compile(r'(?<=maxSleepTime:)\w+\b')
    dbHostRegex = re.compile(r"(?<=dbhost:)\w+\b")
    dbUserRegex = re.compile(r'(?<=dbuser:)\w+\b')
    dbPasswdRegex = re.compile(r'(?<=dbpasswd:)\w+\b')
    dbRegex = re.compile(r'(?<=db:)\w+\b')
    dbPortRegex = re.compile(r'(?<=port:)\w+\b')
    dbCharSetRegex = re.compile(r'(?<=charset:)\w+\b')
    headersRegex = re.compile(r'(?<=theheaders:).+$')

    timeOutLimit = int(timeOutLimitRegex.search(pzString).group())
    maxSleepTime = int(maxSleepTimeRegex.search(pzString).group())
    dbHost = dbHostRegex.search(pzString).group()
    dbUser = dbUserRegex.search(pzString).group()
    dbPasswd = dbPasswdRegex.search(pzString).group()
    dbName = dbRegex.search(pzString).group()
    dbPort = int(dbPortRegex.search(pzString).group())
    dbCharSet = dbCharSetRegex.search(pzString).group()
    headers = json.loads(headersRegex.search(pzString).group())


def start(startQQNum,count):
    for i in range(count):
        qq = str(startQQNum+i)

        oneQQ(qq)

        pauseTime = random.randint(0,maxSleepTime)
        print("暂停"+str(pauseTime)+"秒")
        time.sleep(pauseTime)

# readConfiguration()
#
# start(1136440300,100)


if __name__ == '__main__':

    startQQNumber = int(sys.argv[1])
    qqCount = int(sys.argv[2])

    print(startQQNumber)
    print(qqCount)
    readConfiguration()

    start(startQQNumber,qqCount)



# readConfiguration()
# start(1136440300,1000)

# 2676133033
#2215
# select count(distinct url) from qzone_photo
#1136438646

