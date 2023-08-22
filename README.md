# File-Transfer
## 软件介绍

​	本软件File-Transfer旨在实现跨平台，局域网内文件快速传输，文件传输速度不受CS架构中服务器带宽限制，采用用户直连。传输速度理论上只受本地路由器等硬件限制，最高可跑满带宽，传输速度30M-60M。

## 文件说明

* 文档共有四个文件：
<img width="207" alt="image-20230822103147279" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/494b14cd-f418-466e-b837-0d9d7a4e6989">

1. <img width="122" alt="image-20230822103303979" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/e306afe8-38d0-4b5d-afdb-ef471948bb34">为程序源码，本软件使用python语言编写，其中只使用到第三方库PyQt

2. <img width="172" alt="image-20230822103627327" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/c5ff99e7-c404-4bf1-ba37-a4a3a0ab75bc">若电脑为MacBook，且CPU为M系列（M1和M2），使用该软件

3. <img width="160" alt="image-20230822104045142" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/1ba379d1-cb9f-42b8-b224-59653f7dcaf3">若电脑为MacBook，且CPU为Inte系列，使用该软件

4. <img width="153" alt="image-20230822104134003" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/7d50976c-9395-4a61-8bec-b14e25b6b5fd">若电脑为WIndows，且CPU为64位，使用该软件

## 使用说明

* **软件安装**

安装方式一：按照文件说明直接将软件拖动到桌面即可

安装方式二：mac电脑可以讲软件拖动至finder中的application中

* **软件使用**

1. **软件界面介绍**

<img width="400" alt="image-20230822104508719" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/20bd651a-7c45-45dc-b947-4dc7173b1b95">

第一个显示框为当前软件运行状态信息，软件初始化会显示本机局域网中的ip；

第二个显示框`服务器IP地址：`为同一个局域网中的其余设备，其中自己设备将在后面括号中显示`xxxx-（本机设备）`的字样，以区分本机和其余设备；

第三个输入框`已选设备`可以通过点击`服务器IP地址：`列表中的设备自动填充，也可以手动输入

第四个输入框`选择要发送的文件：`可以通过点击和拖拽的方式选择发送文件

进度条和底部显示栏会显示传输百分比

2. **软件使用步骤**

​	1）首先需要发送方和接收方在同一个局域网（WI-FI）下，并且都处于软件打开的状态

​	2）等待软件扫描，发送方单击接收方的IP<img width="298" alt="image-20230822105445145" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/0ed56cfd-641b-4d7a-86c4-d8ac7daf5383">，<img width="298" alt="image-20230822105526897" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/f546aece-702f-4676-9531-0e31e85e046a">自动填充接收方的IP信息，或者手动输入接收方IP；

​	3）<img width="365" alt="image-20230822105853244" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/dd41b745-3f2f-47c9-806d-768a1ae41a77">通过点击该区域，或者将文件拖拽至该区域实现文件上传，上传成功后<img width="181" alt="image-20230822110359692" src="https://github.com/one-lucky-pig/File-Transfer/assets/66020383/9f30e6bf-c98e-467d-a2d3-c0cc2ff393d1">会显示上传文件。

​	4）点击发送文件成功发送，==**苹果电脑传送文件会自动保存在`下载`文件夹中，Windows电脑会自动保存在`桌面`。**==
