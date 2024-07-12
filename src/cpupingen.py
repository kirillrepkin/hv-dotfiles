from enum import Enum
import argparse

class CoreType(Enum):
    system = 'system'
    virtual = 'virtual'
    io = 'io'
    idle = 'idle'

    def __repr__(self):
        return self.value

class CorePinning:
    num: int
    type: [CoreType]

    def __init__(self, num: int, type: CoreType):
        self.num = num
        self.type = [type]
    
    def __repr__(self):
        return f'c:{self.num}-{self.type}'

    def system(self):
        self.type = [CoreType.system]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CPU Pinning script')
    parser.add_argument('--total-cores', type=int, required=True, help='Total count of cores')
    parser.add_argument('--threads-per-core', type=int, required=True, help='Thread per core')
    parser.add_argument('--io-threads', type=int, required=True, help='Count of emulator pins')
    parser.add_argument('--system-cores', type=str, required=True, help='List of system cores')
    
    args = parser.parse_args()
    args.system_cores = args.system_cores.split(',')

    pinnings = []

    for i in range(0, args.total_cores):
        pinnings.append(CorePinning(i, CoreType.idle))

    for pin in pinnings:
        if(str(pin.num) in args.system_cores):
            pin.system()
    
    print(pinnings)
