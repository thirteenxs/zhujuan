import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import setting
import os
from 控制打印颜色 import *


class SVC:
    def __init__(self):
        self.url = 'https://passport.bilibili.com/login'

        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Firefox(firefox_options=options)
        self.driver.maximize_window()
        self.driverwait = WebDriverWait(self.driver, 5)
        self.email = setting.user
        self.password =setting.password
        self.location = {}
        self.size = {'width': 260, 'height': 160}
        self.BORDER = 40

    # def __del__(self):
    #     self.driver.close()

    def setAttribute(self, elementObj, attributeName, value):
        # 封装设置页面对象的属性值的方法
        # 调用JavaScript代码修改页面元素的属性值，arguments[0]－［2］分别会用后面的
        # element、attributeName和value参数值进行替换，并执行该JavaScript代码
        self.driver.execute_script("arguments[0].setAttribute (arguments[1],arguments[2])", elementObj, attributeName,
                                   value)

    def removeAttribute(self, elementObj, attributeName):
        # 封装删除页面元素属性的方法
        # 调用JavaScript代码删除页面元素的指定的属性，arguments[0]－［1］分别会用后面的
        # element、attributeName参数值进行替换，并执行该JavaScript代码
        self.driver.execute_script("arguments[0].removeAttribute(arguments[1])", elementObj, attributeName)


    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.driverwait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def open(self):
        """
        打开网页输入用户名密码
        :return: None
        """
        self.driver.get(self.url)
        email = self.driver.find_element_by_xpath('//*[@id="login-username"]')
        password = self.driver.find_element_by_xpath('//*[@id="login-passwd"]')
        # email = self.driverwait.until(EC.presence_of_element_located((By.ID, 'email')))
        # password = self.driverwait.until(EC.presence_of_element_located((By.ID, 'password')))
        email.send_keys(self.email)
        password.send_keys(self.password)
        submit = self.driver.find_element_by_class_name('btn-login')
        submit.click()


    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_geetest_image(self, name):
        """
        获取验证码图片 captcha.png
        :return: 图片对象
        """
        left, top, right, bottom = (1080, 292, 1300, 440)

        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(os.path.join(setting.img_path,name))
        return captcha

    def getImg(self):
        time.sleep(3)
        ele = self.driver.find_elements_by_tag_name('canvas')
        self.location = ele[1].location
        self.setAttribute(ele[2], 'style', 'display: none;')  # 移除小方框
        self.get_geetest_image('captcha_up.png')
        self.setAttribute(ele[1], 'style', 'display: none;')  # 移除上面图片
        self.removeAttribute(ele[3], 'style')  # 移除隐藏属性以显示地面图片
        self.get_geetest_image('captcha_down.png')
        self.removeAttribute(ele[1], 'style')
        time.sleep(0.5)
        self.removeAttribute(ele[2], 'style')
        time.sleep(0.5)
        self.setAttribute(ele[3], 'style', 'display: none;')

    def get_gap(self, image1, image2):
        """
        获取缺口偏移量
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return:
        """
        left = 0
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                        pixel1[2] - pixel2[2]) < threshold:

            return True
        else:
            # print(pixel1, pixel2)
            return False

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        list1 = []

        # 当前位移
        num=0
        while distance>1:
            x=random.uniform(0.3,0.8)*distance
            list1.append(x)
            distance-=x
        else:
            list1.append(distance)
        return list1

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
        # time.sleep(0.5)
        ActionChains(self.driver).release().perform()

    def start(self):
        # 输入用户名密码
        self.open()

    def crack(self):
        self.getImg()
        Image2 = Image.open(os.path.join(setting.img_path,'captcha_down.png'))
        Image1 = Image.open(os.path.join(setting.img_path,'captcha_up.png'))
        gap = self.get_gap(Image1, Image2)
        # print('缺口位置', gap)
        # 减去缺口位移
        gap-=1
        track = self.get_track(gap)
        # print('滑动轨迹', track)
        slider = self.get_slider()
        self.move_to_gap(slider, track)
        time.sleep(3)
        success=''
        try:
            success = self.driver.find_element_by_class_name('van-popover__reference')
        except:
            sprint(0, 31, 0, '登录失败，重新登陆\n')
        # 失败后重试
        if not success:
            time.sleep(0.1)
            self.crack()
        else:
            sprint(0, 31, 0, '登录成功\n')

    def get_cookie(self):
        login_cookies = self.driver.get_cookies()
        cookies = {}
        for c in login_cookies:
            cookies[c['name']] = c['value']
        return cookies





def run():
    sprint(0, 31, 0, '开始登录\n')
    svc = SVC()
    svc.start()
    svc.crack()
    cookies=svc.get_cookie()
    svc.driver.close()
    return cookies

