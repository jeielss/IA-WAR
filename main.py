import time
import os
from BIA import *
os.environ['CUDA_VISIBLE_DEVICES'] = "0"
from PIL import ImageGrab
import PySimpleGUI as sg


_print = "TelasTeste/tela3.png"
image = cv2.imread(_print)
jogadores = {}
territorios = {}

debug = False
imagem_processada, paises, rect_acoes, rect_jogador = encontraPaises(image, jogadores, territorios)
img = redimensionaProporcional(imagem_processada, 1000)
imgbytes = bytesImgBGR(img)

size = imagem_processada.shape
size_reduzido = img.shape
layout = [[sg.Multiline(key="saida", autoscroll=True, expand_x=True,size=(None, 5))],
          [ sg.Text(text="", key="resultado",expand_x=True, justification="c")],
          [sg.Input(key="entrada", expand_x=True),],
            [sg.Graph((size_reduzido[1],size_reduzido[0]), (0,size[0]),(size[1],0),key="img_tela", enable_events=True)]]

# Create the window

window = sg.Window("BIA", layout)

window.read(1)

window['img_tela'].draw_image(data=imgbytes, location=(0,0))
window['entrada'].bind("<Return>", "_Enter")
atualizar = False
m_cor = "azul"
objetivo = "verde"
prox_acao = "fort"
rect_jogo = []
while True:

    event, values = window.read(500)
    entrada = values["entrada"]
    saida = values["saida"]
    if event == "entrada" + "_Enter":
        if entrada.upper() == "R" or "p=" in entrada:
            jogadores = {}
            territorios = {}
            if entrada.upper() != "R":
                _sp = str(entrada).split('p=')
                if _sp[1].isnumeric():
                    _print = f"TelasTeste/tela{_sp[1]}.png"
                else:
                    saida+=f"Numero invalido!\n"
                    window["entrada"].Update("p=")
                    window["saida"].Update(saida)
                    continue

            if _print != "":
                saida+=f"Imagem: {_print}\n"
                image = cv2.imread(_print)
            imagem_processada, paises, rect_acoes, rect_jogador = encontraPaises(image, jogadores, territorios)
            inicio = time.time() # inicio
            print(f"{lerRect(image, rect_jogador)}: {lerRect(image, rect_acoes)}")
            fim = time.time()
            print(f"Tempo areas: {fim - inicio}")
            saida += f"\nTempo areas: {fim - inicio}"

            inicio = time.time() # inicio
            AtualizaTodosPaises(paises, image, debug= debug)
            fim = time.time()
            print(f"Tempo leitura ocr: {fim - inicio}")
            saida += f"\nTempo leitura ocr: {fim - inicio}"

            img = redimensionaProporcional(imagem_processada, 1000)
            imgbytes = bytesImgBGR(img)
            window['img_tela'].draw_image(data=imgbytes, location=(0,0))
            window["entrada"].Update("")
            window["saida"].Update(saida)

        elif "d=" in entrada:
            if entrada.split("d=")[1] != "1": debug = False
            else : debug = True

            saida+= f"\nDebug={debug}"
            window["entrada"].Update("")
            window["saida"].Update(saida)
        elif "a=" in entrada:
            if entrada.split("a=")[1] != "1": atualizar = False
            else : atualizar = True

            saida+= f"\nAtualizar={debug}"
            window["entrada"].Update("")
            window["saida"].Update(saida)
        elif "c=" in entrada:
            m_cor = entrada.split('c=')[1]
            saida+= f"\nCor={m_cor}"
            window["entrada"].Update("")
            window["saida"].Update(saida)
        elif "o=" in entrada:
            objetivo = entrada.split('o=')[1]
            saida+= f"\nObjetivo={objetivo}"
            window["entrada"].Update("")
            window["saida"].Update(saida)
        elif entrada in paises.keys():
            pais = paises[entrada]
            print(f"{entrada}: {pais[4]} - {pais[5]}\n{pais}")
            window["resultado"].Update(f"{entrada}: {pais[4]} - {pais[5]}")
            #saida += f"\n{entrada}: {pais[4]} - {pais[5]}"

            pais_sublinhado = image.copy()
            pais_sublinhado = redimensionaProporcional(pais_sublinhado, 3000)
            cv2.rectangle(pais_sublinhado, pais[0:2], pais[2:4], (0,255,0), 2)
            pais_sublinhado = redimensionaProporcional(pais_sublinhado,1000)

            imgbytes = bytesImgBGR(pais_sublinhado)
            window['img_tela'].draw_image(data=imgbytes, location=(0,0))
            window["entrada"].Update("")
            #window["saida"].Update(saida)
    elif event == "img_tela":

        x,y = values["img_tela"]
        print(x,y)
        menor = next(iter(paises))
        for nome, pais in paises.items():
            if distanciaPaisPonto(paises[menor], (x,y)) > distanciaPaisPonto(pais, (x,y)):
                menor = nome
        pais = paises[menor]
        print(f"{menor}: {pais[4]} - {pais[5]}\n{pais}")
        window["resultado"].Update(f"{menor}: {pais[4]} - {pais[5]}")
        #saida += f"\n{entrada}: {pais[4]} - {pais[5]}"

        pais_sublinhado = image.copy()
        pais_sublinhado = redimensionaProporcional(pais_sublinhado, 3000)
        cv2.rectangle(pais_sublinhado, pais[0:2], pais[2:4], (0,255,0), 2)
        pais_sublinhado = redimensionaProporcional(pais_sublinhado,1000)

        imgbytes = bytesImgBGR(pais_sublinhado)
        window['img_tela'].draw_image(data=imgbytes, location=(0,0))
        window["entrada"].Update("")
        #window["saida"].Update(saida)
    elif atualizar:
        saida += "\nProcessando..."
        window["saida"].Update(saida)

        while m_cor.lower() not in cores_jogadores.keys():
            m_cor = sg.popup_get_text("Digite a cor da BIA", "Cor")

        while validaObjetivo(objetivo) == False:
            objetivo = sg.popup_get_text("Digite o objetivo da BIA", "Objetivo")
        window.send_to_back()
        image = np.array(ImageGrab.grab())
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if rect_jogo == []:
            rect_jogo = cv2.selectROI("", image)
            cv2.destroyAllWindows()

        _print = ""
        image = image[rect_jogo[1]:rect_jogo[1]+rect_jogo[3], rect_jogo[0]:rect_jogo[0]+rect_jogo[2]]
        window.bring_to_front()
        jogadores = {}
        territorios = {}
        imagem_processada, paises, rect_acoes, rect_jogador = encontraPaises(image, jogadores, territorios)
        img = redimensionaProporcional(imagem_processada, 1000)
        imgbytes = bytesImgBGR(img)
        window['img_tela'].draw_image(data=imgbytes, location=(0,0))
        if len(territorios) != 44:
            rect_jogo = []
            continue

        if m_cor in lerRect(image, rect_jogador):
            acao_atual = lerRect(image, rect_acoes)
            for acao in acoes:
                if acao in acao_atual: acao_atual = acao
            AtualizaTodosPaises(paises, image, debug= debug)
            if acoes.index(acao_atual) >= acoes.index(prox_acao):
                prox_acao = acoes[acoes.index(acao_atual)]
                tomarDecisao(paises,jogadores,objetivo,m_cor, prox_acao)
            else:
                continue
        else:

            prox_acao = "fort"



        atualizar = False
        window["saida"].Update(saida)
print(event)

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
