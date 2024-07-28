import os
import argparse
import xml.etree.ElementTree as ET
from cpupingen import SystemCpuLayout

fname = 'libvirt/domains/hv/windows.xml'
tree = ET.parse(fname)
root = tree.getroot()

class SystemLayout(SystemCpuLayout):
    memory: int

    def __init__(self, memory: int, total_cores: int, threads_per_core: int, io_threads: int, system_cores: str, virtual_cores: int):
        self.memory = memory
        super().__init__(total_cores, threads_per_core, io_threads, system_cores, virtual_cores)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CPU Pinning script')
    parser.add_argument('--domain', type=str, required=True, help='domain name at hostname domain@hostname')
    parser.add_argument('--memory', type=int, required=True, help='Total RAM in GB')
    parser.add_argument('--layout', type=str, required=True, help='Layout file')
    parser.add_argument('--dry-run', type=bool, required=False, default=False, help='Do not save results')

    args = parser.parse_args()
    domain, hostname = args.domain.split('@')

    xml_file_name = f"libvirt/domains/{hostname}/{domain}.xml"
    if not os.path.exists(xml_file_name):
        raise Exception(f"Domain file {xml_file_name} not found")
        exit(1)

    layout_file_name = f"libvirt/layout/{args.layout}.json"
    if not os.path.exists(layout_file_name):
        raise Exception(f"Layout file {layout_file_name} not found")
        exit(1)

    tree = ET.parse(xml_file_name)
    root = tree.getroot()

    for elem_name in ['.//memory', './/currentMemory']:
        elem = tree.find(elem_name)
        elem.text = str(args.memory*1024*1024)

    for elem_name in ['.//vcpu', './/cpu', './/iothreads', './/cputune']:
        elem = tree.find(elem_name)
        parent = elem.getparent()
        parent.remove(elem)

    if not args.dry_run:
        tree.write(fname)
