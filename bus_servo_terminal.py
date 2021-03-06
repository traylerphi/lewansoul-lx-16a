#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Bus Servo Terminal for LewanSoul LX-16A servos

Author: traylerphi
Website: https://github.com/traylerphi/lewansoul-lx-16a
Last edited: August 7th, 2018
"""

import re
import sys

from PyQt5.QtWidgets import (QWidget, QGridLayout,
    QApplication, QDesktopWidget,
    QLabel, QPushButton, QListWidget, QLineEdit)

import serial
from serial.tools.list_ports import comports
from serial.tools import hexlify_codec

class BusServoTerminal(QWidget):
    
    def __init__(self):
        """
        Class constructor / init
        """
        super().__init__()
        
        self.selected_port = False
        self.available_ports = []
        self.connection = False
        self.selected_servo_id = False
        self.initUI()
        
    def initUI(self):
        """
        Create UI elements in grid to allow resize
        """
        self.getPorts()
        
        grid = QGridLayout()
        self.setLayout(grid)
        
        self.lblPort = QLabel('Using port {!r}'.format(self.selected_port.device), self)
        grid.addWidget(self.lblPort, 0, 0)
        
        self.lblConnected = QLabel('Not Connected')
        grid.addWidget(self.lblConnected, 0, 3)
        
        btnPoll = QPushButton('Poll Bus for Servos')
        btnPoll.clicked.connect(self.pollBus)
        grid.addWidget(btnPoll, 1, 0, 1, 2)
        
        self.servolist = QListWidget(self)
        self.servolist.itemClicked.connect(self.select_servo)
        grid.addWidget(self.servolist, 2, 0, 15, 2)
        
        
        self.lblStatus = QLabel('No Selection')
        grid.addWidget(self.lblStatus,2,3,1,3)
        
        
        lblServoID = QLabel('Servo ID:',self)
        self.textServoID = QLineEdit(self)
        btnSetID = QPushButton('Set')
        btnSetID.clicked.connect(self.set_servo_id)
        grid.addWidget(lblServoID,3,3)
        grid.addWidget(self.textServoID,3,4,1,2)
        grid.addWidget(btnSetID,3,6)
        
        self.toggleMotorOn = QPushButton('Motor Off')
        self.toggleMotorOn.setCheckable(True)
        self.toggleMotorOn.clicked[bool].connect(self.toggle_motor_state)
        grid.addWidget(self.toggleMotorOn,4,4)
        
        self.toggleLightOn = QPushButton('LED Off')
        self.toggleLightOn.setCheckable(True)
        self.toggleLightOn.clicked[bool].connect(self.toggle_light_state)
        grid.addWidget(self.toggleLightOn,4,5)
        
        lblMode = QLabel('Control:',self)
        self.toggleMode = QPushButton('Servo')
        self.toggleMode.setCheckable(True)
        self.toggleMode.clicked[bool].connect(self.toggle_mode)
        grid.addWidget(lblMode,4,3)
        grid.addWidget(self.toggleMode,5,4)
        
        lblSpeed = QLabel('Continuous Speed:',self)
        lblSpeed2 = QLabel('(-1000 ~ 1000)',self)
        self.textSpeed = QLineEdit(self)
        btnSetSpeed = QPushButton('Set')
        btnSetSpeed.clicked[bool].connect(self.set_speed)
        grid.addWidget(lblSpeed,6,3)
        grid.addWidget(lblSpeed2,6,4)
        grid.addWidget(self.textSpeed,6,5)
        grid.addWidget(btnSetSpeed,6,6)
        
        lblPosition = QLabel('Position:',self)
        self.textPosition = QLabel(self)
        self.textPosCommand = QLineEdit(self)
        btnPosCommand = QPushButton('Command')
        btnPosCommand.clicked.connect(self.command_position)
        grid.addWidget(lblPosition,7,3)
        grid.addWidget(self.textPosition,7,4)
        grid.addWidget(self.textPosCommand,7,5)
        grid.addWidget(btnPosCommand,7,6)
        
        lblPosRange = QLabel('Pos Range:',self)
        self.textPosRangeLow = QLineEdit(self)
        self.textPosRangeHigh = QLineEdit(self)
        btnPosRange = QPushButton('Set')
        btnPosRange.clicked.connect(self.set_position_range)
        grid.addWidget(lblPosRange,8,3)
        grid.addWidget(self.textPosRangeLow,8,4)
        grid.addWidget(self.textPosRangeHigh,8,5)
        grid.addWidget(btnPosRange,8,6)
        
        lblPosOffset = QLabel('Pos Offset:',self)
        lblPosOffset2 = QLabel('(-125 ~ 125)',self)
        self.textPosOffset = QLineEdit(self)
        btnPosOffset = QPushButton('Set')
        btnPosOffset.clicked.connect(self.set_pos_offset)
        grid.addWidget(lblPosOffset,9,3)
        grid.addWidget(lblPosOffset2,9,4)
        grid.addWidget(self.textPosOffset,9,5)
        grid.addWidget(btnPosOffset,9,6)

        lblTemperature = QLabel('Temperature:',self)
        self.textTemperature = QLabel(self)
        grid.addWidget(lblTemperature,10,3)
        grid.addWidget(self.textTemperature,10,4,1,3)
        
        lblMaxTemp = QLabel('Max Temp:',self)
        self.textMaxTemp = QLineEdit(self)
        btnMaxTemp = QPushButton('Set')
        btnMaxTemp.clicked.connect(self.set_max_temp)
        grid.addWidget(lblMaxTemp,11,3)
        grid.addWidget(self.textMaxTemp,11,4,1,2)
        grid.addWidget(btnMaxTemp,11,6)
        
        lblVoltage = QLabel('Voltage:',self)
        self.textVoltage = QLabel(self)
        grid.addWidget(lblVoltage,12,3)
        grid.addWidget(self.textVoltage,12,4,1,3)
        
        lblVoltRange = QLabel('Voltage Range:',self)
        self.textVoltRangeLow = QLineEdit(self)
        self.textVoltRangeHigh = QLineEdit(self)
        btnVoltRange = QPushButton('Set')
        btnVoltRange.clicked.connect(self.set_voltage_range)
        grid.addWidget(lblVoltRange,13,3)
        grid.addWidget(self.textVoltRangeLow,13,4)
        grid.addWidget(self.textVoltRangeHigh,13,5)
        grid.addWidget(btnVoltRange,13,6)
        
        lblAlarm1 = QLabel('Temperature Alarm',self)
        lblAlarm2 = QLabel('Voltage Alarm',self)
        lblAlarm4 = QLabel('Stall Alarm',self)
        self.toggleAlarmEnable1 = QPushButton('Disabled')
        self.toggleAlarmEnable2 = QPushButton('Disabled')
        self.toggleAlarmEnable4 = QPushButton('Disabled')
        self.toggleAlarmEnable1.setCheckable(True)
        self.toggleAlarmEnable2.setCheckable(True)
        self.toggleAlarmEnable4.setCheckable(True)
        self.toggleAlarmEnable1.clicked[bool].connect(self.update_alarm_config)
        self.toggleAlarmEnable2.clicked[bool].connect(self.update_alarm_config)
        self.toggleAlarmEnable4.clicked[bool].connect(self.update_alarm_config)
        grid.addWidget(lblAlarm1,14,3)
        grid.addWidget(self.toggleAlarmEnable1,14,4)
        grid.addWidget(lblAlarm2,15,3)
        grid.addWidget(self.toggleAlarmEnable2,15,4)
        grid.addWidget(lblAlarm4,16,3)
        grid.addWidget(self.toggleAlarmEnable4,16,4)
        
        """
        Initilize the window itself, center in the screen with default size 800x300
        """
        self.resize(800, 300)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('Bus Servo Terminal for LewanSoul LX-16A servos - traylerphi')    
        self.show()
        
    def getPorts(self):
        """
        Find list of connected COM ports
        Auto-select any port that matches VID:PID
        TODO: UI element to select between discovered ports
        """
        self.available_ports.clear()
        
        not_found = True
        for port in sorted(comports()):
            self.available_ports.append(port)
            sys.stderr.write('Found port {!r}\n'.format(port.device))
            if (port.vid == 6790) and (port.pid == 29987):
                self.selected_port = port
                not_found = False
                sys.stderr.write('* Auto-selecting port {!r}\n'.format(port.device))
        if not_found == True:
            sys.stderr.write('No device found, is Lewan Debug board connected?\n')
            sys.exit()
        sys.stderr.flush()
    
    def connectToPort(self):
        """
        Connect to selected_port (singleton style)
        """
        if self.connection == False:
            self.connection = serial.Serial(self.selected_port.device, 115200, timeout=0.1)
            self.lblConnected.setText('CONNECTED')
            sys.stderr.write('--- Connected to {!r}\n'.format(self.connection.name))
        sys.stderr.flush()
    
    def pollBus(self):
        """
        Determine list of servos attached to bus
        """
        self.clear_selected_servo()
        self.servolist.clear()
        self.connectToPort()
        self.lblStatus.setText("Polling Servo Bus...")
        sys.stderr.write('--- Polling Servo Bus ---\n')
        QApplication.instance().processEvents() # Force list to clear
        QApplication.instance().processEvents() # so user knows
        QApplication.instance().processEvents() # something is happening
        
        """
        The documentation allows for a 'broadcast address' to ask an
        unknown servo what it's ID number is, however this only works
        if there is one ONE servo on the bus :(
        Therefore, we'll ask each ID in turn if for it's ID - if the
        servo is connected, we'll get a response.
        If multiple servos with the same ID are connected, we'll (almost always)
        get a garbled response.
        """
        for id in range(40):
            found = self.checkForID(id)
            if found == True:
                self.servolist.addItem('Servo ID:{!r}'.format(id))
            if found == 'Multiple': 
                self.servolist.addItem('Servo ID:{!r} - ERROR: Multiple Found'.format(id))
            #QApplication.instance().processEvents()
        
        self.lblStatus.setText("No Selection")
        sys.stderr.flush()
        
    def sendCommand(self, command):
        """
        Add packet headers and checksum
        """
        sum = 0
        for i in command:
            sum = sum + i
        if sum > 255:
            sum = sum & 255
        sum = 255 - sum
        
        prepared = [85,85,*command,sum]
        
        self.connection.flushInput()
        self.connection.flushOutput()
        self.connection.write(prepared)
        result = []
        response = bytearray([0]*10)
        count = self.connection.readinto(response)
        found_header = 0
        for i in range(count):
            if found_header == 2:
                result.append(response[i])
            if response[i] == 85:
                found_header = found_header + 1
            if found_header == 3:
                found_header = 1
        #print(result)
        return result
    
    def clear_selected_servo(self):
        self.lblStatus.setText('No Selection')
        self.selected_servo_id = False
        self.textServoID.setText('')
        self.update_motor_state_button()
        self.update_light_state_button()
        self.update_mode_button()
        self.textPosition.setText('')
        self.textPosCommand.setText('')
        self.textPosRangeLow.setText('')
        self.textPosRangeHigh.setText('')
        self.textPosOffset.setText('')
        self.textTemperature.setText('')
        self.textMaxTemp.setText('')
        self.textVoltage.setText('')
        self.textVoltRangeLow.setText('')
        self.textVoltRangeHigh.setText('')
        self.update_alarm_enable_buttons()
    
    def select_servo(self, item):
        id = int(re.search('Servo ID:(\d+)',item.text()).group(1));
        self.clear_selected_servo();
        self.lblStatus.setText("Loading Servo ID:{!r}...".format(id))
        QApplication.instance().processEvents() # Force update
        QApplication.instance().processEvents() # so user knows
        QApplication.instance().processEvents() # something
        QApplication.instance().processEvents() # is happening
        self.clear_selected_servo()
        if self.checkForID(id):
            self.lblStatus.setText("Selected Servo ID:{!r}".format(id))
            self.selected_servo_id = id
            self.textServoID.setText(str(id))
            self.update_motor_state_button()
            self.update_light_state_button()
            self.update_mode_button()
            self.textPosition.setText(str(self.read_position()))
            self.textPosCommand.setText(self.textPosition.text())
            position_range = self.read_position_range()
            self.textPosRangeLow.setText(str(position_range[0]))
            self.textPosRangeHigh.setText(str(position_range[1]))
            self.textPosOffset.setText(str(self.read_position_offset()))
            self.textTemperature.setText(str(self.read_temperature()))
            self.textMaxTemp.setText(str(self.read_max_temp()))
            self.textVoltage.setText(str(self.read_voltage()))
            voltage_range = self.read_voltage_range()
            self.textVoltRangeLow.setText(str(voltage_range[0]))
            self.textVoltRangeHigh.setText(str(voltage_range[1]))
            self.update_alarm_enable_buttons()
        else:
            # Bad selection - re poll
            self.pollBus()
        
    def checkForID(self, id):
        """
        Send command 14 (READ ID, length 3) to id
        
        Return True if valid response
        Return False otherwise
        """
        result = self.sendCommand([id,3,14])
        if result == []:
            return False
        if result[0] == id:
            return True
        return False
    
    def set_servo_id(self):
        if self.selected_servo_id != False:
            self.lblStatus.setText("Setting ID...")
            newid = int(self.textServoID.text())
            sys.stderr.write('--- Setting ID of {!r} to {!r}\n'.format(self.selected_servo_id,newid))
            result = self.sendCommand([self.selected_servo_id,4,13,newid])
            self.pollBus()  
            
    def read_position(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,28])
            return (int(result[4]*256) + int(result[3]))
        return ''
    
    def command_position(self):
        if self.selected_servo_id != False:
            
            value = int(self.textPosCommand.text())
            high = 0
            low = value
            while low > 255:
                low = low - 256
                high = high + 1
            self.sendCommand([self.selected_servo_id,7,1,low,high,0,0])
            
        self.update_motor_state_button()
    
    
    def read_position_range(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,21])
            low = (int(result[4]*256) + int(result[3]))
            high = (int(result[6]*256) + int(result[5]))
            return [low,high]
        return ['','']
    
    def set_position_range(self):
        if self.selected_servo_id != False:
            low_high = 0
            low_low = int(self.textPosRangeLow.text())
            while low_low > 255:
                low_low = low_low - 256
                low_high = low_high + 1
            high_high = 0
            high_low = int(self.textPosRangeHigh.text())
            while high_low > 255:
                high_low = high_low - 256
                high_high = high_high + 1
            self.sendCommand([self.selected_servo_id,7,20,low_low,low_high,high_low,high_high])

    def read_position_offset(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,19])
            offset = int(result[3])
            if offset > 125:
                offset = offset - 256
            return offset
        return ''

    def set_pos_offset(self):
        if self.selected_servo_id != False:
            offset = int(self.textPosOffset.text())
            if offset < 0:
                offset = 256 + offset
            self.sendCommand([self.selected_servo_id,4,17,offset])
            self.sendCommand([self.selected_servo_id,3,18])

    def read_temperature(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,26])
            return result[3]
        return ''
    
    def read_max_temp(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,25])
            return result[3]
        return ''
    
    def set_max_temp(self):
        if self.selected_servo_id != False:
            newvalue = int(self.textMaxTemp.text())
            self.sendCommand([self.selected_servo_id,4,24,newvalue])
    
    def read_voltage(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,27])
            return (int(result[4]*256) + int(result[3]))
        return ''
    
    def read_voltage_range(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,23])
            low = (int(result[4]*256) + int(result[3]))
            high = (int(result[6]*256) + int(result[5]))
            return [low,high]
        return ['','']
    
    def set_voltage_range(self):
        if self.selected_servo_id != False:
            low_high = 0
            low_low = int(self.textVoltRangeLow.text())
            while low_low > 255:
                low_low = low_low - 256
                low_high = low_high + 1
            high_high = 0
            high_low = int(self.textVoltRangeHigh.text())
            while high_low > 255:
                high_low = high_low - 256
                high_high = high_high + 1
            
            self.sendCommand([self.selected_servo_id,7,22,low_low,low_high,high_low,high_high])
    
    def update_motor_state_button(self):
        if self.read_motor_state():
            self.toggleMotorOn.setText('Motor On')
            self.toggleMotorOn.setChecked(True)
        else:
            self.toggleMotorOn.setText('Motor Off')
            self.toggleMotorOn.setChecked(False)
            
    def read_motor_state(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,32])
            if result[3] == 1:
                return True
        return False
    
    def toggle_motor_state(self, pressed):
        if self.selected_servo_id == False:
            pressed = False
        if pressed:
            value = 1
        else:
            value = 0
            
        if self.selected_servo_id != False:
            self.sendCommand([self.selected_servo_id,4,31,value])
            
        self.update_motor_state_button()
    
    def update_mode_button(self):
        if self.read_mode():
            self.toggleMode.setText('Continuous')
            self.toggleMode.setChecked(True)
        else:
            self.toggleMode.setText('Servo')
            self.toggleMode.setChecked(False)
            self.textSpeed.setText('0')
    
    def read_mode(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,30])
            if result[3] == 1:
                return True
        return False
    
    def set_speed(self):
        if self.selected_servo_id != False:
            high = 0
            low = int(self.textSpeed.text())
            if low < 0:
                low = 65536 + low
            while low > 255:
                low = low - 256
                high = high + 1
            self.sendCommand([self.selected_servo_id,7,29,1,0,low,high])
            self.toggleMode.setText('Continuous')
            self.toggleMode.setChecked(True)
    
    def toggle_mode(self, pressed):
        if self.selected_servo_id == False:
            pressed = False
        if pressed:
            value = 1
        else:
            value = 0
            
        if self.selected_servo_id != False:
            if value == 0:
                self.sendCommand([self.selected_servo_id,7,29,0,0,0,0])
            else:
                self.set_speed()
            
        self.update_mode_button()
        
    def update_light_state_button(self):
        if self.read_light_state():
            self.toggleLightOn.setText('LED On')
            self.toggleLightOn.setChecked(True)
        else:
            self.toggleLightOn.setText('LED Off')
            self.toggleLightOn.setChecked(False)
            
    def read_light_state(self):
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,34])
            if result[3] == 0:
                return True
        return False
    
    def toggle_light_state(self, pressed):
        if self.selected_servo_id == False:
            pressed = False
        if pressed:
            value = 0
        else:
            value = 1
            
        if self.selected_servo_id != False:
            self.sendCommand([self.selected_servo_id,4,33,value])
            
        self.update_light_state_button()
    
    def update_alarm_enable_buttons(self):
        self.toggleAlarmEnable1.setText('Disabled')
        self.toggleAlarmEnable1.setChecked(False)
        self.toggleAlarmEnable2.setText('Disabled')
        self.toggleAlarmEnable2.setChecked(False)
        self.toggleAlarmEnable4.setText('Disabled')
        self.toggleAlarmEnable4.setChecked(False)
        
        if self.selected_servo_id != False:
            result = self.sendCommand([self.selected_servo_id,3,36])
            config = int(result[3])
            if config & 1:
                self.toggleAlarmEnable1.setText('Enabled')
                self.toggleAlarmEnable1.setChecked(True)
            if config & 2:
                self.toggleAlarmEnable2.setText('Enabled')
                self.toggleAlarmEnable2.setChecked(True)
            if config & 4:
                self.toggleAlarmEnable4.setText('Enabled')
                self.toggleAlarmEnable4.setChecked(True)
                
    
    def update_alarm_config(self, pressed):
        config = 0;
        if self.toggleAlarmEnable1.isChecked():
            config = config + 1
        if self.toggleAlarmEnable2.isChecked():
            config = config + 2
        if self.toggleAlarmEnable4.isChecked():
            config = config + 4
        if self.selected_servo_id != False:
            self.sendCommand([self.selected_servo_id,4,35,config])
        self.update_alarm_enable_buttons()
    
    
    def closeEvent(self, event):
        """
        Application closing
        """
        if self.connection:
            sys.stderr.write('--- Closing connection to {!r}\n'.format(self.connection.name))
            self.connection.close()
        event.accept()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    bst = BusServoTerminal()
    sys.exit(app.exec_())

