# -*- coding: utf-8 -*-
#Author：哈士奇说喵
from selenium import webdriver
import os
import sys,time
import time
from PIL import Image,ImageEnhance
import pytesser.pytesser as pytesser

#shift+tab多行缩进(左)
reload(sys)
PostUrl = "http://www.zhihu.com"

driver=webdriver.Chrome()

while 1:#sb登录系统，即使输对所有消息还是登不进去的，需要登录两次及以上
	time.sleep(3)
	driver.get(PostUrl)
	try:
		elem_code = driver.find_element_by_class_name('Input')
		if elem_code == None:
			print 'this is not rectify page continue'
			continue
	except:
		continue

	#-------------------对验证码进行区域截图，好吧，这方法有点low------------------
	driver.get_screenshot_as_file('screen_shot.png')#比较好理解
	im =Image.open('screen_shot.png')
	box = (545, 238, 624, 279)  #设置要裁剪的区域
	region = im.crop(box)     #此时，region是一个新的图像对象。
	#region.show()#显示的话就会被占用，所以要注释掉
	region.save("image_code.jpg")

	#-------------------------------------------------------------------

	#--------------ImageGrab.grab()直接可以区域截图，但是有bug，截图不全-------
	'''
	bbox = (780, 0, 1020, 800)
	img = ImageGrab.grab()
	img.save("E:\image_code.jpg")
	img.show()
	'''
	#-------------------------手动输入验证码：适用范围更广，但不够方便------------------------------
	'''
	response = opener.open(CaptchaUrl)
	picture = response.read()
	with open('e:/image.jpg', 'wb') as local:
		local.write(picture)
	# 保存验证码到本地

	#------------对于不能用pytesser+ocr进行识别，手动打开图片手动输入--------
	# 打开保存的验证码图片 输入
	#SecretCode = raw_input('please enter the code: ')
	#----------------------------------------------------------------------
	'''

	#--------------------图片增强+自动识别简单验证码-----------------------------
	#time.sleep(3)防止由于网速，可能图片还没保存好，就开始识别
	def image_file_to_string(file):
		cwd = os.getcwd()
		try :
			os.chdir("pytesser")
			return pytesser.image_file_to_string(file)
		finally:
			os.chdir(cwd)

	im=Image.open("image_code.jpg")
	imgry = im.convert('L')#图像加强，二值化
	sharpness =ImageEnhance.Contrast(imgry)#对比度增强
	sharp_img = sharpness.enhance(2.0)
	sharp_img.save("image_code.jpg")
	#http://www.cnblogs.com/txw1958/archive/2012/02/21/2361330.html
	#imgry.show()#这是分布测试时候用的，整个程序使用需要注释掉
	#imgry.save("E:\\image_code.jpg")

	code= image_file_to_string("../image_code.jpg")#code即为识别出的图片数字str类型
	print code
	#打印code观察是否识别正确


	#----------------------------------------------------------------------


	elem_code.send_keys(code)
	click_login = driver.find_element_by_class_name('Button')
	click_login.click()