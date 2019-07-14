# qzone photos downloader

qq空间照片下载器，支持遍历QQ号段，下载所有可访问到的相册。具体使用方式参见 [说明.doc](https://github.com/nianiaele/qzonePicClawer/blob/master/%E8%AF%B4%E6%98%8E.docx)文档

Web crawler for qzone photos. Support to travsere a range of account and download all possible ablums. 

## Environment
windows 7

## Built with
- [requests](https://2.python-requests.org/en/master/)
- [MySQL](https://www.mysql.com/)

## Usage
download the albums infomation
```powershell
python getinfo.py startQQ n
```
startQQ is the initial QQ account number for scanning

n is the number of account to be scanned

---
download the photos
```powershell
python downloader.py id n
```
id is the photo id in mysql

n is the number of photos to be downloaded
