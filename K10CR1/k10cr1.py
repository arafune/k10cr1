import math

import serial
from serial.tools import list_ports


class K10CR1:
    """Thorlabs K10CR1 rotation stage class."""

    def __init__(self, ser_num: str) -> None:
        """Set up and connect to device with serial number: ser_num

        Parameters
        ----------
        ser_num : str
            serial number of the K10CR1
        """
        self.ser_num = ser_num
        self.ready = False
        self.connect()
        if not self.ready:
            print("Unable to connect to device with serial number: {}".format(ser_num))
        else:
            print("Connect successful to device with serial number: {}".format(ser_num))
            self.zerobacklash()

    def connect(self) -> None:
        """Searches all com ports for device with matching serial number
        and opens a connection
        """
        ports = list_ports.comports()
        for port in ports:
            print(port)
            try:
                if port.serial_number.startswith(self.ser_num):
                    self.ser = serial.Serial(
                        baudrate=115200, timeout=0.1, port=port.device
                    )
                    self.ready = True
                    break
            except AttributeError:
                pass

    def angle_to_DU(self, ang: float) -> int:
        return int(ang * 24576000 / 180)

    def DU_to_angle(self, DU: int) -> float:
        return DU * 180 / 24576000

    def dth(self, x: int, bytelen: int) -> str:
        if x >= 0:
            hstring = hex(x)
            hstring = hstring[2:]
            while len(hstring) < 2 * bytelen:
                hstring = "0" + hstring
            count = 0
            new = list(hstring)
            while count < bytelen * 2:
                tmp = new[count]
                new[count] = new[count + 1]
                new[count + 1] = tmp
                count = count + 2
            hstring = "".join(new)
            hstring = hstring[::-1]
            return hstring
        elif x < 0:
            y = abs(x)
            bstring = bin(y)
            bstring = bstring[2:]
            while len(bstring) < 2 * bytelen * 4:
                bstring = "0" + bstring
            # print(bstring)
            count = 0
            new = list(bstring)
            while count < 2 * bytelen * 4:
                if new[count] == "1":
                    new[count] = "0"
                else:
                    new[count] = "1"
                count = count + 1

            bstring = "".join(new)
            # print(bstring)
            count = 2 * bytelen * 4 - 1
            add = "1"
            while count > -1:
                if new[count] != add:
                    add = "0"
                    new[count] = "1"
                else:
                    new[count] = "0"
                count = count - 1
            bstring = "".join(new)
            # print(bstring)
            hstring = hex(int(bstring, 2))
            hstring = hstring[2:]
            while len(hstring) < 2 * bytelen:
                hstring = "0" + hstring
            count = 0
            new = list(hstring)
            while count < bytelen * 2:
                tmp = new[count]
                new[count] = new[count + 1]
                new[count + 1] = tmp
                count = count + 2
            hstring = "".join(new)
            hstring = hstring[::-1]
            lenhstring = len(hstring)
            if lenhstring > 2 * bytelen:
                hstring = hstring[1:]
            return hstring

    def btd(self, x: bytes) -> int:
        bytelen = len(x)
        count = 0
        dvalue = 0
        while count < bytelen:
            dvalue = dvalue + x[count] * (math.pow(256, count))
            count = count + 1
        bstring = bin(int(dvalue))
        if len(bstring) < 2 * bytelen * 4 + 2:
            return int(dvalue)
        elif len(bstring) > 2 * bytelen * 4 + 2:
            print("Error:Error in byte conversion")
        else:
            bstring = bin(int(dvalue - 1))
            bstring = bstring[2:]
            count = 0
            new = list(bstring)
            while count < 2 * bytelen * 4:
                if new[count] == "1":
                    new[count] = "0"
                else:
                    new[count] = "1"
                count = count + 1
            bstring = "".join(new)
            return (int(bstring, 2)) * (-1)

    def rd(self, bytelen: int) -> bytes:
        x = self.ser.readline()
        while len(x) < bytelen:
            x = x + self.ser.readline()
        return x

    def write(self, x: str) -> None:
        command = bytearray.fromhex(x)
        return self.ser.write(command)

    def identify(self) -> None:
        """Identify itself by flashing its front panel LEDs)"""
        return self.write("230200005001")  # 23, 02, 00, 00, 50, 01

    def set_home_speed(self, speed_deg_s: float) -> None:
        """Set the velocity for homing

        Parameters
        ----------
        speed_deg_s : int
            rotation sppeed in degree/s.
        """
        set_home_params: str = "40040E00d001"
        channel: str = "0100"
        home_direction: str = "0200"
        limit_switch: str = "0100"
        velocity: str = self.dth(int(7329109 * speed_deg_s), 4)
        offset_distance: str = self.dth(self.angle_to_DU(0), 4)
        self.write(
            set_home_params
            + channel
            + home_direction
            + limit_switch
            + velocity
            + offset_distance
        )
        return None

    def home(self) -> None:
        """Start a home move

        MGMSG_MOT_MOVE_HOME
        TX structure:

        43, 04, "Channel ident", 0x, d, s
        """
        self.set_home_speed(10)
        self.write("430401005001")  ## 43, 04, 01, 00, 50, 01
        return self.rd(6)

    def moverel(self, angle_deg: float) -> None:
        """Start a relative move.

        In this method, the longer version (6 byte header plus 6 data bytes) is used.
        Thus, the third and 4th bytes is "06 00"

        Parameters
        -----------
        anlge_deg: float
            Relative rotation angle in degree.
        """
        rel_position: str = self.dth(self.angle_to_DU(angle_deg), 4)
        channel: str = "0100"
        header = "48040600d001"  ## 48, 04, 06, 00, d0, 01
        cmd: str = header + channel + rel_position
        self.write(cmd)

    def moveabs(self, angle_deg: float) -> None:
        """Start a absolute move.

        Parameters
        ----------
        angle_deg : float
            Absolute angle of the stage head in degree.
        """
        abs_position: str = self.dth(self.angle_to_DU(angle_deg), 4)
        channel: str = "0100"
        header: str = "53040600d001"  # 53, 04, 06, 00, d0, 01
        cmd: str = header + channel + abs_position
        self.write(cmd)
        # return self.rd(20)

    def zerobacklash(self) -> None:
        backlash_position = self.dth(self.angle_to_DU(0), 4)
        channel: str = "0100"
        header: str = "3A040600d001"  # 3A, 04, 06, 00, d0, 01
        cmd: str = header + channel + backlash_position
        self.write(cmd)

    def jog(self) -> bytes:
        """Jog starts

        Returns
        -------
        Start a jog move
        """
        self.write("6a0401015001")  # 6a, 04, 01, 01, 50, 01
        # the first 01 is the channel.
        # the second 01 is the forward jog.
        return self.rd(20)

    def getpos(self) -> float:
        self.write("110401005001")  ## 11, 04, 01, 00, 50, 01
        bytedata: bytes = self.rd(12)[8:]
        x = self.DU_to_angle(self.btd(bytedata))
        return float("%.3f" % x)


"""
The source and destination fields require some further explanation.
In general, as the name suggests, they are used to indicate the
source and destination of the message. In non-card- slot type of
systems the source and destination of messages is always unambiguous,
as each module appears as a separate USB node in the system.
In these systems, when the host sends a message to the module,
it uses the source identification byte of 0x01 (meaning host)
and the destination byte of 0x50 (meaning “generic USB unit”).
(In messages that the module sends back to the host,
the content of the source and destination bytes is swapped.)
"""

"""なので、最後が 01 で終わるのは当然"""
