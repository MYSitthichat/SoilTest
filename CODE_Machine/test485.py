from pymodbus.client import ModbusSerialClient as ModbusClient

comport = 'COM3'
client = ModbusClient(method='rtu',port=comport,stopbits=1,bytesize=8,parity='N',baudrate=9600,timeout=1)


if client.connect():
    print("Connected to MODBUS device")
    try:
        address = 0x80 
        count = 2        
        unit = 1         

        response = client.read_holding_registers(address, count, unit=unit)
        
        
        if not response.isError():
            print(f"ค่าที่อ่านได้จาก 40081: {response.registers[0]}")
        else:
            print(f"เกิดข้อผิดพลาด: {response}")
        
    except Exception as e:
        print(f"Exception: {e}")
        
    finally:
        client.close()
        
else:
    print("Failed to connect to MODBUS device")

