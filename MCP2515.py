# MCP2515 Minimal Module for canbus I/O with OBDII
# Created by Gemini, customized by AndrewNox & corrected
# Ver 0.4

from machine import Pin, SPI
import time

class MCP2515:
    def __init__(self, spi, cs):
        '''
            Parameters:
                spi -> istanza SPI (es. SPI(0, ...))
                cs  -> pin di Chip Select configurato come Pin.OUT
        '''
        self.spi = spi
        self.cs = cs
        self.cs.value(1)
    
    def select(self):
        self.cs.value(0)
    
    def deselect(self):
        self.cs.value(1)
        
    def reset(self):
        ''' Reset function at the beginning of CAN setup '''
        self.cs.value(0)
        self.spi.write(bytearray([0xC0]))
        self.cs.value(1)
        time.sleep_ms(100)
        
    def write_reg(self, addr, val):
        ''' Function to write a command in an internal MCP register '''
        self.cs.value(0)
        self.spi.write(bytearray([0x02, addr, val]))
        self.cs.value(1)
    
    def read_reg(self, addr):
        ''' Function to read the response from an MCP register '''
        self.cs.value(0)
        self.spi.write(bytearray([0x03, addr]))
        val = self.spi.read(1)[0]
        self.cs.value(1)
        return val
    
    def bit_modify(self, addr, mask, data):
        ''' Function to modify specific bits in a register '''
        self.cs.value(0)
        self.spi.write(bytearray([0x05, addr, mask, data]))
        self.cs.value(1)
        
    def send_message(self, can_id, data):
        ''' Core function to send PID or other data via CAN BUS using TXBuffer 0 '''
        # TXB0SIDH (Standard ID High)
        self.write_reg(0x31, (can_id >> 3) & 0xFF)
        # TXB0SIDL (Standard ID Low)
        self.write_reg(0x32, (can_id << 5) & 0xE0)
        # TXB0DLC (Data Length Code - numero di byte)
        self.write_reg(0x35, len(data) & 0x0F)
        
        # Scrittura dei dati nei registri da TXB0D0 (0x36) in poi
        for i, b in enumerate(data):
            self.write_reg(0x36 + i, b)
        
        # Comando RTS (Request To Send) per il Buffer 0 (0x81)
        self.cs.value(0)
        self.spi.write(bytearray([0x81]))
        self.cs.value(1)
        
    def read_message(self):
        ''' Read message from Buffer RX0 del MCP2515 if exists '''
        # Control registry CANINTF (0x2C) if exists a message in RXB0 (bit 0)
        canintf = self.read_reg(0x2C)
        if not (canintf & 0x01):
            return None  # No message in the buffer 0
            
        # Read standard ID (SIDH e SIDL) from the registry RXB0
        sidh = self.read_reg(0x61)
        sidl = self.read_reg(0x62)
        can_id = (sidh << 3) | (sidl >> 5)
        
        # Read DLC (Data Length Code - byte number)
        dlc = self.read_reg(0x65) & 0x0F
        
        # Read effective data from RXB0D0 (0x66) 
        data = bytearray(dlc)
        for i in range(dlc):
            data[i] = self.read_reg(0x66 + i)
            
        # Cleaning interrupt flag RX0IF (zeroing bit 0 in the CANINTF 0x2C registry)
        self.bit_modify(0x2C, 0x01, 0x00)
        
        return can_id, data