import cv2
import struct
import time
import serial


def VdoPrcs(vdo, path,h: int = 8, w: int = 8,fps:int=None,isBin:int=1,threshold:int=None):
    """
    not tested!!
    Process the video into specified size and style
    :param vdo: the path of the video file or the object of cv2
    :param path: the path of file that write the processed video
    :param h: the new height of the video
    :param w: the new width of the video
    :param fps: the new fps of the video
    :param isBin: weather processing the video into black-and-white style
    :param threshold: the threshold of the process above
    :return: None
    """
    VdoWtr=cv2.VideoWriter(path,cv2.VideoWriter_fourcc('X','V','I','D'), fps,(w,h))
    if type(vdo) == str:
        vdo = cv2.VideoCapture(vdo)
    sz = list(map(int, (vdo.get(cv2.CAP_PROP_FRAME_HEIGHT), vdo.get(cv2.CAP_PROP_FRAME_WIDTH))))
    if fps==None:
        fps=vdo.get(cv2.CAP_PROP_FPS)
    if vdo.isOpened():
        while 1:
            ret, frm = vdo.read()
            if not ret:
                break
            if isBin:
                frm = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
                ret, frm = cv2.threshold(frm, threshold, 255, cv2.THRESH_BINARY)
            frm = cv2.resize(frm, (w, h))
            VdoWtr.write(frm)

def img2arr(img, h: int, w: int, thr: int) -> list:
    """
    Turn each frame into an array of number.Notice that this function process the video column by column.
    :param img: obj of cv2
    :param h: the height of each frame
    :param w: the width of each frame 
    :param thr: the threshold of the process that turns the video into black-and-white style
    :return: a list.
    """
    col = 0
    lst = []
    for i in range(w):
        col = 0
        for j in range(h):
            col = col * 2 + int(img[j][i] / thr)
        lst.append(col)

    return lst


def Vdo2Arr(vdo, threshold: int = 127, newH: int = 8, newW: int = 8, isResz=1, isShow: int = 0) -> (list,float):
    """
    Turn the video into an array of number.Notice that this function process the video column by column.
    :param vdo: obj of cv2 or the path of the video file
    :param threshold: the threshold of the process that turns the video into black-and-white style
    :param newH: the new height of each frame
    :param newW: the new width of each frame
    :param isResz: whether to resize the video
    :param isShow: whether to preview/show the video
    :return: the list is the code of each frame.the float number is the fps of the video file.
    """
    if type(vdo) == str:
        vdo = cv2.VideoCapture(vdo)
    sz = list(map(int, (vdo.get(cv2.CAP_PROP_FRAME_HEIGHT), vdo.get(cv2.CAP_PROP_FRAME_WIDTH))))
    res = []
    if vdo.isOpened():
        while 1:
            ret, frm = vdo.read()
            if not ret:
                break
            frm = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
            ret, frm = cv2.threshold(frm, threshold, 255, cv2.THRESH_BINARY)
            if isResz:
                frm = cv2.resize(frm, (newW, newH))
                sz[0]=newH
                sz[1]=newW
            if isShow:
                cv2.imshow("pic", frm)
                cv2.waitKey(20)
            res.append(list(map(int, img2arr(frm, sz[0], sz[1], threshold))))
    return res,vdo.get(cv2.CAP_PROP_FPS)



print("Start processing...")
vdo_file ,fps= Vdo2Arr("Here is your video file path", 185,isShow=0)
ser = serial.Serial("the port of your mcu", 9600, timeout=99999, stopbits=1, bytesize=8)
i = 0
l = len(vdo_file)
print("Video fps:",fps)
input("Finished.Press Enter to start.")
while 1:
    send_data = vdo_file[i]  # 需要发送的串口包
    i += 1
    if i >= l:
        i = 0
    send_data = struct.pack("%dB" % (len(send_data)), *send_data)  # 解析成16进制
    if i % int(fps) == 0:
        print(i / fps, '  /  ', l / fps)
    ser.write(send_data)
    time.sleep(1/fps)
    ser.read()
