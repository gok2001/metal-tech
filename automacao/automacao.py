import requests
import time


while True:
    for port in range(1,4):
       url = f'http://10.110.12.41/iolinkmaster/port[{port}]/iolinkdevice/pdin/getdata'

       try:
            response = requests.get(url, timeout=0.03)

            if response.status_code == 200:
                dados = response.json()

                valor_em_hex = dados["data"]["value"]

                valor_decimal = int(valor_em_hex, 16)

                if(port == 1):
                    sensor = "Distância"
                elif(port == 2):
                    sensor = "Capacitivo"
                elif(port == 3):
                    sensor = "Indutivo"

                #print(f"Sensor {sensor}: \nValor: {valor_decimal/16} \nCodigo: {dados["code"]}\n")
                print(f"Sensor {sensor}: {dados}")

       except Exception as e:
            print(f"Erro ao ler {port}: {e}")

    print("-" * 30)
    time.sleep(1)
    