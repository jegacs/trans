#!/usr/bin/python3
import sys, spidev, socket, time, RPi.GPIO as gpio, array, math
import copy

#gpio.setmode(gpio.BCM)
#gpio.setup(17, gpio.OUT)
def mycrc(data):
    raw_data = []
    for byte in data:
        for b in range(0,8):
            raw_data.append( 0x01&(byte >> b) )
    c = [0]*3
    c_xor = [0]*3
    for input in raw_data:
        #print(c, input)
        c_xor[0] = (c[2]^input)
        c_xor[1] = ((c[0]^c[2])^input)
        c_xor[2] = ((c[1]^c[2])^input)
        #print(c_xor)
        c[0] = c_xor[0] # Registro de corrimiento
        c[1] = c_xor[1] # Registro de corrimiento
        c[2] = c_xor[2] # Registro de corrimiento
    #print(c)
    crcvalue = ((0x01&c[2]) << 2) | ((0x01&c[1]) << 1) | (0x01&c[0])
    return crcvalue

def get_adc(channel):
    # Only 2 channels 0 and 1 else return -1
    if ((channel > 1) or (channel < 0)):
        return -1
    r = spi.xfer2([1,(2+channel)<<6,0])

    ret = ((r[1]&0x0F) << 8) + (r[2])
    return ret

def getMeasure(channel):
    tempval = 0
    for x in range(0, 9):
        tempval += get_adc(channel)
        
        #Get the prom
    promval = tempval/10
    return promval

def send_frame(s, tramas, iden, n = None, error = None, errorpos = None):
    global recovertrama
    if n is None:

        del tramas[:]
        for w in range(0, 7):
            trama.append(ord('A'))
            trama.append(iden)
            trama.append(ord('1'))
            for i in range(0, 5):
                lectura = getMeasure(0)*256.0/4096.0
                trama.append(ord(chr(int(lectura))))

            trama.append(ord('2'))
            for i in range(0, 5):
                lectura = getMeasure(1)*256.0/4096.0
                trama.append(ord(chr(int(lectura))))
            
            trama.append(ord('F'))
            trama.append(mycrc(trama))
            if (error is not None) and (w == errorpos):
                recovertrama = copy.copy(trama)
                print(recovertrama)
                newtrama = copy.copy(trama)
                newtrama[errorpos] = error
                tramas.append(copy.copy(newtrama))
                del newtrama
            else:
                tramas.append(copy.copy(trama))
            iden = iden + 1
            if iden > 7:
                iden = 0
            
            del trama[:]
    else:
        for x in range(0,n+1):
            tramas.pop(0) # Eliminamos las tramas anteriores a la que  tuvo error.
        tramas.insert(0, recovertrama)

        print("Tramas a enviar ")
        for i in tramas:
            print(i)
    
        iden = n
        for i in range (0, len(tramas)):
            iden = iden + 1
            if(iden > 7):
                iden = 0

        for w in range(0, 7 - len(tramas)):
            trama.append(ord('A'))
            trama.append(iden)
            trama.append(ord('1'))
            for i in range(0, 5):
                lectura = getMeasure()*256.0/4096.0
                trama.append(ord(chr(int(lectura))))

            trama.append(ord('2'))
            for i in range(0, 5):
                trama.append(0)
            
            trama.append(ord('F'))
            trama.append(mycrc(trama))
            # print (trama)
            iden = iden + 1
            if iden > 7:
                iden = 0
            tramas.append(copy.copy(trama))
            del trama[:]
    for t in tramas:
        clientsocket.send(t)
        print(t)
    gobackn = array.array('B', clientsocket.recv(2))
    print("Confirmacion" ,gobackn)
    return gobackn[1], iden

recovertrama = array.array('B')
try:

    gobackn = 0
    iden = 0
    tramas = []
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('', 1000))
    serversocket.listen(5)

    spi = spidev.SpiDev()
    spi.open(0,0)

    clientsocket, addr = serversocket.accept()
    print ("Conextion establecida")
    while True:
        trama = array.array('B')
        #gobackn, iden = send_frame(clientsocket, tramas, iden, error=100, errorpos=5)
        #print (gobackn, iden, tramas)
        # gobackn, iden = send_frame(clientsocket, tramas, iden)
        # print (gobackn, iden, tramas)
        #if ((gobackn - iden != 0)):
        #    print("Error")
        gobackn, iden = send_frame(clientsocket, tramas, iden)
        
        #input("Enter para siguiente trama")


except (KeyboardInterrupt, SystemExit):
    # clientsocket.close()
    sys.exit()
