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
    
    def virtual(self):
        self.type = [CoreType.virtual]
    
    def io(self):
        self.type.append(CoreType.io)
    
    def idle(self):
        self.type = [CoreType.idle]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CPU Pinning script')
    parser.add_argument('--total-cores', type=int, required=True, help='Total count of cores')
    parser.add_argument('--threads-per-core', type=int, required=True, help='Thread per core')
    parser.add_argument('--io-threads', type=int, required=True, help='Count of emulator pins')
    parser.add_argument('--system-cores', type=str, required=True, help='List of system cores')
    parser.add_argument('--virtual-cores', type=int, required=True, help='Count of virtual cores')

    def is_io(pin: CorePinning):
        return CoreType.io in pin.type
    
    def is_virtual(pin: CorePinning):
        return CoreType.virtual in pin.type
    
    def is_system(pin: CorePinning):
        return CoreType.system in pin.type

    def is_idle(pin: CorePinning):
        return CoreType.idle in pin.type
    
    args = parser.parse_args()
    args.system_cores = args.system_cores.split(',')

    pinnings = []
    virt_cnt = 0
    io_thread_cnt = 0

    # default pin state
    for i in range(0, args.total_cores):
        pin = CorePinning(i, CoreType.idle)
        if(str(pin.num) in args.system_cores):
            pin.system()
            pin.io()

        else:
            if virt_cnt < args.virtual_cores:
                pin.virtual()
                virt_cnt += 1
        pinnings.append(pin)

    print(f"<vcpu placement='static'>{int(args.virtual_cores)}</vcpu>")
    print(f"<cpu mode='host-passthrough' check='none' migratable='on'>")
    print(f"\t<topology sockets='1' dies='1' clusters='1' cores='{int(args.virtual_cores/args.threads_per_core)}' threads='{args.threads_per_core}'/>")
    print(f"</cpu>")
    print(f"<iothreads>{args.io_threads}</iothreads>")
    print(f"<cputune>")
    i=0
    for pin in filter(is_virtual, pinnings):
        print(f"\t<vcpupin vcpu='{i}' cpuset='{pin.num}'/>")
        i += 1
    print(f"\t<emulatorpin cpuset='{",".join(args.system_cores)}'/>")
    i=1
    for pin in range(0, args.io_threads):
        print(f"\t<iothreadpin iothread='{i}' cpuset='{",".join(args.system_cores)}'/>")
        i += 1
    print(f"</cputune>")
