import re
import subprocess
import sys

from PyQt5.QtChart import QChart, QChartView, QScatterSeries, QValueAxis, QLineSeries
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGroupBox, QCheckBox, QFormLayout, QSpinBox, \
    QDoubleSpinBox, QLabel, QLineEdit, QHBoxLayout, QPushButton, QSizePolicy, QSpacerItem, QSplitter, QTableWidget, \
    QFileDialog, QTableWidgetItem


# QLineEdit  单行文本
# QVBoxLayout  创建垂直布局
# QSplitter 可以拖动的分隔条


class WorkerThread(QThread):
    dataReady = pyqtSignal(list)
    result = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def set_parameters(self, paras):
        self.paras = paras

    def run(self):
        if self.paras is not None:
            mtz_shelc = self.paras[0]
            temp_tangent_method_cb = self.paras[1]
            strong_reflections_spin = self.paras[2]
            trials_spin = self.paras[3]
            iteration_spin = self.paras[4]
            resolution_cutoff_spin = self.paras[5]
            fraction = self.paras[6]
            temp_refine_heavy_atoms_cb = self.paras[7]
            cctr = self.paras[8]
            num_heavy_atoms_input = self.paras[9]
            heavy_atom_input = self.paras[10]
            wavelength = self.paras[11]
            filename = self.paras[12]
            script_path2 = '/ssd2/code_python/pythonProject/pdb7_38_3mei/exp-test/38_3mei/run_dsas.sh'
            process_2 = subprocess.Popen(['bash', script_path2, mtz_shelc, temp_tangent_method_cb,
                                          strong_reflections_spin, trials_spin,
                                          iteration_spin, resolution_cutoff_spin,
                                          fraction, temp_refine_heavy_atoms_cb,
                                          cctr, num_heavy_atoms_input, heavy_atom_input,
                                          wavelength, filename],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # output_2, error_2 = process_1.communicate()
            # 持续读取输出
            # 初始化一个标志以指示何时开始提取数据

            start_extraction = False
            # 初始化一个列表来存储提取的数据
            result = []
            acc = []
            files = []
            results = []
            while True:
                # 读取一行输出
                outputt = process_2.stdout.readline()
                output = outputt.decode('utf-8')
                print(output)
                # 如果输出为空且进程已结束，则退出循环
                # if "completed successfully" in output and process_2.poll() is not None:
                if  process_2.poll() is not None:
                    break
                # 打印输出
                if output:
                    line = output.strip()
                    # 如果行包含"the number of multiplicity point"
                    if "the number of multiplicity point" in line:
                        # 设置标志以开始提取数据
                        start_extraction = True
                    # 如果标志已设置且行包含相关数据
                    elif start_extraction and line.strip() != "" and "top best" not in line:
                        # 从行中提取相关数据并存储它
                        data = line.strip().split()  # 使用 strip() 去除行末的空白字符
                        # 假设您想要第一列和第四列的数据
                        result.append((float(data[0]), float(data[3])))
                        self.dataReady.emit(result)
                        # 如果行包含"top best"，则停止提取数据
                    elif "top best 10 CC is :" in line:
                        start_extraction = False
                        acc.append(line.strip("top best 10 CC is :"))
                    elif "Logical Name: recover" in line:
                        files.append(line.split()[-1].split('.')[0])

            # 等待进程结束并获取返回码
            process_2.wait()
            for file, acc_value in zip(files, acc):
                results.append([file, acc_value])
            self.result.emit(results)


class MyApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.filename = ''

    def initUI(self):
        layout = QVBoxLayout()

        # Create splitter to divide window into left and right sections
        splitter = QSplitter()
        layout.addWidget(splitter)

        # Left section
        left = QWidget()
        left_layout = QVBoxLayout(left)


        # First line: Mtz input, Browse button
        first_line_layout = QHBoxLayout()
        # input 文本
        mtz_label = QLabel("MTZ Input:")
        self.mtz_input = QLineEdit()
        self.mtz_input.setStyleSheet("background-color: yellow;")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browseFile)
        first_line_layout.addWidget(mtz_label)
        first_line_layout.addWidget(self.mtz_input)
        first_line_layout.addWidget(browse_button)
        left_layout.addLayout(first_line_layout)

        # Second line: Heavy Atom, Number of Heavy Atoms in ASU, and Buttons
        second_line_layout = QHBoxLayout()

        self.heavy_atom_input = QLineEdit()
        self.heavy_atom_input.setFixedWidth(80)
        self.heavy_atom_input.setStyleSheet("background-color: yellow;")
        self.num_heavy_atoms_input = QLineEdit()
        self.num_heavy_atoms_input.setFixedWidth(80)

        self.num_heavy_atoms_input.setStyleSheet("background-color: yellow;")

        second_line_layout.addWidget(QLabel("Heavy Atom:"))
        second_line_layout.addWidget(self.heavy_atom_input)
        second_line_layout.addSpacing(100)
        second_line_layout.addWidget(QLabel("Number of Heavy Atoms in ASU:"))

        second_line_layout.addWidget(self.num_heavy_atoms_input)
        second_line_layout.addSpacing(100)
        second_line_layout.addWidget(QLabel("Wavelength:"))

        self.wavelength = QDoubleSpinBox()
        # 设置范围为0到99999
        self.wavelength.setRange(0, 99999)
        # 设置小数位数为4
        self.wavelength.setDecimals(4)
        second_line_layout.addWidget(self.wavelength)
        spacer_item = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        second_line_layout.addItem(spacer_item)
        left_layout.addLayout(second_line_layout)

        # third

        third_line_layout = QHBoxLayout()
        # input 文本
        work_label = QLabel("Work directory:")
        self.work_input = QLineEdit()
        # self.work_input.setFixedWidth(500)
        self.work_input.setStyleSheet("background-color: yellow;")
        work_button = QPushButton("Browse")
        work_button.clicked.connect(self.browseDirectory)
        third_line_layout.addWidget(work_label)
        third_line_layout.addWidget(self.work_input)

        third_line_layout.addWidget(work_button)
        left_layout.addLayout(third_line_layout)
        # Add left section to the splitter
        splitter.addWidget(left)

        # Right section
        right = QWidget()
        right_layout = QVBoxLayout(right)

        # Run and Stop Buttons
        run_button = QPushButton("Run")
        stop_button = QPushButton("Stop")
        # 连接按钮点击事件
        run_button.clicked.connect(self.startTask)

        self.workerThread = WorkerThread()
        self.workerThread.dataReady.connect(self.updateScatter)

        stop_button.clicked.connect(self.stopScript)
        right_layout.addWidget(run_button)
        right_layout.addWidget(stop_button)

        # Adjust sizes of buttons
        for button in [run_button, stop_button]:
            button.setMaximumHeight(self.heavy_atom_input.sizeHint().height())

        # Add right section to the splitter
        splitter.addWidget(right)

        self.setLayout(layout)
        self.setWindowTitle('DSAS —— dual-space algorithm for anomalous substructures')

        # Second part: Experimental information
        # Experimental Information Group
        # Second part: Experimental information
        # Experimental Information Group
        exp_info_group = QGroupBox("Experimental Information")
        exp_info_group.setAlignment(Qt.AlignCenter)

        exp_info_layout = QVBoxLayout()

        # Add f(+) and sigF(+) in one row with input length 50
        self.f_plus_line = QLineEdit(alignment=Qt.AlignCenter)
        # self.f_plus_line.setFixedWidth(200)
        self.sigF_plus_line = QLineEdit(alignment=Qt.AlignCenter)
        # self.sigF_plus_line.setFixedWidth(200)

        line1 = QHBoxLayout()
        # spacer_item = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        # lablef =QLabel("f(+):")
        # lablef.setAlignment()
        line1.addWidget(QLabel("F(+)/I(+):"))

        line1.addWidget(self.f_plus_line)
        # # line1.addSpacing(20)
        # spacer_item = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        line1.addWidget(QLabel("sigF(+)/sigI(+):"))
        line1.addWidget(self.sigF_plus_line)
        # line1.addSpacing(200)
        line1.addItem(spacer_item)
        exp_info_layout.addLayout(line1, 1)

        # Add f(-) and sigF(-) in one row with input length 50
        self.f_minus_line = QLineEdit(alignment=Qt.AlignCenter)
        # self.f_minus_line.setFixedWidth(200)
        self.sigF_minus_line = QLineEdit(alignment=Qt.AlignCenter)
        # self.sigF_minus_line.setFixedWidth(200)
        line2 = QHBoxLayout()
        line2.addWidget(QLabel("F(-)/I(-):  "))
        line2.addWidget(self.f_minus_line)
        line2.addWidget(QLabel("sigF(-)/sigI(-):  "))
        line2.addWidget(self.sigF_minus_line)

        line2.addItem(spacer_item)
        exp_info_layout.addLayout(line2, 2)

        # Add Space Group with input length 50

        line3 = QHBoxLayout()

        # Set alignment to left
        line3.setAlignment(Qt.AlignHCenter)

        # Add QLabel "Space Group"
        space_group_label = QLabel("Space Group:")
        line3.addWidget(space_group_label)

        # Add a spacer item to create a fixed space between the QLabel and QLineEdit
        # spacer_item = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        # Add QLineEdit "self.space_group_line"
        self.space_group_line = QLineEdit()

        self.space_group_line.setFixedWidth(100)
        line3.addWidget(self.space_group_line)
        line3.addItem(spacer_item)
        # Add the QHBoxLayout to the QVBoxLayout with stretch factor 3
        exp_info_layout.addLayout(line3, 3)

        # Add Cell Parameters with input length 50
        self.a_line = QLineEdit()

        self.b_line = QLineEdit()
        self.c_line = QLineEdit()
        self.alpha_line = QLineEdit()
        self.beta_line = QLineEdit()
        self.gamma_line = QLineEdit()
        for line_edit in [self.a_line, self.b_line, self.c_line, self.alpha_line, self.beta_line, self.gamma_line]:
            line_edit.setFixedWidth(80)
        line4 = QHBoxLayout()
        line4.addWidget(QLabel("Cell Parameters:"))
        line4.addWidget(QLabel("a:"))
        line4.addWidget(self.a_line)
        line4.addWidget(QLabel("b:"))
        line4.addWidget(self.b_line)
        line4.addWidget(QLabel("c:"))
        line4.addWidget(self.c_line)
        line4.addWidget(QLabel("alpha:"))
        line4.addWidget(self.alpha_line)
        line4.addWidget(QLabel("beta:"))
        line4.addWidget(self.beta_line)
        line4.addWidget(QLabel("gamma:"))
        line4.addWidget(self.gamma_line)
        line4_item = QSpacerItem(600, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
        line4.addItem(line4_item)
        exp_info_layout.addLayout(line4, 4)

        exp_info_group.setLayout(exp_info_layout)
        exp_info_group.setAlignment(Qt.AlignCenter)
        layout.addWidget(exp_info_group)

        # 水平布局
        third_layout = QHBoxLayout()

        # Left part: Automated parameter setting
        auto_param_group = QGroupBox("Automated Parameter Setting")

        self.auto_param_layout = QFormLayout()  # 将auto_param_layout定义为类的属性
        self.tangent_method_cb = QCheckBox("Use Tangent Method", checked=True)
        # 显示隐藏strong_reflections_spin
        # self.tangent_method_cb.stateChanged.connect(self.showExtraControl)
        self.refine_heavy_atoms_cb = QCheckBox("Refine Heavy Atoms with BP3")
        self.strong_reflections_spin = QSpinBox()
        self.strong_reflections_spin.setRange(0, 99999)  # 设置范围为 0 到 99999
        self.trials_spin = QSpinBox()
        self.trials_spin.setRange(0, 99999)  # 设置范围为 0 到 99999
        self.iteration_spin = QSpinBox()
        self.iteration_spin.setRange(0, 99999)  # 设置范围为 0 到 99999
        self.resolution_cutoff_spin = QDoubleSpinBox()
        # 设置范围为0到99999
        self.resolution_cutoff_spin.setRange(0, 99999)
        # 设置小数位数为4
        self.resolution_cutoff_spin.setDecimals(4)
        self.fraction = QDoubleSpinBox()
        # 设置范围为0到99999
        self.fraction.setRange(0, 99999)
        # 设置小数位数为4
        self.fraction.setDecimals(4)

        self.auto_param_layout.addRow(self.tangent_method_cb)
        self.auto_param_layout.addRow("Number of Strong Reflections:", self.strong_reflections_spin)
        self.auto_param_layout.addRow("Number of Trials:", self.trials_spin)
        self.auto_param_layout.addRow("Number of Iteration:", self.iteration_spin)
        self.auto_param_layout.addRow("High-Resolution Cutoff (Å):", self.resolution_cutoff_spin)
        self.auto_param_layout.addRow("Fraction of weak reflection:", self.fraction)
        self.auto_param_layout.addRow(self.refine_heavy_atoms_cb)
        auto_param_group.setLayout(self.auto_param_layout)
        auto_param_group.setAlignment(Qt.AlignCenter)
        third_layout.addWidget(auto_param_group)
        layout.addLayout(third_layout)
        # Right part: Results
        result_group = QGroupBox("Results")
        result_group.setAlignment(Qt.AlignCenter)
        result_layout = QHBoxLayout()
        # 创建散点图
        self.chart = QChart()
        self.chartView = QChartView(self.chart)
        # self.chartView.setMinimumWidth(550)
        layout.addWidget(self.chartView)
        # for value in range(10, 300):
        #     scatter.append(value, random.random() * 100)

        # 创建散点数据
        self.scatter = QScatterSeries()
        self.scatter.setName("DSAS")

        # self.scatter.setMarkerShape(QScatterSeries.MarkerShapeCircle)
        # self.scatter.setBrush(Qt.blue)
        # self.scatter.setPen(Qt.blue)

        self.scatter.setMarkerSize(8)
        # self.scatter.setMarkerShape(QScatterSeries.MarkerShapeCircle)
        pen = self.scatter.pen()
        pen.setColor(Qt.blue) #QColor(135, 206, 250)pen.setColor(Qt.blue)
        pen.setWidth(1)
        self.scatter.setPen(pen)
        self.chart.addSeries(self.scatter)

        # 创建横坐标轴

        self.axis_x = QValueAxis()
        self.axis_x.setTickCount(5)
        self.axis_x.setRange(0, 400)

        self.axis_x.setLabelFormat("%d") #横轴值设为整数
        self.axis_x.setMinorTickCount(1) #添加子刻表线

        self.axis_x.setTitleText("Trials")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)  # 将横坐标轴添加到图表中

        # 创建纵坐标轴
        self.axis_y = QValueAxis()
        self.axis_y.setTickCount(7)
        self.axis_y.setRange(10, 40)
        self.axis_y.setTitleText("CC/%")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)  # 将纵坐标轴添加到图表中

        # 关联散点系列和坐标轴
        self.chart.addSeries(self.scatter)
        self.chart.setAxisX(self.axis_x, self.scatter)  # 将横坐标轴与散点系列关联
        self.chart.setAxisY(self.axis_y, self.scatter)  # 将纵坐标轴与散点系列关联
        # 将默认的坐标轴隐藏
        self.chartView.setRenderHint(QPainter.Antialiasing)

        self.chartView.setChart(self.chart)
        # Add the scatter_layout to the result_layout with stretch factor of 7 (70%)
        result_layout.addWidget(self.chartView, 7)

        # Table Section
        table_layout = QVBoxLayout()
        self.result_table = QTableWidget()

        self.result_table.setObjectName("best_results")
        self.result_table.setColumnCount(2)
        self.result_table.setColumnWidth(0, 149)
        self.result_table.setColumnWidth(1, 149)
        self.result_table.setFixedWidth(300)
        self.result_table.setFixedHeight(460)
        self.result_table.setHorizontalHeaderLabels(["Files", "CC"])

        self.workerThread.result.connect(self.updateResult)

        table_layout.addWidget(self.result_table, alignment=Qt.AlignRight)  # Align the table to the right
        # Add stretch to the table_layout to push the table to the bottom
        table_layout.addStretch(1)
        # Add the table_layout to the result_layout with stretch factor of 3 (30%)

        result_layout.addLayout(table_layout, 3)

        result_group.setLayout(result_layout)

        third_layout.addWidget(auto_param_group)
        third_layout.addWidget(result_group)

        layout.addLayout(third_layout)

        # 在初始化时调用showExtraControl方法，以确保根据复选框的初始状态正确隐藏或显示 "Number of Strong Reflections:" 这一行
        # self.showExtraControl(Qt.Unchecked)
        # Set window size fixed
        self.setFixedSize(1200, 800)

        self.setLayout(layout)

    # 选择文件
    def browseFile(self):
        self.filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '.', 'MTZ Files (*.mtz)')
        if self.filename:
            self.mtz_input.setText(self.filename)
            self.runBashScript()
            # self.runScript(filename)

    # 选择文件夹
    def browseDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.work_input.setText(directory)  # 将选择的目录路径设置为 QLineEdit 的文本
    def updateResult(self, data):
        self.result_table.setRowCount(len(data))  # Set row count
        for i, (result, cc) in enumerate(data):
            result_item = QTableWidgetItem(result)
            cc_item = QTableWidgetItem(cc)
            self.result_table.setItem(i, 0, result_item)
            self.result_table.setItem(i, 1, cc_item)


    def runBashScript(self):
        # Replace 'your_script.sh' with the path to your bash script file
        script_path = '/ssd2/code_python/pythonProject/pdb7_38_3mei/exp-test/38_3mei/browsefile.sh'
        process = subprocess.Popen(['bash', script_path, self.filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        print(type(str(self.strong_reflections_spin)))
        print(str(self.strong_reflections_spin.value()))
        # You can handle the output and error here as per your requirements
        if output:
            output_str = output.decode().strip().split()
            sg = ' '.join(output_str[10:])
            self.f_plus_line.setText(output_str[0])
            self.sigF_plus_line.setText(output_str[1])
            self.f_minus_line.setText(output_str[2])
            self.sigF_minus_line.setText(output_str[3])
            self.space_group_line.setText(sg)
            self.a_line.setText(output_str[4])
            self.b_line.setText(output_str[5])
            self.c_line.setText(output_str[6])
            self.alpha_line.setText(output_str[7])
            self.beta_line.setText(output_str[8])
            self.gamma_line.setText(output_str[9])

            print("Output:", output.decode())
        if error:
            print("Error:", error.decode())

    def startTask(self):
        paras = self.runScript()  # 调用 runScript 方法
        self.workerThread.set_parameters(paras)
        self.workerThread.start()

    def runScript(self):

        # This method could be for another purpose, filename is the raw mtz, including F+ F-
        # automated parameter setting
        script_path = '/ssd2/code_python/pythonProject/pdb7_38_3mei/exp-test/38_3mei/run_prep.sh'
        temp_tangent_method_cb = "1"
        if self.tangent_method_cb.isChecked():
            temp_tangent_method_cb = "1"
        else:
            temp_tangent_method_cb = "0"
        temp_refine_heavy_atoms_cb = "0"
        if self.refine_heavy_atoms_cb.isChecked():
            temp_refine_heavy_atoms_cb = "1"
        else:
            temp_refine_heavy_atoms_cb = "0"

        process_1 = subprocess.Popen(['bash', script_path, self.filename, temp_tangent_method_cb,
                                      str(self.strong_reflections_spin.value()), str(self.trials_spin.value()),
                                      str(self.iteration_spin.value()),
                                      str(self.resolution_cutoff_spin.value()), str(self.fraction.value()),
                                      temp_refine_heavy_atoms_cb],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output_1, error_1 = process_1.communicate()
        output_str = output_1.decode().strip()
        pattern_sayr = r'sayr:\s+([\d.]+)'
        pattern_scut = r'scut:\s+([\d.]+)'
        pattern_ntri = r'ntri:\s+([\d.]+)'
        pattern_nitr = r'nitr:\s+([\d.]+)'
        pattern_reso = r'reso:\s+([\d.]+)'
        pattern_weak = r'weak:\s+([\d.]+)'
        pattern_bp3 = r'bp3:\s+([\d.]+)'
        pattern_mtz = r'1111\s(.*?)\s2222'
        pattern_cctr = r'cctr:\s+([\d.]+)'
        match_scut = re.search(pattern_scut, output_str)
        match_ntri = re.search(pattern_ntri, output_str)
        match_nitr = re.search(pattern_nitr, output_str)
        match_reso = re.search(pattern_reso, output_str)
        match_weak = re.search(pattern_weak, output_str)
        match_mtz = re.search(pattern_mtz, output_str)
        match_cctr = re.search(pattern_cctr, output_str)

        print("fraction1: ", self.fraction.value())
        self.strong_reflections_spin.setValue(int(match_scut.group(1)))
        self.trials_spin.setValue(int(match_ntri.group(1)))
        self.iteration_spin.setValue(int(match_nitr.group(1)))
        self.resolution_cutoff_spin.setValue(float(match_reso.group(1)))
        self.fraction.setValue(float(match_weak.group(1)))
        cctr = match_cctr.group(1)
        mtz_shelc = match_mtz.group(1)
        print(cctr, mtz_shelc)
        print(self.space_group_line, type(self.space_group_line))
        print(self.num_heavy_atoms_input, type(self.num_heavy_atoms_input))
        print(self.heavy_atom_input, type(self.heavy_atom_input))
        print(self.wavelength, type(self.wavelength))
        print(str(self.wavelength.text()))
        print("fraction2: ", self.fraction.value())
        print("num:", self.num_heavy_atoms_input.text())

        return [mtz_shelc, temp_tangent_method_cb,
                str(self.strong_reflections_spin.value()), str(self.trials_spin.value()),
                str(self.iteration_spin.value()), str(self.resolution_cutoff_spin.value()),
                str(self.fraction.value()), temp_refine_heavy_atoms_cb,
                cctr, str(self.num_heavy_atoms_input.text()), str(self.heavy_atom_input.text()),
                str(self.wavelength.value()), self.filename]

    def updateScatter(self, data):
        # 更新散点图
        self.scatter.clear()
        for point in data:
            self.scatter.append(point[0], point[1])

    def stopScript(self):
        # This method could be for another purpose
        pass

    def showExtraControl(self, state):
        for i in range(self.auto_param_layout.rowCount()):
            label_item = self.auto_param_layout.itemAt(i, QFormLayout.LabelRole)
            if label_item is not None and label_item.widget().text() == "Number of Strong Reflections:":
                spin_box = self.auto_param_layout.itemAt(i, QFormLayout.FieldRole).widget()
                if state == Qt.Checked:
                    label_item.widget().setVisible(True)
                    spin_box.setVisible(True)
                else:
                    label_item.widget().setVisible(False)
                    spin_box.setVisible(False)
                break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApplication()
    ex.show()
    sys.exit(app.exec_())
