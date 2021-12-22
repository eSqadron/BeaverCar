import struct
from time import sleep

import serial


class MotorMode:
    SPEED = 1
    TORQUE = 2


class MotorError(Exception):
    def __init__(self, message="Salary is not in (5000, 15000) range"):
        super().__init__(message)


class BG431BESC1:
    """
    B-G431B-ESC1 Motor Controller
    TODO - dodać sterowanie rampą (która mi w pilocie nie działa XD)
    TODO - zamienić wypisywanie wartości powrotnej na sprawdzanie i wyrzucanie errorów
    TODO - dodać KP i KI dividera (które nie wiem co robią XD)
    TODO - może zrobić self.mode na setterach i getterach?
    TODO - dodać zapytania o temperaturę, obecną prędność, moc itp.
    TODO - ogarnąć kontrolowanie PI w trybie torque a trybie speed (bo chyba się różni)
    TODO - typing
    TODO - zamykanie seriali i tego typu szit
    TODO - destruktor może jakiś
    TODO - zrobić osobny plik z zupełnie osobną klasą tworzący wykresy (To tak może kiedyś dodatkowo)
    """

    def __init__(self, serial_port_, serial_baudrate_, default_mode=MotorMode.SPEED):  # , data_logging=0):
        self.serial_port = serial.Serial(serial_port_, serial_baudrate_)
        self.mode = default_mode
        # self.acc_speed = []
        # self.time_plot = []
        # self.target_speed = []
        # self.data_logging = data_logging

        self.__start_sequence()

    # Set basic Values

    def set_speed(self, speed):
        if self.mode != MotorMode.SPEED:
            raise MotorError(f"can't set speed when motor is not in speed mode!")

        self.serial_port.write(self.__get_speed_string(speed))

    def set_torque(self, torq):
        if self.mode != MotorMode.SPEED:
            raise MotorError(f"can't set torque when motor is not in torque mode!")
        self.serial_port.write(self.__get_torq_string(torq))

    # Start/Stop motor

    def stop_motor(self):
        # 290000E02100
        self.serial_port.write(bytes.fromhex("290000E02100"))

    def start_motor(self):
        # 290000E01900
        self.serial_port.write(bytes.fromhex("290000E01900"))

    # Set PI

    def set_KP(self, kp):
        send_str = self.__get_KP_string(kp)
        self.serial_port.write(send_str)
        # print("send kp request")
        # recv = self.serial_port.read(5)
        # print(struct.unpack('ci', recv), " ", struct.unpack('si', bytes.fromhex('1A00002000')))

    def set_KI(self, ki):
        send_str = self.__get_KI_string(ki)
        self.serial_port.write(send_str)
        recv = self.serial_port.read(5)
        # print(recv)

    # Other

    def ack_fault(self):
        # 290000E03900
        self.serial_port.write(bytes.fromhex("290000E03900"))

    def set_mode(self, mode):
        self.mode = mode
        if mode == MotorMode.TORQUE:
            self.serial_port.write(bytes.fromhex("590000F00800890000"))
        elif mode == MotorMode.SPEED:
            self.serial_port.write(bytes.fromhex("590000F00800890001"))

    # Private methods

    def __get_speed_string(self, speed):
        res = 'C90000C0080069010600'
        res += self.__short_to_hex(speed).upper()
        if speed < 0:
            res += 'FFFF'
        else:
            res += '0000'
        res += '0000'
        print(res)
        return bytes.fromhex(res)

    def __get_torq_string(self, speed):
        res = 'C90000C00800A9010600'
        res += self.__short_to_hex(speed).upper()
        if speed < 0:
            res += 'FFFF'
        else:
            res += '0000'
        res += '0000'
        print(res)
        return bytes.fromhex(res)

    def __get_KP_string(self, kp):
        res = '6900000008009100'
        res += self.__short_to_hex(kp).upper()
        print("KP ", res)
        return bytes.fromhex(res)

    def __get_KI_string(self, ki):
        res = '690000000800D100'
        res += self.__short_to_hex(ki).upper()
        print("KI ", res)
        return bytes.fromhex(res)

    def __short_to_hex(self, sh):
        res = struct.pack('h', sh)
        res = ''.join('{:02x}'.format(x) for x in res)

        # print(res)
        return res

    def __start_sequence(self):
        # THEFUCK?
        # To wszystko jest tu potrzebne?
        # Te sleepy mi się nie podobają
        # i te printy na sprawdzanie i ew. rzucanie errorów by się przydało zamienić
        self.serial_port.write(bytes.fromhex("05C70114"))  # ASPEP_BEACON
        recv = self.serial_port.read(4)
        print(struct.unpack('i', recv)[0], " ", struct.unpack('i', bytes.fromhex('05C70114'))[0])
        sleep(0.1)
        self.serial_port.write(bytes.fromhex("06000060"))  # ASPEP_PING
        recv = self.serial_port.read(4)
        print(struct.unpack('i', recv)[0], " ", struct.unpack('i', bytes.fromhex('06000060'))[0])
        sleep(0.1)
        self.serial_port.write(bytes.fromhex("06000060"))  # ASPEP_PING
        recv = self.serial_port.read(4)
        print(struct.unpack('i', recv)[0], " ", struct.unpack('i', bytes.fromhex('06000060'))[0])
        sleep(0.1)
        #print("PID calibration")
        # self.set_KP(2000)
        # self.set_KI( 1000)
        #print("PID done")

        self.ack_fault()

        sleep(0.1)

        self.set_mode(self.mode)

        sleep(0.1)
        self.serial_port.flushInput()
        self.serial_port.flushOutput()
        sleep(0.1)

    # def get_curr_speed(self):
    #     self.serial_port.flushInput()
    #     self.serial_port.flushOutput()
    #     self.serial_port.write(bytes.fromhex(
    #         "A9020040110019005900990091099102D10251099101D101511491149100D1001109D1089105D105110649008900"))
    #     recv = self.serial_port.read(49)
    #     # DA02 0060 0000 0000 0000 0000 DC05 0000  0000 D80E D308 0000 D80E D308 1000 0001 E803 BC02 0000 0000 1100 2900 0000 0001 00
    #     if self.data_logging == 1:
    #         recv = (struct.unpack('hfhhhhhhhhhhhhhhhhhhhhc', recv))
    #         self.acc_speed.append(recv[2])
    #         self.target_speed.append((recv[4]))
    #         self.time_plot.append(time())
    #     # print(recv[2] , recv[4])
    #
    # def meass_speed_for(self):
    #     t0 = time()
    #     delta_time = 0
    #     while True:
    #
    #         self.get_curr_speed()
    #         delta_time = time() - t0
    #         if delta_time > 5:
    #             break
