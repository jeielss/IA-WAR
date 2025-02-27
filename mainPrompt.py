

import time
import os
from BIA import *

#Interface Prompt
print("BIA pronta!")
cont = 4
entrada = input("Digite r ou o nome de um país:\n")
while entrada:
    if entrada.upper() == "R":
        image = cv2.imread(f"tela{cont}.png")
        imagem_processada, paises, rect_acoes, rect_jogador = encontraPaises(image, jogadores, territorios)
        inicio = time.time() # inicio
        print(f"{lerRect(image, rect_jogador)}: {lerRect(image, rect_acoes)}")
        fim = time.time()
        print(f"Tempo areas: {fim - inicio}")

        inicio = time.time() # inicio
        AtualizaTodosPaises(paises, image)
        fim = time.time()
        print(f"Tempo leitura ocr: {fim - inicio}")

        cv2.imshow("Reconhecimento", imagem_processada)
        cv2.waitKey()
        cv2.destroyAllWindows
    elif entrada in paises.keys():
        pais = paises[entrada]
        print(f"{entrada}: {pais[4]}\n{pais}")
        img_width = 1000
        img_height = int(imagem_processada.shape[0]/ imagem_processada.shape[1] * img_width )
        pais_sublinhado = imagem_processada.copy()
        cv2.rectangle(pais_sublinhado, pais[0:2], pais[2:4], (0,255,0), 2)
        pais_sublinhado = cv2.resize(imagem_processada, (img_width, img_height))
        cv2.imshow(entrada, pais_sublinhado)
        cv2.waitKey()
    cont+=1
    if cont > 4: cont = 0
    entrada = input("Digite r ou o nome de um país:\n")
    cv2.destroyAllWindows()