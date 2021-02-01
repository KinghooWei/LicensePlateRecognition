# LicensePlateRecognition
License plate recognition 车牌识别

记得**star一下**呀

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
车牌定位就是在图片中识别出哪个位置有车牌，是字符分割和字母数字识别的前提，是车牌识别系统的关键和难点。具体算法如下：

1. 对原始图像进行高斯模糊，减少噪点。

2. 提取图像边缘。首先将彩色图像转为灰度图gray，利用大核对灰度图进行开操作得到图像open，相当于对灰度图进行涂抹操作，将灰度图gray和开操作后的图像open按1：-1的比例融合得到图像add，以上操作可以将大面积灰度值相似的地方置黑，可以减少车灯、背景、地面、挡风玻璃等细节。接着使用canny算法对融合图像add提取边缘，得到图像canny。

<table width="100%" border="0">
	<tr align="center">
		<td><img src="https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/9625d89c3dca4f2a929b87a97ec11a69~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /><br>gray</td>
		<td><img src="https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1146bc7e0f5e494397dc4e917b2b89bb~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /><br>open</td>
	</tr>
	<tr align="center">
		<td><img src="https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/993ae37c2b4d40ecaf8b2909c8e3d0e9~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /><br>add</td>
		<td><img src="https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/275fd16f3047499cb38ee702a6f896ca~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /><br>canny</td>
	</tr>
    <tr align="center">
    <td colspan="2">提取图像边缘</td>
    </tr>
</table>

3. 使用横向长条作为核对边缘图像进行一次闭操作，得到图像close，相当于对边缘横向涂抹，因为一般视角车牌是宽大于高的矩形。再对图像close进行一次开操作，得到图像open2，消除较细的线条和不大的竖向线条，从而将车牌位置的连通区域独立出来。
 	 
<table width="100%" border="0">
	<tr align="center">
		<td><img src="https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/1c6da490be3247bd9c3a23af6672ddb8~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /><br>闭操作close</td>
		<td><img src="https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/aa69bf239f0a4804a6c571d84c2cc48b~tplv-k3u1fbpfcp-watermark.image" width="90%"  border=0 /><br>开操作open2</td>
	</tr>
    <tr align="center">
    <td colspan="2">对边缘进行闭操作和开操作</td>
    </tr>
</table>


4. 查找连通区域，通过最小外接矩形的宽高比2~5.5筛选合适的连通区域。

5. 将最小外接矩形图像旋转矫正，上下左右向外扩展一点范围，避免连通区域没能覆盖车牌造成影响。

6. 将连通区域原图转为HSV图像，确定图像的主要颜色，若不为蓝、黄、绿，则排除。按照3种颜色对车牌进行精细定位，缩小范围。

7. 再次通过图像宽高比2.2~5.3筛选合适的位置，至此车牌定位结束。
<div align="center">
    <img src="https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/8973cbba4d5b42ca994c944ed79f2bdd~tplv-k3u1fbpfcp-watermark.image" height = "100" alt=""/>
    <br>
    <p>车牌定位</p>
</div>

## 字符分割

字符分割连接车牌定位和字符识别两个步骤，起到承上启下的作用，准确的字符分割是准确识别字符的前提，具体算法如下：

1. 先将RGB图像转为灰度图，再转为二值图像，由于黄牌和绿牌的字符是黑色的，因此要将黄牌和绿牌的二值图像做反转处理。

2. 车牌的上边缘或下边缘有2颗铆钉，考虑到车牌字符一般为7位，理论上遍历每行像素，若黑白跳变次数大于14次，可以判断该行像素有字符的像素，予以保留，若小于等于14次，可以判断行像素没有字符的像素，将这一整行像素置黑，即可消除铆钉。考虑到车牌倾斜的可能性，项目中将这一阈值设定为8。

3. 将二值图像的像素值向x轴投射，白色像素越多，投射出的值越高，投射值低于设定阈值时，可以视为字符间隔。由于省市编号与其它编号距离较大，所以字符最大间隔可以视为省市编号与其它编号之间的间隔，再往数前一个间隔，可以得到车牌号的第一个字符。大间隔右边由于字符较多，所以通过连通区域面积最大的5个进行查早，再通过x坐标排序，从而得到其余字符，至此字符分割完成。
<div align="center">
    <img src="https://p1-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/c49889bcbd2f42d291634191f25a18e0~tplv-k3u1fbpfcp-watermark.image" height = "100" alt=""/>
    <br>
    <p>字符分割</p>
</div>

## 字符识别

### 特征描述

把每个字符的二值图像调整为32*64像素的二值图像，逐行读取像素值，从而得到2048维向量，此向量作为字符的特征。

### k-NN算法

在模式识别领域中，k-NN算法是一种用于分类和回归的非参数统计方法。在k-NN分类算法中，输入包含k个最接近的特征空间的训练样本，输出是一个分类族群。一个对象的分类是由其邻近样本占多数的类别确定的，k为正整数，通常为奇数。k个最邻近样本中最多的分类类别决定了赋予该对象的类别，若$k = 1$，则该对象的类别直接由最近的一个节点赋予。

k-NN算法是所有的机器学习算法中最简单的之一。k个最邻近样本都是已经正确分类的对象，虽然没要求明确的训练步骤，但这也可以当作是此算法的一个训练样本集。训练样本是多维特征空间向量，其中每个训练样本带有一个类别标签。算法的训练阶段只包含存储的特征向量和训练样本的标签。k-NN算法的缺点是对数据的局部结构非常敏感。

在分类阶段，k是一个常数，项目中选取$k = 7$。

一般情况下，可以用欧氏距离作为距离度量。在欧几里得空间中，点$x = (x_1,x_2,...,x_n)$和点$y = (y_1,y_2,...,y_n)$之间的欧式距离为

$$d(x,y) = \sqrt{(x_1-y_1)^2+(x_2-y_2)^2+...+(x_n-y_n)^2}$$

k-NN算法分类会在类别分布不均时出现缺陷，也就是说，出现频率较多的样本将会影响测试样本的预测结果。因为样本更多的类别更可能出现在测试点的K邻域，而测试点的属性又是通过k邻域内的样本计算出来的。解决这个缺点的方法之一是在进行分类时将样本到k个近邻点的距离考虑进去。k近邻点中每一个的分类都乘以与测试点之间距离的成反比的权重。

## 参考

[python cv2函数总结resize boxPoints minAreaRect](https://blog.csdn.net/Bismarckczy/article/details/88026806?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522158540891219725211943679%2522%252C%2522scm%2522%253A%252220140713.130056874..%2522%257D&request_id=158540891219725211943679&biz_id=0&utm_source=distribute.pc_search_result.none-task)

[Python-Tkinter图形化界面设计（详细教程 ）](https://blog.csdn.net/rng_uzi_/article/details/89792518#3.2)

[Python3+OpenCV2实现图像的几何变换:平移、镜像、缩放、旋转、仿射](https://blog.csdn.net/missyougoon/article/details/81092512?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task)