from MotorController import BG431BESC1
from time import sleep
from maestro import Controller
from InputMappings.MappingClass import MappingClass
from InputMappings.EvdevInput import EvdevDeviceInput, x360Pad


# TODO - ogarnąć innego pada
# TODO - przenieść część funkcjonalności do innego pliku EngineSection czy coś (to już jak ruszy)

class BeaverCar:
    def __init__(self):
        self.engine1 = BG431BESC1("COM8", 1843200)
        # self.engine2 = BG431BESC1("COMX", 1843200)
        # self.servo_controller = Controller("COMX")

        self.__engine_setup(self.engine1)
        # self.__engine_setup(self.engine2)

        # Sterowanie - idea z UnrealEngine

        # First, map names to various functions
        self.mapping_object = MappingClass()

        self.mapping_object.map_standard_action("test1", self.test_engine1)

        self.mapping_object.map_standard_action("speed", self.control_speed)
        self.mapping_object.map_standard_action("turn", self.turning)

        # then add device and map various inputs on given device to previously mapped names
        self.pad = x360Pad(self.mapping_object)

        self.pad.map_key("BTN_X", "test1")
        self.pad.map_joystick("LEFT_J", "turn", action_type="ang_str")
        self.pad.map_joystick("TRIGGERS", "control_speed", action_type="x_y")

        # instance of class actually responsible for listening to inputs from various devices
        self.evdevInput = EvdevDeviceInput()

        self.evdevInput.connect_devices()

    def control_speed(self, acc: float, dec: float) -> None:
        """
        control car's speed
        :param acc: acceleration, float from 0-1 (how strong is right trigger pressed)
        :param dec: deceleration, float from 0-1 (how strong is left trigger pressed)
        :return: None
        """
        # TODO - zaimplementować
        pass

    def turning(self, angle: float, strength: float) -> None:
        """

        :param angle: joystick angle, float from -90 to 270 (in degrees)
        :param strength: strength of tilt, float from 0 to 1 (unused)
        :return: None
        """
        # TODO - zaimplementować
        pass

    def __engine_setup(self, engine: BG431BESC1) -> None:
        engine.ack_fault()
        engine.set_KP(16000)
        engine.set_KI(1000)
        engine.set_speed(1000)
        sleep(0.1)

    def test_engine1(self) -> None:
        sleep(0.1)
        print(0)
        self.engine1.start_motor()
        print(1)
        sleep(3)
        print(2)
        self.engine1.stop_motor()

    def runCar(self) -> None:
        self.evdevInput.listen_and_execute_one_dev()
        # TODO - ta funkcja jest do dokładnej przebudowy
