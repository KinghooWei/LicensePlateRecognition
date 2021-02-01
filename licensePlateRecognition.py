from tkinter import *
from tkinter.filedialog import *
from cv2 import *
from numpy import *
from PIL import ImageTk, Image
import operator


class recognition:
    # oriImage
    def open(self):
        img_path = askopenfilename(initialdir='./testImage', title='选择待识别图片',
                                   filetypes=[("jpg", "*.jpg"), ("png", "*.png")])
        if img_path:
            img = cv2.imdecode(fromfile(img_path, dtype=uint8), cv2.IMREAD_COLOR)

            self.show(img, 400, oriImg)

            colors, lisencePlates = self.getROI(img)
            for m in range(len(lisencePlates)):
                self.show(lisencePlates[m], 40, ROIImg)
                letters = self.getLetters(lisencePlates[m], colors[m])

                results = []
                for letter in letters:
                    feature = self.getFeature(letter)
                    result = self.sort(feature, trainingMat, labels, 5)
                    results.append(result)
                    # print(result)
                recogResult = ','.join(results)

                resultShow.configure(text=recogResult)

    def show(self, img, newheight, label):
        global oriTk, ROITk
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        height = img.height
        width = img.width

        scaleRatio = newheight / height
        newwidth = int(width * scaleRatio)
        img = img.resize((newwidth, newheight), Image.ANTIALIAS)
        if label == oriImg:
            self.oriTk = ImageTk.PhotoImage(image=img)
            label.configure(image=self.oriTk)
        elif label == ROIImg:
            self.ROITk = ImageTk.PhotoImage(image=img)
            label.configure(image=self.ROITk)

    def getROI(self, img):
        # oriImg = Image.fromarray(img)
        # imgHeight = oriImg.height
        # imgWidth = oriImg.width
        # 尺寸太大则缩小
        imgHeight, imgWidth = img.shape[:2]
        if imgHeight > 1000:
            scaleRatio = 1000 / imgHeight
            imgHeight = 1000
            imgWidth = int(imgWidth * scaleRatio)
            img = cv2.resize(img, (imgWidth, imgHeight), interpolation=cv2.INTER_AREA)

        oriImg = img  # 保存原图副本
        img = cv2.GaussianBlur(img, (3, 3), 0)  # 高斯模糊
        # print(img)
        gaussianImg = img  # 保存副本
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转灰度图
        # imshow("gray",img)
        kernel = ones((20, 20), uint8)
        imgOpen = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)  # 开操作，突出黑
        # imshow("open",imgOpen)
        img = cv2.addWeighted(img, 1, imgOpen, -1, 0)  # 图像融合
        # imshow("add",img)
        ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # 二值化
        img = cv2.Canny(img, 100, 200)  # canny算法查找边缘
        # imshow("canny",img)
        kernel = ones((4, 19), uint8)
        img = cv2.morphologyEx(img, MORPH_CLOSE, kernel)  # 闭操作，横向涂抹
        # imshow("close",img)
        # kernel = ones((4, 25), uint8)
        img = cv2.morphologyEx(img, MORPH_OPEN, kernel)  # 开操作，去除细线
        # imshow("open2",img)

        # 查找连通区域
        try:
            contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        except ValueError:
            image, contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 2000]  # 排除面积太小的连通区域
        print("number of big contours: ", len(contours))

        # 通过长宽比排除比例不适的连通区域
        rightRatioRects = []
        for cnt in contours:
            rect = cv2.minAreaRect(cnt)  # 最小内接矩形[(x_center, y_center),(w,h), theta]
            w, h = rect[1]
            if w < h:
                width, height = h, w
            else:
                width, height = w, h
            ratio = width / height
            if 2 < ratio < 5.5:
                rightRatioRects.append(rect)
                box = cv2.boxPoints(rect)
                # print(box)
                box = int0(box)
                # cv2.drawContours(gaussianImg, [box], 0, (0, 255, 0), 2)   #圈出来

        # imshow("img", gaussianImg)
        print("number of right ratio contours: ", len(rightRatioRects))

        # 对可能的区域进行旋转调整和扩大范围
        rotatedRects = []
        for rect in rightRatioRects:
            box = cv2.boxPoints(rect)
            w, h = rect[1]
            extraX = 5
            extraY = 10
            if w > h:  # 宽大于高，顺时针旋转
                width, height = w, h
                matRotate = cv2.getRotationMatrix2D((box[0][0], box[0][1]), rect[2], 1)
                img = cv2.warpAffine(oriImg, matRotate, (imgWidth + 100, imgHeight + 100))

                # 扩大范围
                if int(box[0][0]) - extraX < 0:
                    minX = 0
                else:
                    minX = int(box[0][0]) - extraX

                if int(box[0][0]) + int(width) + extraX > imgWidth + 99:
                    maxX = imgWidth + 99
                else:
                    maxX = int(box[0][0]) + int(width) + extraX

                if int(box[0][1]) - int(height) - extraY < 0:
                    minY = 0
                else:
                    minY = int(box[0][1]) - int(height) - extraY

                if int(box[0][1]) + extraY > imgHeight + 99:
                    maxY = imgHeight + 99
                else:
                    maxY = int(box[0][1]) + extraY

            else:  # 宽小于高，逆时针旋转
                width, height = h, w
                matRotate = cv2.getRotationMatrix2D((box[0][0], box[0][1]), -90 + rect[2], 1)
                img = cv2.warpAffine(oriImg, matRotate, (imgWidth + 100, imgHeight + 100))
                # imshow("rotate", img)
                # 扩大范围
                if int(box[0][0]) - extraX < 0:
                    minX = 0
                else:
                    minX = int(box[0][0]) - extraX

                if int(box[0][0]) + int(width) + extraX > imgWidth + 99:
                    maxX = imgWidth + 99
                else:
                    maxX = int(box[0][0]) + int(width) + extraX

                if int(box[0][1]) - extraY < 0:
                    minY = 0
                else:
                    minY = int(box[0][1]) - extraY

                if int(box[0][1]) + int(height) + extraY > imgHeight + 99:
                    maxY = imgHeight + 99
                else:
                    maxY = int(box[0][1]) + int(height) + extraY

            img = img[minY:maxY, minX:maxX]
            # imshow(str(rect), img)
            rotatedRects.append(img)

        # 利用颜色排除不是车牌的区域，并进行较精细定位
        colors = []
        lisencePlates = []

        for img in rotatedRects:
            green = yellow = blue = 0
            hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            row, col = hsvImg.shape[:2]
            pixelCount = row * col
            # print("pixel count: ", pixelCount)

            for i in range(row):
                for j in range(col):
                    H = hsvImg.item(i, j, 0)
                    S = hsvImg.item(i, j, 1)
                    V = hsvImg.item(1, j, 2)
                    if 15 <= H <= 30 and S >= 60 and V >= 45:
                        yellow += 1
                    elif 65 <= H <= 90 and S >= 15 and V >= 65:
                        green += 1
                    elif 100 <= H <= 120 and S >= 55 and V >= 40:
                        blue += 1
            if yellow > green and yellow > blue and yellow > pixelCount * 0.45:
                xl, xr, yh, yl = self.fineMap("yellow", hsvImg)
                img = img[yh:yl, xl:xr]
                h, w = img.shape[:2]
                if 2.2 < w / h < 5.3:
                    colors.append("yellow")
                    lisencePlates.append(img)
                    # imshow(str(img), img)
            if blue > yellow and blue > green and blue > pixelCount * 0.45:
                xl, xr, yh, yl = self.fineMap("blue", hsvImg)
                img = img[yh:yl, xl:xr]
                h, w = img.shape[:2]
                if 2.2 < w / h < 5.3:
                    lisencePlates.append(img)
                    colors.append("blue")
                    # imshow(str(img), img)
            if green > yellow and green > blue and green > pixelCount * 0.35:
                xl, xr, yh, yl = self.fineMap("green", hsvImg)
                img = img[yl - int((yl - yh) * 4 / 3):yl, xl:xr]
                h, w = img.shape[:2]
                if 2.2 < w / h < 5.3:
                    lisencePlates.append(img)
                    colors.append("green")
                    # imshow(str(img), img)
        print("num of lisence plate: " + str(len(lisencePlates)))
        return colors, lisencePlates

    # 精细定位
    def fineMap(self, color, hsvImg):
        if color == "yellow":
            limit1 = 15
            limit2 = 30
            limitS = 60
            limitV = 45
        elif color == "green":
            limit1 = 65
            limit2 = 90
            limitS = 15
            limitV = 65
        elif color == "blue":
            limit1 = 100
            limit2 = 120
            limitS = 55
            limitV = 40
        row_num, col_num = hsvImg.shape[:2]
        xl = col_num - 1
        xr = 0
        yh = row_num - 1
        yl = 0
        # col_num_limit = self.cfg["col_num_limit"]
        row_num_limit = row_num * 0.5 if color != "green" else row_num * 0.3  # 绿色有渐变
        col_num_limit = col_num * 0.3
        # 按行
        for i in range(row_num):
            count = 0
            for j in range(col_num):
                H = hsvImg.item(i, j, 0)
                S = hsvImg.item(i, j, 1)
                V = hsvImg.item(i, j, 2)
                if limit1 <= H <= limit2 and S >= limitS and V >= limitV:
                    count += 1
            if count > col_num_limit:
                if yh > i:
                    yh = i
                if yl < i:
                    yl = i
        # 按列
        for j in range(col_num):
            count = 0
            for i in range(row_num):
                H = hsvImg.item(i, j, 0)
                S = hsvImg.item(i, j, 1)
                V = hsvImg.item(i, j, 2)
                if limit1 <= H <= limit2 and S >= limitS and V >= limitV:
                    count += 1
            if count > row_num_limit:
                if xl > j:
                    xl = j
                if xr < j:
                    xr = j
        return xl, xr, yh, yl

    # 二值化，去铆钉，字符分割
    def getLetters(self, img, color):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转灰度图
        # 二值化
        if color == "blue":
            ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif color == "yellow" or color == "green":
            ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # 去铆钉
        rowNum, colNum = img.shape[:2]
        for i in range(rowNum):
            previousPixel = -1
            jump = 0
            for j in range(colNum):
                if previousPixel == -1:
                    previousPixel = img[i][j]
                else:
                    if previousPixel != img[i][j]:
                        jump += 1
                    previousPixel = img[i][j]
            if jump < 8:
                for j in range(colNum):
                    img[i][j] = 0

        # 字符分割
        accumulation = img.sum(axis=0)
        max, min = accumulation.max(axis=0), accumulation.min(axis=0)
        accumulation = (accumulation - min) / (max - min)
        # print(accumulation)

        successive = []
        intervalPre = []
        isPreviousLess = 0
        for m in range(len(accumulation)):
            if isPreviousLess:
                if accumulation[m] <= 0.2:
                    successive.append(m)
                else:
                    isPreviousLess = 0
                    intervalPre.append(successive)
                    successive = []
            else:
                if accumulation[m] <= 0.2:
                    isPreviousLess = 1
                    successive.append(m)

        # 找到最大间隔，为省市和编号之间的间隔
        intervalLen = 0
        for n in range(len(intervalPre)):
            if len(intervalPre[n]) > intervalLen:
                intervalLen = len(intervalPre[n])
                bigInterval = intervalPre[n]
                bigIntervalIndex = n

        # 找到最大间隔的前一个间隔，即省简称和字母之间的间隔
        if bigIntervalIndex >= 1:
            minIndex = self.findInterval(accumulation, intervalPre[bigIntervalIndex - 1])

        img = img[:, minIndex:]  # 截取字母区域
        contours, heirachy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 获取连通区域

        # 通过面积找到字母连通区域
        if color == "green":
            cntNum = 7
        else:
            cntNum = 6

        list = []
        for m in range(len(contours)):
            tuple = (m, cv2.contourArea(contours[m]))
            list.append(tuple)
        list.sort(key=lambda x: x[1], reverse=True)

        bigCnts = []  # 字母连通区域
        for n in range(cntNum):
            bigCnts.append(contours[list[n][0]])

        # 通过x坐标排序
        list = []
        for n in range(cntNum):  # 外接矩形
            x, y, width, height = cv2.boundingRect(bigCnts[n])
            tuple = (n, x)
            list.append(tuple)
        list.sort(key=lambda x: x[1])

        cnts = []  # 从左到右，字母连通区域
        for n in range(cntNum):
            cnts.append(bigCnts[list[n][0]])

        # 裁剪
        letters = []
        for cnt in cnts:
            x, y, width, height = cv2.boundingRect(cnt)
            letter = img[y:y + height, x:x + width]
            letter = cv2.resize(letter, (32, 64), interpolation=cv2.INTER_CUBIC)
            letters.append(letter)
            # imshow(str(cnt), letter)
        return letters
        # print(intervalPre)
        # print(minIndex)
        # imshow("img", gaussianImg)
        # imshow("img", img)

    def findInterval(self, accumulation, intervalPre):
        min = 1  # 最小值
        for m in range(len(intervalPre)):
            if accumulation[intervalPre[m]] < min:
                min = accumulation[intervalPre[m]]
                minIndex = intervalPre[m]
        return minIndex

    def getFeature(self, img):
        feature = []
        for i in range(64):
            for j in range(32):
                if img[i, j] == 0:
                    pixel = 0
                else:
                    pixel = 1
                feature.append(pixel)
        return feature

    # 构建训练集
    def createTrainSet(self):
        labels = []
        fileList = os.listdir('train')
        m = len(fileList)
        trainingMat = zeros((m, 2048))
        for i in range(m):
            fileName = fileList[i]
            labels.append(self.getNumLabel(fileName))
            ori = cv2.imread('train/%s' % fileName)  # 读取训练样本
            img_gray = cv2.cvtColor(ori, cv2.COLOR_BGR2GRAY)
            ret, img_bin = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 二值化
            # img = skewCorrection(img_bin)  # 倾斜校正
            img = self.crop(img_bin)
            trainingMat[i, :] = self.getFeature(img)
        return labels, trainingMat

    # 由图像名称得到数字类别
    def getNumLabel(self, file_name):
        fileStr = file_name.split('.')[0]  # 根据文件名中的字符"."进行切片
        numLabel = fileStr.split('_')[0]  # 根据文件切片结果中的"_"进行再次切片
        return numLabel

    # 裁剪伸缩
    def crop(self, img):
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        x, y, w, h = cv2.boundingRect(contours[0])
        img_crop = img[y:y + h, x:x + w]
        imgOut = cv2.resize(img_crop, (32, 64), interpolation=cv2.INTER_CUBIC)
        return imgOut

    # KNN算法
    def sort(self, imgFeature, trainingMat, labels, k):
        trainingSetSize = trainingMat.shape[0]
        diffMat = tile(imgFeature, (trainingSetSize, 1)) - trainingMat
        sqDiffMat = diffMat ** 2
        sqDistances = sqDiffMat.sum(axis=1)  # 每一行上元素之和
        distances = sqDistances ** 0.5
        sortedDistIndicies = distances.argsort()  # 从小到大排序，返回下标
        classCount = {}
        for i in range(k):
            voteLabel = labels[sortedDistIndicies[i]]  # 距离第i小的训练样本的类型
            classCount[voteLabel] = classCount.get(voteLabel, 0) + 1
        sortedClassCount = sorted(classCount.items(), key=operator.itemgetter(1), reverse=True)
        return sortedClassCount[0][0]


if __name__ == '__main__':
    global oriTk, ROITk
    choose = recognition()

    if os.path.exists('labels.npy') & os.path.exists('trainingMat.npy'):
        labels = load('labels.npy')
        trainingMat = load('trainingMat.npy')
        # print(labels)
        # print(trainingMat)
    else:
        labels, trainingMat = choose.createTrainSet()
        save('labels.npy', labels)
        save('trainingMat.npy', trainingMat)

    root = Tk()
    root.title("车牌识别")
    root.geometry('800x700')

    btnChoose = Button(root, text="选择图片", command=choose.open)
    btnChoose.place(x=20, y=10)

    oriImgLabel = Label(root, text="原图：", fg='black')
    oriImgLabel.place(x=25, y=50)

    oriImg = Label(root)
    oriImg.place(x=35, y=70)

    ROIImgLabel = Label(root, text="车牌定位：", fg='black')
    ROIImgLabel.place(x=25, y=500)

    ROIImg = Label(root)
    ROIImg.place(x=35, y=520)

    resultLabel = Label(root, text="识别结果：", fg='black')
    resultLabel.place(x=25, y=570)

    resultShow = Label(root, text="", fg='black')
    resultShow.place(x=35, y=590)

    root.mainloop()
