import requests
import json
import os
import time
from 控制打印颜色 import *
from deal_mp4 import *
import re
import setting
from tqdm import tqdm
import login
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
threadPool = ThreadPoolExecutor(max_workers=10)
from  shutil import copyfile



#####伪造请求头
headers={
'Accept-Encoding':	'gzip, deflate, br',
'origin':'https://www.bilibili.com',
'Referer':	'https://www.bilibili.com',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0)  Gecko/20100101 Firefox/58.0'
}




#####搜索video列表
def serach_video(page=1,name=None):
    url='https://api.bilibili.com/x/web-interface/search/all/v2?context=&page={0}&order=&keyword={1}&duration=&tids_1=&tids_2=&__refresh__=true&highlight=1&single_column=0&jsonp=jsonp&callback='
    res=requests.get(url=url.format(page,name),headers=headers)
    text=res.text.replace('\\u003cem class=\\"keyword\\"\\u003e','').replace('\\u003c/em\\u003e','')
    content_json=json.loads(text)
    ###做字符串处理

    total=content_json['data']['pageinfo']['video']['total'] ####视频总数
    pages=content_json['data']['pageinfo']['video']['pages'] ####视频页数
    setting.total_page=pages####将值赋给全部变量
    setting.current_page=page
    sprint(0, 31, 0,'视频总数%s，视频总页数%s，当前查看页数%s\n'%(total,pages,page))
    result=content_json['data']['result']
    for line in result:
        if line['result_type']=='video':
            for i in range(1,len(line['data'])):
                sprint(0, 32, 0,'  %s:%s\n'%(i,line['data'][i-1]['title']))
            with open('video_list.txt','w',encoding='utf8') as f:
                f.write(json.dumps(line['data']))
                f.flush()

#####获取视频url
def get_video_url(index=None,data=None):
    session=get_session()
    video_url='https://www.bilibili.com/video/av'
    if index:
        with open('video_list.txt','r',encoding='utf8') as f:
            data =json.loads(f.read())[index-1]
    htm=session.get(url=video_url+str(data['aid']),headers=headers).text.replace(' ','').replace('\r','').replace('\n','')
    ####用re来筛需要的数据
    video_data=json.loads(re.findall('window.__playinfo__=(.*?)</script>',htm)[0])
    try:
        setting.video_type =video_data['data']['dash']['video'][0]['mimeType'].split('/')[-1]
        setting.video_url.append(video_data['data']['dash']['video'][0])
        setting.audio_url=video_data['data']['dash']['audio']
    except:
        setting.video_type=video_data['data']['accept_format'].split(',')[0]
        setting.video_url = video_data['data']['durl']
        setting.audio_url = []

    title=data['title'].replace('/','').replace('.','').replace(' ','')
    return title

####创建session
def get_session():
    session=requests.session()
    requests.utils.add_dict_to_cookiejar(session.cookies, setting.cookies)
    return session

#####下载视频内容
def video_content(url,i,name,type,limit):
    # print(i,type,limit)
    session=get_session()
    try:
        headers['Range']='bytes=%s'%limit
        res = session.get(url=url, headers=headers,stream=True)
        # print(res.headers['Content-Range'],limit)
        if limit in res.headers['Content-Range']:
            setting.video_dic[type][i] = res.content
            # print(i, type, int(res.headers['content-length']))
            return int(res.headers['content-length'])
        else:
            return video_content(url, i, name,type, limit)

    except:
        return video_content(url,i,name,type,limit)

###循环启用多线程
def while_thred(length,i,name,type,url):
    num=0
    while num < length:
        limit=''
        i += 1
        if length-num<setting.size:
            limit='{0}-'.format(num)
            num += length-num
        else:
            limit='{0}-{1}'.format(num, num + setting.size- 1)
            num += setting.size
        t = threadPool.submit(video_content, url, i, name,type,limit)
        setting.thread_dic[i] = t
    return i

####获取视频
def get_video(name):
    # for i in range(len(setting.video_list[0:-1])):
    setting.video_dic['mp3']={}
    setting.video_dic[setting.video_type] = {}
    i=0
    video_urls, audio_url = get_type_url()
    for j in range(len(video_urls)):
        i = while_thred(setting.video_url[j]['length'],i,name,setting.video_type,video_urls[j])
    if audio_url:
        i = while_thred(setting.audio_langth,i,name,'mp3',audio_url)

def get_type_url():
    video_url=[]
    audio_url=None
    if setting.video_type=='mp4':
        video_url.append(setting.video_url[0]['baseUrl'])
        audio_url=setting.audio_url[0]['baseUrl']
    else:
        for line in setting.video_url:
            video_url.append(line['url'])
        audio_url=None
    return video_url,audio_url

#####获取总大小
def get_video_audio_size(name):
    audio_r=None
    video_urls, audio_url=get_type_url()
    for i in range(len(video_urls)):

        video_r = requests.get(url=video_urls[i],headers=headers,stream=True)
        setting.video_url[i]['length'] =int(video_r.headers['content-length'])
        setting.video_langth += int(video_r.headers['content-length'])
    create_video_file(name, setting.video_type, setting.video_langth)

    if audio_url:
        audio_r = requests.get(url=audio_url, headers=headers,stream=True)
        setting.audio_langth = int(audio_r.headers['content-length'])
        create_video_file(name, 'mp3', setting.audio_langth)

####生成一样大小的文件
def create_video_file(name,type,langth):
    file_path=os.path.join(setting.video_path, name + '.' + type)
    if os.path.exists(file_path):
        os.remove(file_path)
    f = open(file_path, 'wb')
    f.truncate(langth)
    f.close()

####处理视频
def video_deal(name):
    sprint(0, 31, 0, '下载完成,视频处理中请等待......\n')
    ####合并声音和视频
    video_path=setting.video_path + '/{0}.{1}'.format(name, setting.video_type)
    if setting.video_type=='mp4':
        video_add_mp3(setting.video_path + '/{0}.{1}'.format(name, setting.video_type), setting.video_path + '/{}.mp3'.format(name))
        ####合并完后删除
        os.remove(setting.video_path + '/{}.mp3'.format(name))
    else:
        copyfile(video_path, name+'.'+setting.video_type)
    os.remove(video_path)

####写入视频音频文件
def write_video_audio(name):
    type_list=list(setting.video_dic.keys())
    for type in type_list:
        file_path=os.path.join(setting.video_path, name+'.'+type)
        f= open(file_path,'wb')
        keys=sorted(setting.video_dic[type].keys())
        for line in keys:
            f.write(setting.video_dic[type][line])
            f.flush()
        f.close()

#####调取获取video的方法,等待线程结束获取返回值
def dispatch_video(name):
    get_video(name)
    pbar=tqdm(total=setting.audio_langth+setting.video_langth)
    pbar.set_description(name)
    bone_list=setting.thread_dic
    reslt_num=0
    for item in as_completed(list(setting.thread_dic.values())):
        data=item.result()
        pbar.update(data)

###错误输入
def input_error():
    sprint(0, 31, 0, '输入错误')

#####获取当前页
def get_page(num=None,last_page=None,next_page=None):
    if num:
        setting.current_page=num
    elif next_page:
        setting.current_page+=1
    elif last_page:
        if last_page>1:
            setting.current_page -= 1

####选择菜单 控制交互
def common_func():
    sprint(0, 31, 0, '请选择操作\n')
    sprint(1, 30, 30, '  1:翻页 ')
    sprint(1, 30, 30, '2:下载 ')
    sprint(1, 30, 30, '3:退出程序\n')
    operate = sinput(0, 31, 0, '>>>>>:')
    if operate == '1':
        sprint(1, 30, 30, '1:输入页码 ')
        sprint(1, 30, 30, '2:上一页 ')
        sprint(1, 30, 30, '3:下一页 ')
        sprint(1, 30, 30, '4:退出程序\n')
        operate = sinput(0, 31, 0, '>>>>>:')
        if operate == '1':
            num = sinput(0, 31, 0, '页码>>>>>:')
            get_page(num=int(num))
        elif operate == '2':
            get_page(next_page=True)
        elif operate == '3':
            get_page(last_page=True)
        elif operate == '4':
            return False
        else:
            input_error()
    elif operate=='2':
        sprint(0, 31, 0, '请选择操作\n')
        sprint(1, 30, 30, '  1:输入视频序号 ')
        sprint(1, 30, 30, '2:退出程序\n')
        operate = sinput(0, 31, 0, '>>>>>:')
        if operate == '1':
            num = sinput(0, 31, 0, '序号>>>>>:')
            video(num)
            sprint(0, 31, 0, '视频已经完成下载处理\n')
            return False
        elif operate==2:
            return False
        else:
            input_error()
        return True
    elif operate == '3':
        return False
    else:
        input_error()
    return True

#####按步骤调取video执行函数
def video(num):
    title=get_video_url(index=int(num))
    get_video_audio_size(title)
    sprint(0, 31, 0, '视频总大小:{0}b\n'.format(setting.video_langth + setting.audio_langth))
    dispatch_video(title)
    write_video_audio(title)
    video_deal(title)













if __name__ == '__main__':
    setting.cookie=login.run()
    name = sinput(0, 31, 0, '输入关键词>>>>>:')
    serach_video(name=name)
    while True:
        tag=common_func()
        if not tag:break
        serach_video(page=setting.current_page, name=name)

