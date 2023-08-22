import sys
import os
import socket
import threading
import time
import re
import urllib
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QProgressBar, QVBoxLayout, QWidget, QLabel, \
    QTextBrowser, QFileDialog,  QListWidget, QMessageBox, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import platform

if platform.system() == "Darwin":
    # macOS
    default_save_path = os.path.expanduser("~/Downloads")
elif platform.system() == "Windows":
    # Windows
    default_save_path = os.path.expanduser("~/Desktop")
else:
    default_save_path = os.path.expanduser("~")


class ServerThread(QThread):
    update_signal = pyqtSignal(str)

    def run(self):
        self.start_server()

    # 监听广播的函数
    def listen_for_broadcast(self):
        server_ip = '0.0.0.0'
        broadcast_port = 5001

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((server_ip, broadcast_port))

        while True:
            data, addr = server_socket.recvfrom(8192)
            decoded_data = data.decode('utf-8')
            # 打印接收到的数据包内容

            if decoded_data.startswith("Looking for peers from "):
                local_ip = self.get_local_ip()
                if local_ip:
                    device_name = platform.node()
                    response_message = f"{device_name} - {local_ip}"
                    if addr[0] == local_ip:  # 检查地址是否是本机局域网IP
                        response_message = f"{device_name}(本机设备) - {local_ip}"
                    server_socket.sendto(response_message.encode(), addr)

    # 获取本机局域网IP地址的函数
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            print("获取IP地址失败：", e)
            return None

    # 处理客户端连接的函数
    def handle_client(self, client_socket, client_address, save_folder):
        message = f"连接来自: {client_address}"
        self.update_signal.emit(message)

        # 接收文件名长度和文件名
        file_name_len_bytes = client_socket.recv(4)
        file_name_len = int.from_bytes(file_name_len_bytes, byteorder='big')

        file_name_bytes = client_socket.recv(file_name_len)
        encoded_file_name = file_name_bytes.decode()

        # 解码文件名
        decoded_file_name = urllib.parse.unquote(encoded_file_name)

        # 保存文件的完整路径
        save_path = os.path.join(save_folder, decoded_file_name)

        # 创建并打开文件，接收文件内容
        with open(save_path, 'wb') as f:
            while True:
                data = client_socket.recv(8192)
                if not data:
                    break
                f.write(data)

        message = f"文件 '{decoded_file_name}' 接收完成，保存在：{save_path}"
        self.update_signal.emit(message)

        client_socket.close()

    # 启动文件接收服务器
    def start_server(self):
        self.update_signal.emit("等待连接...")

        # 启动广播监听线程
        broadcast_thread = threading.Thread(target=self.listen_for_broadcast)
        broadcast_thread.start()

        local_ip = self.get_local_ip()
        if local_ip:
            self.update_signal.emit(f"本机局域网IP地址: {local_ip}")
        else:
            self.update_signal.emit("无法获取局域网IP地址。")

        server_ip = local_ip
        server_port = 12347

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((server_ip, server_port))
        server_socket.listen(1)
        self.update_signal.emit("等待连接...")

        while True:
            while True:
                client_socket, client_address = server_socket.accept()
                threading.Thread(target=self.handle_client,
                                 args=(client_socket, client_address, default_save_path)).start()

class FileTransferThread(QThread):
    update_signal = pyqtSignal(str, int)

    def __init__(self, file_path, server_ip, server_port):
        super().__init__()
        self.file_path = file_path
        self.server_ip = server_ip
        self.server_port = server_port

    def run(self):
        self.send_file()

    def send_file(self):
        file_name = os.path.basename(self.file_path)
        encoded_file_name = urllib.parse.quote(file_name)  # 编码文件名

        file_size = os.path.getsize(self.file_path)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_ip, self.server_port))

        client_socket.send(len(encoded_file_name).to_bytes(4, byteorder='big'))
        client_socket.send(encoded_file_name.encode())

        # client_socket.send(len(file_name).to_bytes(4, byteorder='big'))
        # client_socket.send(file_name.encode())

        total_bytes_sent = 0
        with open(self.file_path, 'rb') as f:
            data = f.read(8192)
            while data:
                client_socket.send(data)
                total_bytes_sent += len(data)
                progress = (total_bytes_sent / file_size) * 100
                progress_message = f"传输进度: {progress:.2f}%"
                self.update_signal.emit(progress_message, progress)
                data = f.read(8192)

        client_socket.close()
        self.update_signal.emit("文件发送完成", 100)

class ScanThread(QThread):
    scan_finished = pyqtSignal(list)

    def __init__(self, device_brand):
        super().__init__()
        self.device_brand = device_brand
        self.running = True  # 标志来控制线程的运行状态

    def run(self):
        while self.running:  # 持续循环扫描
            responses = self.send_broadcast()
            self.scan_finished.emit(responses)
            time.sleep(1)  # 等待1秒再进行下一次扫描

    def stop(self):
        self.running = False  # 停止线程运行

    def send_broadcast(self):
        broadcast_ip = '255.255.255.255'
        broadcast_port = 5001

        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        device_brand = "YourDeviceBrand"  # 设置你的设备品牌名称
        message = f"Looking for peers from {device_brand}"
        broadcast_socket.sendto(message.encode('utf-8'), (broadcast_ip, broadcast_port))

        responses = []
        broadcast_socket.settimeout(5)  # 设置超时时间，避免阻塞太久
        while True:
            try:
                data, addr = broadcast_socket.recvfrom(8192)
                responses.append(data.decode())
            except socket.timeout:
                break

        broadcast_socket.close()
        return responses

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File-Transfer")
        self.setGeometry(100, 100, 400, 400)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.main_tab = QWidget()

        # Main Tab
        self.main_layout = QVBoxLayout(self.main_tab)
        self.server_text_browser = QTextBrowser(self.main_tab)
        self.file_label = QLabel("选择要发送的文件:", self.main_tab)
        #self.file_button = QPushButton("选择文件", self.main_tab)
        self.progress_bar = QProgressBar(self.main_tab)
        self.server_ip_label = QLabel("服务器IP地址:", self.main_tab)
        self.scan_result_list = QListWidget(self.main_tab)

        self.server_ip_label_choose = QLabel("已选设备：", self.main_tab)
        self.server_ip_input = QLineEdit(self.main_tab)
        self.server_ip_input.setPlaceholderText("请选择或者输入设备IP地址")
        self.send_button = QPushButton("发送文件", self.main_tab)
        self.drag_label = QLabel("点击 或 将文件拖拽至此区域上传", self.main_tab)
        self.drag_label.setAlignment(Qt.AlignCenter)
        self.drag_label.setStyleSheet("border: 2px dashed #ccc; padding: 20px;")
        self.drag_label.mousePressEvent = self.open_file_dialog  # 连接点击事件
        self.main_layout.addWidget(self.drag_label)


        self.setAcceptDrops(True)  # 启用拖放功能
        self.statusBar().showMessage("File-Transfer Version 1.0    Author:fjc")

        self.main_layout.addWidget(self.server_text_browser)
        self.main_layout.addWidget(self.server_ip_label)
        self.main_layout.addWidget(self.scan_result_list)
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(self.server_ip_label_choose)
        ip_layout.addWidget(self.server_ip_input)
        self.main_layout.addLayout(ip_layout)
        #self.main_layout.addWidget(self.server_ip_input)
        self.main_layout.addWidget(self.progress_bar)
        self.main_layout.addWidget(self.file_label)
        self.main_layout.addWidget(self.drag_label)
#        self.main_layout.addWidget(self.file_button)
        self.main_layout.addWidget(self.send_button)
        self.main_tab.setLayout(self.main_layout)

        self.layout.addWidget(self.main_tab)
        self.central_widget.setLayout(self.layout)

        self.server_thread = None
        self.file_transfer_thread = None
        self.scan_thread = None

#        self.file_button.clicked.connect(self.select_file)
        self.send_button.clicked.connect(self.send_file)

        self.start_scan()
        self.start_server()
        self.scan_result_list.itemClicked.connect(self.select_scan_result)

    def open_file_dialog(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"已选择文件: {os.path.basename(file_path)}")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.selected_file = file_path
            self.file_label.setText(f"已选择文件: {os.path.basename(file_path)}")
            event.accept()
        else:
            event.ignore()

    def start_server(self):
        self.server_text_browser.clear()
        self.server_thread = ServerThread()
        self.server_thread.update_signal.connect(self.update_server_text_browser)
        self.server_thread.start()

    def stop_server(self):
        if self.server_thread:
            self.server_thread.terminate()

    def update_server_text_browser(self, message):
        self.server_text_browser.append(message)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.selected_file = file_path
            self.file_label.setText(f"已选择文件: {os.path.basename(file_path)}")

    def send_file(self):

        if not hasattr(self, "selected_file"):
            QMessageBox.critical(self, "错误", "未选择文件")
            return

        server_ip = self.server_ip_input.text()
        server_ip = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', server_ip)
        if not server_ip:
            QMessageBox.critical(self, "错误", "未选择设备")
            return

        self.send_button.setEnabled(False)
        self.drag_label.setEnabled(False)

        self.progress_bar.setValue(0)
        self.file_transfer_thread = FileTransferThread(self.selected_file, server_ip.group(), 12347)
        self.file_transfer_thread.update_signal.connect(self.update_file_progress)
        self.file_transfer_thread.finished.connect(self.enable_file_buttons)
        self.file_transfer_thread.start()

    def update_file_progress(self, message, progress):
        self.statusBar().showMessage(message)
        self.progress_bar.setValue(progress)

    def enable_file_buttons(self):
        self.send_button.setEnabled(True)
        self.drag_label.setEnabled(True)

    def start_scan(self):
        if self.scan_thread is None or not self.scan_thread.isRunning():

            device_brand = "YourDeviceBrand"  # 设置你的设备品牌名称
            self.scan_thread = ScanThread(device_brand)
            self.scan_thread.scan_finished.connect(self.update_scan_text_browser)
            self.scan_thread.start()
            # 设置浅灰色外边框样式
            border_style = "border: 1px solid #333;"  # 使用较浅的灰色
            background_color = "#f8f8f8"  # 更浅的灰色背景
            self.scan_result_list.setStyleSheet(
                f"QListWidget {{ background-color: {background_color}; border: none; {border_style} }}"
                "QListWidget::item { border-bottom: 1px solid #000; padding: 3px; }"
                "QListWidget::item:nth-child(even) { background-color: #e0e0e0; }"
                "QListWidget::item:nth-child(odd) { background-color: #f0f0f0; }"
                "QListWidget::item:last-child { border-bottom: none; }"
                "QListWidget::item:selected { background-color: #0078d4; color: white; }"
            )

    def update_scan_text_browser(self, responses):
        self.scan_result_list.clear()
        for response in responses:
            self.scan_result_list.addItem(response)

    def select_scan_result(self, item):
        selected_text = item.text()
        ip_address = selected_text.split(' - ')[-1]  # 提取IP地址部分
        self.server_ip = ip_address
        self.server_ip_input.setText(ip_address)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
