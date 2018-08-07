#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Bus Servo Terminal for LewanSoul LX-16A servos

Author: traylerphi
Website: https://github.com/traylerphi/lewansoul-lx-16a
Last edited: August 7th, 2018
"""

import sys
from PyQt5.QtWidgets import (QWidget, QGridLayout,
    QApplication, QDesktopWidget,
    QLabel, QPushButton, QListWidget)

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
        grid.addWidget(self.lblConnected, 0, 1)
        
        btn1 = QPushButton('Poll Bus for Servos')
        btn1.clicked.connect(self.pollBus)
        grid.addWidget(btn1, 1, 0, 1, 2)
        
        self.servolist = QListWidget()
        grid.addWidget(self.servolist, 2, 0, 1, 2)
        
        """
        Initilize the window itself, center in the screen with default size 800x600
        """
        self.resize(800, 600)
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
        
        for port in sorted(comports()):
            self.available_ports.append(port)
            sys.stderr.write('Found port {!r}\n'.format(port.device))
            if (port.vid == 6790) and (port.pid == 29987):
                self.selected_port = port
                sys.stderr.write('* Auto-selecting port {!r}\n'.format(port.device))
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
        self.servolist.clear()
        self.connectToPort()
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
        
        sys.stderr.flush()
        
    def checkForID(self, id):
        """
        Send command 14 (READ ID, length 3) to id
        
        Return True if valid response
        Return 'Multple' if garbled response
        Return False if no response
        """
        command = self.prepareCommand([id,3,14])
        self.connection.write(command)
        response = bytearray([0]*7)
        count = self.connection.readinto(response)
        if count > 0:
            if response[0] == 85 and response[1] == 85 and response[2] == id:
                return True
            else:
                return 'Multiple'
            self.connection.flushInput()
            self.connection.flushOutput()
        return False
    
    def prepareCommand(self, command):
        """
        Add packet headers and checksum
        """
        sum = 0
        for i in command:
            sum = sum + i
        if sum > 255:
            sum = sum & 255
        sum = 255 - sum
        return bytearray([85,85,*command,sum])
        
    def closeEvent(self, event):
        """
        Application closing
        """
        sys.stderr.write('--- Closing connection to {!r}\n'.format(self.connection.name))
        self.connection.close()
        event.accept()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    bst = BusServoTerminal()
    sys.exit(app.exec_())

