import pyvisa as pv
import pyvisa.constants
import time

rm = pv.ResourceManager()
print(rm.list_resources())


def now():
    return (time.asctime(time.gmtime(time.time())))


class Keithley_2000():
    def __init__(self, address: str):
        self.address: str = address
        try:
            if "GPIB" in address or "gpib" in address:
                self.inst = rm.open_resource(address, )
            else:
                self.inst = rm.open_resource(
                    address,
                    baud_rate=19200,
                    # parity=pv.constants.Parity.odd,
                    data_bits=8,
                    read_termination="\r"
                )
        except Exception as e:
            print(e)

    def name(self):
        try:
            print(self.inst.query("*IDN?"))
            return self.inst.query("*IDN?")
        except Exception as e:
            print(self.address, f": FAIL to get ID ({e})")
            return None

    def function(self, function):
        name_dict = {'VAC': 'VOLT:AC',
                     'VDC': 'VOLT:DC',
                     'R4': 'FRES',
                     'CAC': 'CURR:AC',
                     'R2': "RES",
                     'CDC': 'CURR:DC',
                     'FREQ': 'FREQ',
                     'TEMP': 'TEMP',
                     'PER': 'PER',
                     'DIOD': 'DIOD',
                     'CONT': 'CONT'}

        try:
            self.inst.write(f":FUNC \'{name_dict[function]}\'")
            print(f"func set to {self.inst.query(':FUNC?')}")
            if self.inst.query(":FUNC?").strip()[1:-1] != name_dict[function]:
                raise KeyError(f'wrong key {self.inst.query(":FUNC?").strip()} != {name_dict[function]}')
            return self.inst.query(":FUNC?")
        except Exception as e:
            print(self.address, f": FAIL to func ({e})")
            return None

    def read(self):
        try:
            #print(self.inst.query(":DATA?"))
            return float(self.inst.query(":DATA?"))
        except Exception as e:
            print(self.address, f": FAIL to read ({e})")
            return None

    def range(self, range=120e6, auto=False):
        if auto == True:
            try:
                self.inst.write(f"FRES:RANG:AUTO 1")
                print(f"range AUTO set to {self.inst.query('FRES:RANG:AUTO?')}")
                return self.inst.query('FRES:RANG:AUTO?')
            except Exception as e:
                print(self.address, f": FAIL to set AUTO ({e})")
                return None
        else:
            try:
                self.inst.write(f"FRES:RANG:UPP {range}")
                time.sleep(1)
                print(f"range set to {self.inst.query('FRES:RANG:UPP?')}")
                return self.inst.query("FRES:RANG:UPP?")

            except Exception as e:
                print(self.address, f": FAIL to range ({e})")
                return None

if __name__ == "__main__":


    R1 = Keithley_2000("ASRL6::INSTR")
    R1.name()
    R1.function(function='R2')
    R1.read()
    R1.range(auto=False)
