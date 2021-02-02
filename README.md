# LicensePlateRecognition 车牌识别
华南理工大学模式识别实践

记得**star一下**呀

README只列了框架，详情可以跳转[https://juejin.cn/post/6923916531965362184](https://juejin.cn/post/6923916531965362184)

## 最终效果图
<table width="100%" border="0">
	<tr align="center">
		<td><img src="https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/70e6257fff5a496aa70339770fa34839~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /></td>
		<td><img src="https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/4e77f9719f2d4fe89bab70ecce4a1cf0~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /></td>
	</tr>
	<tr align="center">
		<td><img src="https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1da03d94ca1544bb825f276deadb0c30~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /></td>
		<td><img src="https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/5e2d71f5406b4bcd8b91029b6446a35f~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /></td>
</table>

汽车图片来源于网络

## 设计思路

项目的编程环境为python3.7.7，编译器使用pycharm2019.3.4 x64，设计一个车牌识别系统，有GUI界面。选择一张有车牌的图片后，完成车牌定位、倾斜校正、字符分割，最后通过k-NN算法对车牌的字母和数字进行识别，将识别结果在GUI界面中显示出来。

### 车牌定位

### 字符分割

### 字符识别

### 特征描述

### k-NN分类算法

## 参考

[python cv2函数总结resize boxPoints minAreaRect](https://blog.csdn.net/Bismarckczy/article/details/88026806?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522158540891219725211943679%2522%252C%2522scm%2522%253A%252220140713.130056874..%2522%257D&request_id=158540891219725211943679&biz_id=0&utm_source=distribute.pc_search_result.none-task)

[Python-Tkinter图形化界面设计（详细教程 ）](https://blog.csdn.net/rng_uzi_/article/details/89792518#3.2)

[Python3+OpenCV2实现图像的几何变换:平移、镜像、缩放、旋转、仿射](https://blog.csdn.net/missyougoon/article/details/81092512?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task)