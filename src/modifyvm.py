import xml.etree.ElementTree as ET

fname = 'libvirt/domains/hv/windows.xml'
tree = ET.parse(fname)
root = tree.getroot()

for elem_name in ['.//memory', './/currentMemory']:
    elem = tree.findall(elem_name)
    elem[0].text = str(16*1024*1024)
    tree.write(fname)