import os

video_dic={}
total_page=1
current_page=1
video_url=[]
audio_url=[]
thread_dic={}
video_langth=0
audio_langth=0
size=5242880
base_path= os.path.dirname(__file__)
tmp_video_path=os.path.join(base_path,'tmp_video')
video_path=os.path.join(base_path,'video_list')
video_type='mp4'
img_path=os.path.join(base_path,'img')
pbar=None
user='17721147097'
password='sxx960729'
cookies={}

