#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
from datetime import datetime

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)




def main():
    try:

        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        
        print("Abriu a comunicação")
        
        #Codigo Predro

        com1.enable()
        print("esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1) 

        arq = open("Server2.txt", "x")

        Error = False
        
        lista_de_comandos = []
        #Começando a receber os dados  
        numero_de_comandos = 1
        print("começo")
        ocioso = True
        servidorTrabalhando = False
        server_ID = b'\xEE'
        server_ID_int = int.from_bytes(server_ID, byteorder='big')
        while ocioso == True:
            
            
            if ocioso == True:
                
                firstConnection, nRx = com1.getData(14)
                
                arq.write(f"{datetime.now()} / receb / 1 / {len(firstConnection)}\n")
                firstHeader = firstConnection[0:9]
                #print("amigo estou aqui")
                if firstHeader[0] ==  1:
                    if firstHeader[1] == server_ID_int:
                        ocioso = False
                        totalPacotes = firstHeader[3]
                        #print("amigo estou aqui2")
                    else:
                        time.sleep(1)
                else:
                    time.sleep(1)
            
        
        

        
        confirmacao = b'\x02'
        Pacote_de_confimarcao = bytearray()
        header_Server =  confirmacao + b'\x00'*9
        eop_Server = b'\xAA\xBB\xCC\xDD'
        Pacote_de_confimarcao =  header_Server + eop_Server
        com1.sendData(Pacote_de_confimarcao)

        imagem = bytearray()
        Contagem_Pacotes = 0
        #print("amigo estou aqui3")
        servidorTrabalhando = True
        timer1 = time.time()
        timer2 = time.time()
        timeoutforcado = False
        while servidorTrabalhando == True: 
            
            if timeoutforcado == True:
                time.sleep(30)
                timeoutforcado = False
                      
            if Contagem_Pacotes <= totalPacotes - 1:
                timer1 = time.time()
                timer2 = time.time()
                listaHeader = []
                pacoteBytes = Contagem_Pacotes.to_bytes(1,byteorder='big')
               
                if not com1.rx.getIsEmpty():
                    Header, nheader = com1.getData(10)
                    print(f'essa é a lista 1: {Header}')
                
                    listaHeader = Header[0:9]

                    if listaHeader[0]==5:
                        ocioso = True
                        confirmacao = b'\x05'
                        header_Server = confirmacao + server_ID + b'\x00'*4 + pacoteBytes +  b'\x00'*3
                        arq.write(f"{datetime.now()} / recebido / 5 / {len(header_Server)+len(eop_Server)}\n")   
                        #print("Time Out")  
                        com1.disable()
                        servidorTrabalhando = False


                    if listaHeader[0]==3:
                        tamanho_do_payload = listaHeader[5]
                        payload,npayload = com1.getData(tamanho_do_payload)
                        print(f'essa é a lista 2: {tamanho_do_payload}')
                        eof_client,nclient = com1.getData(4)
                        arq.write(f"{datetime.now()} / receb / 3 / {len(header_Server)+len(eop_Server)}\n")
                    
                        if listaHeader[4] == Contagem_Pacotes and eof_client ==  b'\xAA\xBB\xCC\xDD' :
                            print("Recebido Pacote")
                            confirmacao = b'\x04'
                            header_Server = confirmacao + server_ID + b'\x00'*4 + pacoteBytes +  b'\x00'*3
                            Pacote_de_confimarcao =  header_Server + eop_Server
                            com1.sendData(Pacote_de_confimarcao)
                            time.sleep(0.05)
                            arq.write(f"{datetime.now()} / envio / 4 / {len(header_Server)+len(eop_Server)}\n")
                            Contagem_Pacotes += 1
                            imagem += payload   
                        else:
                            print("Pacote fora de ordem")
                            confirmacao = b'\x06'
                            header_Server = confirmacao + server_ID + b'\x00'*4 + pacoteBytes +  b'\x00'*3
                            Pacote_de_confimarcao =  header_Server + eop_Server
                            com1.sendData(Pacote_de_confimarcao)
                            time.sleep(0.05)
                            arq.write(f"{datetime.now()} / envio / 6 / {len(header_Server)+len(eop_Server)}\n")

               
                
                else:
                    time.sleep(0.3)
                    tempo = time.time()
                    print(f"tempo1: {tempo - timer2}")
                    if tempo - timer2 > 20:
                        ocioso = True
                        confirmacao = b'\x05'
                        header_Server = confirmacao + server_ID + b'\x00'*4 + pacoteBytes +  b'\x00'*3
                        Pacote_de_confimarcao =  header_Server + eop_Server
                        com1.sendData(Pacote_de_confimarcao)
                        time.sleep(0.05)
                        arq.write(f"{datetime.now()} / envio / 5 / {len(header_Server)+len(eop_Server)}\n")   
                        print("Time Out")  
                        com1.disable()
                        servidorTrabalhando = False
                    else:
                        if tempo - timer1 >2 :
                            #print(f"eu quero este cara: {Contagem_Pacotes}")
                            confirmacao = b'\x04'
                            header_Server = confirmacao + server_ID + b'\x00'*4 + pacoteBytes +  b'\x00'*3
                            Pacote_de_confimarcao =  header_Server + eop_Server
                            com1.sendData(Pacote_de_confimarcao)
                            time.sleep(0.05)
                            arq.write(f"{datetime.now()} / envio / 4 / {len(header_Server)+len(eop_Server)}\n")
                            timer1 = time.time()  
                             
            else:
                print("Operação concluída com sucesso")     
                  
                servidorTrabalhando = False
                ocioso = False
                
       # erro = 0 # condição de erro
        #arraydebites = bytearray()
        #if erro == 1:
        #    numero_de_comandos += 1
        #elif erro == 2:
        #    time.sleep(5) 
         #   numero_de_comandos = 0


        if Error:
            raise Exception("Houve Erro de Conexão")


        




        imagemW = "recebida.png"



        
        #for i in range(len(imagem)):
            #print("recebeu {}" .format(imagem[i]))
        print(f'tamanho imagem = ')
        f = open(imagemW,'wb')
        f.write(imagem)
        f.close()


        
          
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
