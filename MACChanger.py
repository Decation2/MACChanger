
import subprocess
import os

import getmac

def get_interface_win():
    com = 'getmac /FO csv /NH /V'.split()
    address = getmac.getmac.get_mac_address().replace(":", "-").upper()
    interface_temp = subprocess.check_output(com, shell=False).decode('cp866')
    with open('temp.txt', 'w') as file:
        file.write(interface_temp)
    with open('temp.txt') as file:
        src = file.readlines()
    os.remove('temp.txt')
    for line in src:
        if address in line:
            return line.split(",")[0].replace('"', ""), line.split(",")[-1].replace('"', "").split("_")[-1].strip()

def get_key_reg_win():
    from winreg import ConnectRegistry, HKEY_LOCAL_MACHINE, OpenKey, EnumValue
    devicekey = get_interface_win()[1]
    interface = get_interface_win()[0]
    aKey_dict = [r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0000',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0001',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0002',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0003',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0004',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0005',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0006',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0007',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0008',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0009',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0010',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0011',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0012',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0013',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0014',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0015',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0016',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0017',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0018',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0019',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0020',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0021',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0022',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0023',
                 r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}\0024'
                 ]
    aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    for key in aKey_dict:
        try:
            aKey = OpenKey(aReg, key)
            for n in range(0, 100):
                keyname = EnumValue(aKey, n)
                if keyname[0] == 'NetCfgInstanceId':
                    if keyname[1] == devicekey:
                        return interface, key.split("\\")[-1]
                    break
        except:
            continue

def change_mac_windows(new_mac, interface, key_reg):
    print(f"[+] Changing MAC address for {interface} to {new_mac}")
    com_reg = r'reg add HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{' \
              r'4D36E972-E325-11CE-BFC1-08002BE10318}' + f'\\{key_reg} /v NetworkAddress /d ' + f'{new_mac} /f '
    subprocess.call(com_reg, shell=True)
    subprocess.call(f'netsh interface set interface "{interface}" disabled', shell=True)
    subprocess.call('ping -n 6 127.0.0.1 >nul', shell=True)
    subprocess.call(f'netsh interface set interface "{interface}" enabled', shell=True)
    subprocess.call('ping -n 6 127.0.0.1 >nul', shell=True)

def change_mac_linux(new_mac):
    interface = getmac.getmac._get_default_iface_linux()
    print(f"[+] Changing MAC address for {interface} to {new_mac}")
    subprocess.call(f"ifconfig {interface} down", shell=True)
    subprocess.call(f"ifconfig {interface} hw ether {new_mac}", shell=True)
    subprocess.call(f"ifconfig {interface} up", shell=True)

def os_get(new_macs):
    if getmac.getmac.LINUX:
        new_mac = new_macs.replace("-", ":")
        print(f'[+] Current MAC:{getmac.getmac.get_mac_address()}')
        change_mac_linux(new_mac)
        if getmac.getmac.get_mac_address() == new_mac:
            print(f'[+] MAC address was successfully changed to: {new_mac}')
        else:
            print('[-] MAC address did not get changed')
    if getmac.getmac.WINDOWS:
        new_mac = new_macs.replace(":", "").replace("-", "")
        intkey = get_key_reg_win()
        print(f'[+] Current MAC: {getmac.getmac.get_mac_address()}')
        change_mac_windows(new_mac, intkey[0], intkey[1])
        if getmac.getmac.get_mac_address() == new_macs.lower():
            print(f'[+] MAC address was successfully changed to: {new_mac}')
        else:
            print('[-] MAC address did not get changed')

def main():
    os_get(input('Input Mac to Change: '))


if __name__ == "__main__":
    main()

