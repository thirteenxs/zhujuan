import subprocess
import imageio
import os
from PIL import Image
import setting
from moviepy.editor import *
import os




def video2mp3(file_name):
    """
    将视频转为音频
    :param file_name: 传入视频文件的路径
    :return:
    """
    outfile_name = file_name.split('.')[0] + '.mp3'
    subprocess.call('ffmpeg -i ' + file_name
                    + ' -f mp3 ' + outfile_name, shell=True)


def video_add_mp3(file_name, mp3_file):
    """
     视频添加音频
    :param file_name: 传入视频文件的路径
    :param mp3_file: 传入音频文件的路径
    :return:
    """
    outfile_name = file_name.split('/')[-1]
    # outfile_name = '1.mp4'
    subprocess.call('ffmpeg -i ' + file_name
                    + ' -i ' + mp3_file +
                    ' -y -codec  copy  '
                    + outfile_name +' -loglevel quiet', shell=True)


def compose_gif(file_path):
    """
        将静态图片转为gif动图
        :param file_path: 传入图片的目录的路径
        :return:
    """
    img_paths = sorted([int(p[3:-4]) for p in os.listdir(file_path) if os.path.splitext(p)[1] == ".png"])
    img_paths = img_paths[:int(len(img_paths) / 3.6)]
    gif_images = []
    for path in img_paths:
        gif_images.append(imageio.imread('{0}/out{1}.png'.format(file_path, path)))
    imageio.mimsave("test.gif", gif_images, fps=30)


def compress_png(file_path):
    """
        将gif动图转为每张静态图片
        :param file_path: 传入gif文件的路径
        :return:
    """
    img_paths = [p for p in os.listdir(file_path) if os.path.splitext(p)[1] == ".png"]
    for filename in img_paths:
        with Image.open('{0}/{1}'.format(file_path, filename)) as im:
            width, height = im.size
            new_width = 150
            new_height = int(new_width * height * 1.0 / width)
            resized_im = im.resize((new_width, new_height))
            output_filename = filename
            resized_im.save('{0}/{1}'.format(file_path, output_filename))



def splic_mp4(name,type):
    # 定义一个数组
    L = []

    # 访问 video 文件夹 (假设视频都放在这里面)
    for root, dirs, files in os.walk(setting.tmp_video_path):
        # 按文件名排序
        files.sort()
        # 遍历所有文件
        for file in files:
            # 如果后缀名为 .mp4
            if os.path.splitext(file)[1] == '.%s'%type:
                # 拼接成完整路径
                filePath = os.path.join(root, file)
                # 载入视频
                # video = VideoFileClip(filePath)
                # 添加到数组
                # L.append(video)
                read_text=''
                with open(filePath, 'rb') as f:
                    read_text=f.read()
                with open(setting.video_path+"/%s.%s"%(name.replace('/','').replace('.',''),type),'ab') as f:
                    f.write(read_text)
                    f.flush()
                os.remove(filePath)
    # 拼接视频
    # final_clip = concatenate_videoclips(L)

    # 生成目标视频文件
    # final_clip.to_videofile("%s.mp4"%name, fps=24, remove_temp=False)

#
# if __name__ == '__main__':
#     # video2mp3(file_name='data-a.mp4')
#     # video_add_mp3(file_name='1.mp4', mp3_file='1.mp3')
#     # # compose_gif(file_path='merged')
#     # # compress_png(file_path='merged')
#     video_add_mp3('C:\\Users\86189\Desktop\\bilibili\\video_list\【海贼王极致踩点燃爆】点燃你的腺上激素，爽就完事了！！！.mp4'
#                   ,'C:\\Users\86189\Desktop\\bilibili\\video_list\【海贼王极致踩点燃爆】点燃你的腺上激素，爽就完事了！！！.mp3')

