import serial
import time
import consult_interface as ci

# used `socat -d -d pty,raw,echo=0 pty,raw,echo=0` to start a loopback
# result:
# 2024/07/31 13:39:33 socat[511425] N PTY is /dev/pts/9
# 2024/07/31 13:39:33 socat[511425] N PTY is /dev/pts/10
# 2024/07/31 13:39:33 socat[511425] N starting data transfer loop with FDs [5,5] and [7,7]

write_port = serial.Serial('/dev/pts/9', baudrate=9600, timeout=None)
read_port = serial.Serial('/dev/pts/10', baudrate=9600, timeout=None)

write_port.write(b'\x5A\x0B\x5A\x01\x5A\x08\x5A\x0C\x5A\x0D\x5A\x03\x5A\x05\x5A\x09\x5A\x13\x5A\x16\x5A\x17\x5A\x1A\x5A\x1C\x5A\x21\xF0')

# sleep for 1 second
time.sleep(1)
print(f'There are {read_port.in_waiting} bytes available to read.')
incomingData = read_port.read_all()
if incomingData:
    for byte in incomingData:
        if byte == 0x5A or byte == 0xF0:
            print()
        # print in pretty hex
        print(f'{byte:02X}', end=' ')

print()
print('----------------------------')
command = ci.params_to_command([ci.Definition.parameters[7]])
for b in command:
    if b == 0x5A or b == 0xF0:
        print()
    print(f'{b:02X}', end=' ')
