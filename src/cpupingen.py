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

class SystemCpuLayout:
    total_cores: int
    threads_per_core: int
    io_threads: int
    system_cores: list
    virtual_cores: int

    def __init__(self, total_cores: int, threads_per_core: int, io_threads: int, system_cores: str, virtual_cores: int):
        self.total_cores = total_cores
        self.threads_per_core = threads_per_core
        self.io_threads = io_threads
        self.system_cores = system_cores.split(',')
        self.virtual_cores = virtual_cores

    def make_pins(self):
        pinnings = []
        virt_cnt = 0
        io_thread_cnt = 0
        # default pin state
        for i in range(0, self.total_cores):
            pin = CorePinning(i, CoreType.idle)
            if(str(pin.num) in self.system_cores):
                pin.system()
                pin.io()
            else:
                if virt_cnt < self.virtual_cores:
                    pin.virtual()
                    virt_cnt += 1
            pinnings.append(pin)
        return pinnings

    def to_xml(self, pinnings: [CorePinning]):

        def is_io(pin: CorePinning):
            return CoreType.io in pin.type

        def is_virtual(pin: CorePinning):
            return CoreType.virtual in pin.type

        def is_system(pin: CorePinning):
            return CoreType.system in pin.type

        def is_idle(pin: CorePinning):
            return CoreType.idle in pin.type

        result = []
        result.append(f"<systemcpulayout>")
        result.append(f"<vcpu placement='static'>{self.virtual_cores}</vcpu>")
        result.append(f"<cpu mode='host-passthrough' check='none' migratable='on'>")
        result.append(f"\t<topology sockets='1' dies='1' clusters='1' cores='{int(self.virtual_cores/self.threads_per_core)}' threads='{self.threads_per_core}'/>")
        result.append(f"</cpu>")
        result.append(f"<iothreads>{self.io_threads}</iothreads>")
        result.append(f"<cputune>")
        i=0
        for pin in filter(is_virtual, pinnings):
            result.append(f"\t<vcpupin vcpu='{i}' cpuset='{pin.num}'/>")
            i += 1
        result.append(f"\t<emulatorpin cpuset='{",".join(self.system_cores)}'/>")
        i=1
        for pin in range(0, self.io_threads):
            result.append(f"\t<iothreadpin iothread='{i}' cpuset='{",".join(self.system_cores)}'/>")
            i += 1
        result.append(f"</cputune>")
        result.append(f"</systemcpulayout>")
        return "\n".join(result)

    def print_libvirt_xml(self, pinnings: [CorePinning]):
        print(self.to_xml(pinnings))

    def __repr__(self):
        return f'SystemCpuLayout (t:{self.total_cores}, c:{self.threads_per_core}, io:{self.io_threads}, sys:{','.join(self.system_cores)}, vc:{self.virtual_cores})'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CPU Pinning script')
    parser.add_argument('--total-cores', type=int, required=True, help='Total count of cores')
    parser.add_argument('--threads-per-core', type=int, required=True, help='Thread per core')
    parser.add_argument('--io-threads', type=int, required=True, help='Count of emulator pins')
    parser.add_argument('--system-cores', type=str, required=True, help='List of system cores')
    parser.add_argument('--virtual-cores', type=int, required=True, help='Count of virtual cores')
    
    args = parser.parse_args()
    layout = SystemCpuLayout(
        args.total_cores, 
        args.threads_per_core, 
        args.io_threads, 
        args.system_cores, 
        args.virtual_cores)
    
    pinning = layout.make_pins()
    layout.print_libvirt_xml(pinnings=pinning)
