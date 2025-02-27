import keras_ocr
import cv2
import numpy as np
from PIL import Image
from dicts import *
from coresHSV import *
import io

#inicializando leitor ocr
#keras_ocr.pipeline.recognition.tf.debugging.set_log_device_placement(False)
leitorOCR = keras_ocr.pipeline.Pipeline()
#prediction_groups = pipeline.recognize([cv2.imread("9.png")])



algarismo_referencia = cv2.imread("OCR/8.png")
cores_jogadores = {"azul": [ciano_inf, ciano_sup], "vermelho": [vermelho_inf, vermelho_sup],
                   "verde": [verde_inf, verde_sup], "amarelo": [amarelo_inf, amarelo_sup],
                   "roxo": [roxo_inf, roxo_sup]}



def corrige_num_ocr(leituras, tira_pri_algarismo):

    texto = ""
    for lr in leituras:
        texto+=lr[0]

    texto = str(texto)
    print(texto)
    if tira_pri_algarismo: texto = texto[1:]
    if not texto.isnumeric(): print(f"Falha no OCR: {texto}")
    return texto.strip()

def corTerritorio(hsv, limite_inferior = 0, limite_superior = -1):
    for j, linha_p in enumerate(hsv):
        if (j < limite_inferior) or (j > limite_superior and limite_superior != -1): continue
        for pixel in linha_p:
            for cor, faixa in cores_jogadores.items():
                if pixel[0] >= faixa[0][0] and pixel[0] <= faixa[1][0]:
                    if pixel[1] >= faixa[0][1] and pixel[1] <= faixa[1][1]:
                        if pixel[2] >= faixa[0][2] and pixel[2] <= faixa[1][2]:
                            #print(cor, pixel, faixa[0],faixa[1])
                            return cor
    return "sem_cor"

def temNumLateral(hsv, ini_x, ini_y, fim_x, fim_y, limite_lateral=10, distancia_min=1):
    esquerda = hsv[ini_y:fim_y, ini_x-limite_lateral:ini_x-distancia_min]
    direita = hsv[ini_y:fim_y, fim_x+distancia_min:fim_x+limite_lateral]

    resposta = ""
    for linha_p in esquerda:
        for pixel in linha_p:
            if pixel[0] >= branco_inf[0] and pixel[0] <= branco_sup[0]:
                if pixel[1] >= branco_inf[1] and pixel[1] <= branco_sup[1]:
                    if pixel[2] >= branco_inf[2] and pixel[2] <= branco_sup[2]:
                        resposta += "e"
                        break
        if "e" in resposta: break
    for linha_p in direita:
        for pixel in linha_p:
            if pixel[0] >= branco_inf[0] and pixel[0] <= branco_sup[0]:
                if pixel[1] >= branco_inf[1] and pixel[1] <= branco_sup[1]:
                    if pixel[2] >= branco_inf[2] and pixel[2] <= branco_sup[2]:
                        resposta += "d"
                        break
        if "d" in resposta: break
    return resposta


def listaCaminho(direcoes, territorios):
    id_menor_x = next(iter(territorios))
    for id, t in territorios.items():
        ini_x,ini_y, fim_x,fim_y, q_exe, cor, _ = t
        if ini_x < territorios[id_menor_x][0]:
            id_menor_x = id

    ordenacao = [id_menor_x]
    for direcao in direcoes:
        coordenada = territorios[ordenacao[-1]][0:2]
        id_menor_dist = 0
        menor_dist = 300000
        for id, t in territorios.items():

            ini_x,ini_y, fim_x,fim_y, q_exe, cor, _ = t
            if id in ordenacao:
                continue
            distancia = (ini_x - coordenada[0])**2 + (ini_y - coordenada[1])**2
            distancia = distancia**0.5
            match direcao:
                case "l":
                    if ini_x - coordenada[0] < 0 or abs(ini_x - coordenada[0]) - abs(ini_y - coordenada[1]) < -20:continue
                    if distancia < menor_dist:
                        menor_dist = distancia
                        id_menor_dist = id
                case "o":
                    if ini_x - coordenada[0] > 0 or abs(ini_x - coordenada[0]) - abs(ini_y - coordenada[1]) < -20:continue
                    if distancia < menor_dist:
                        menor_dist = distancia
                        id_menor_dist = id
                case "n":
                    if ini_y - coordenada[1] > 0 or abs(ini_x - coordenada[0]) - abs(ini_y - coordenada[1]) > 20:continue
                    if distancia < menor_dist:
                        menor_dist = distancia
                        id_menor_dist = id
                case "s":
                    if ini_y - coordenada[1] < 0 or abs(ini_x - coordenada[0]) - abs(ini_y - coordenada[1]) > 20:continue
                    if distancia < menor_dist:
                        menor_dist = distancia
                        id_menor_dist = id
        ordenacao += [id_menor_dist]


    return ordenacao

def redimensionaProporcional(imagem, largura):
    img_width = largura
    img_height = int(imagem.shape[0]/ imagem.shape[1] * img_width )
    imagem = cv2.resize(imagem,(img_width,img_height))
    return imagem

def bytesImgBGR(imagem):
    imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    imagem = Image.fromarray(imagem)  # create PIL image from frame
    bio = io.BytesIO()  # a binary memory resident stream
    imagem.save(bio, format= 'PNG')  # save image as png to it
    imgbytes = bio.getvalue()  # this can be used by OpenCV hopefully
    return imgbytes

def tratarImagem(imagem, largura):
    hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)

    #mascara
    mask = cv2.inRange(hsv, branco_inf, branco_sup)
    res = cv2.bitwise_and(imagem,imagem, mask= mask)
    blur = cv2.medianBlur(hsv ,3)

    #redimensionando - 0.3s
    img_width = largura
    img_height = int(imagem.shape[0]/ imagem.shape[1] * img_width )
    mask = cv2.resize(mask,(img_width,img_height))
    res = cv2.resize(res,(img_width,img_height))
    imagem = cv2.resize(imagem,(img_width,img_height))
    blur = cv2.resize(blur,(img_width,img_height))

    #tratando a imagem com os numeros para evitar ruidos
    kernel = np.ones((1, 1), np.uint8)
    res = cv2.dilate(res, kernel, iterations=1)
    res = cv2.erode(res, kernel, iterations=1)

    return imagem, res, blur, (img_width, img_height)

def AtualizaPaises(nomes, paises, imagem, largura_img=3000):
    img_original, img_letras, img_Bhsv, size = tratarImagem(imagem, largura_img)
    img_exercitos = []
    for nome in nomes:
        ini_x,ini_y, fim_x,fim_y, exercitos, cor, id = paises[nome]
        img_exercitos += [img_letras[ini_y:fim_y, ini_x:fim_x]]
        num_hsv = img_Bhsv[ini_y:fim_y, ini_x:fim_x]

        cor_atual = corTerritorio(num_hsv, fim_y-ini_y-5)
        paises[nome][5] = cor_atual

    prediction_groups = leitorOCR.recognize(img_exercitos)
    if len(prediction_groups) == len(nomes):
        for i,nome in enumerate(nomes):
            try: paises[nome][4] = corrige_num_ocr(prediction_groups[i][0][0])
            except: print("Erro: Reconhecimento vazio")
        return 0
    else:
        return 1

def lerRect(imagem, rect, largura_img=3000):
    if len(rect) < 4: return ""
    img, _,_,_ = tratarImagem(imagem, largura_img)
    prediction_groups = leitorOCR.recognize([img[rect[2]:rect[3], rect[0]:rect[1]]])

    retorno = ""
    try:
        for recon in prediction_groups[0]:
            retorno += f"{recon[0]} "
    except: 1

    return retorno.strip()

    print(prediction_groups)
def AtualizaTodosPaises(paises, imagem, largura_img=3000, debug=False):
    img_original, img_letras, img_Bhsv, size = tratarImagem(imagem, largura_img)
    img_exercitos = []
    um_algarismo = []
    for pais in paises.values():
        ini_x,ini_y, fim_x,fim_y, exercitos, cor, id = pais

        img_height = fim_y - ini_y
        img_width = int(algarismo_referencia.shape[1]/ algarismo_referencia.shape[0] * img_height )

        clone = cv2.resize(algarismo_referencia, (img_width, img_height))
        espacamento = 11
        if (fim_x - ini_x) < 60:
            img_exercitos += [np.hstack([clone, img_letras[ini_y:fim_y, ini_x+espacamento:fim_x-espacamento]])]
            um_algarismo += [True]
        else:
            img_exercitos += [img_letras[ini_y:fim_y, ini_x:fim_x]]
            um_algarismo += [False]
        num_hsv = img_Bhsv[ini_y:fim_y, ini_x:fim_x]


        if debug:
            cv2.imshow("", img_exercitos[-1])
            cv2.waitKey()
            cv2.destroyAllWindows()

        cor_atual = corTerritorio(num_hsv, fim_y-ini_y-5)
        pais[5] = cor_atual

    prediction_groups = leitorOCR.recognize(img_exercitos)
    if len(prediction_groups) == len(paises.keys()):
        for i,pais in enumerate(paises.values()):
            try: pais[4] = corrige_num_ocr(prediction_groups[i], um_algarismo[i])
            except: print("Erro: Reconhecimento vazio")
        return 0
    else:
        return 1

def encontraPaises(imagem, jogadores, territorios, largura_img=3000, verbose=False, debug=False):
    imagem = imagem.copy()

    img_original, img_letras, img_Bhsv, img_size = tratarImagem(imagem, largura_img)
    img_width, img_height = img_size

    area_total = img_height * img_width
    filtro_area = [(0.3/100000 * area_total),  (20/100000 * area_total)]
    #selecionando objetos brancos 0.12s
    gray = cv2.cvtColor(img_letras, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    referencia = (0,0)
    cont_terri = 0

    img_exercitos = []
    area_acoes =[]
    area_jogador=[]
    algarismo_parte_num = {}
    #processando cada objeto para selecionar apenas os numeros de exercitos de cada pais
    for contour in contours:

        # Calcular o retângulo delimitador do contorno
        area = cv2.contourArea(contour)

        x, y, width, height = cv2.boundingRect(contour)
        proporcao = width/height #proporcao do objeto, usada para filtragem

        #definindo os limites do retangulo
        ini_y, ini_x = y, x
        fim_y, fim_x = y+height, x+width

        #possivel imagem do numero de exercitos
        num_hsv = img_Bhsv[ini_y-5:fim_y+5, ini_x+5:fim_x+5]

        #obtendo a posicao da referencia/ancora - circulo da africa
        if 0.85 < proporcao < 1.1 and (0.7/1000*area_total) < area < (1.5/1000*area_total) and referencia != 0:
            referencia = (x,y)
            cv2.rectangle(img_original, (ini_x, ini_y), (fim_x, fim_y), (0, 0, 255), 2)

            area_acoes = [ini_x -0.30 * img_size[0], ini_x -0.30 * img_size[0] + img_size[0]/4.7,
                          ini_y + 0.19*img_size[1],ini_y + 0.19*img_size[1] + img_size[1]/18]

            area_jogador = [ini_x -0.29 * img_size[0], ini_x -0.29 * img_size[0] + img_size[0]/4.8,
                          ini_y + 0.02*img_size[1],ini_y + 0.02*img_size[1] + img_size[1]/16]
            area_acoes =  np.array(area_acoes, dtype=int)
            area_jogador =  np.array(area_jogador, dtype=int)

            #print('min H = {}, min S = {}, min V = {}; max H = {}, max S = {}, max V = {}'.format(hsv[:,:,0].min(), hsv[:,:,1].min(), hsv[:,:,2].min(), hsv[:,:,0].max(), hsv[:,:,1].max(), hsv[:,:,2].max()))
            cv2.rectangle(img_original, (area_acoes[0], area_acoes[2]), (area_acoes[1], area_acoes[3]), (0, 0, 255), 2)
            cv2.rectangle(img_original, (area_jogador[0], area_jogador[2]), (area_jogador[1], area_jogador[3]), (0, 0, 255), 2)

        #filtrando cada item encontrado pela area
        if filtro_area[0] < area < filtro_area[1] and proporcao < 1.1:


            #filtrando por cor
            cor = corTerritorio(num_hsv)
            if cor == "sem_cor":
                continue
                hsv = num_hsv[5:15, 0:-1]
                print('min H = {}, min S = {}, min V = {}; max H = {}, max S = {}, max V = {}'.format(hsv[:,:,0].min(), hsv[:,:,1].min(), hsv[:,:,2].min(), hsv[:,:,0].max(), hsv[:,:,1].max(), hsv[:,:,2].max()))
                cv2.imshow(f"A: {area} | P: {proporcao}", img_original[ini_y-10:fim_y+10, ini_x-10:fim_x+10])
                cv2.waitKey()
                cv2.destroyAllWindows()
                continue
            if debug:
                cv2.imshow("", img_letras[ini_y:fim_y, ini_x:fim_x])
                cv2.waitKey()
                cv2.destroyAllWindows()
            NumLateral = temNumLateral(img_Bhsv, ini_x,ini_y, fim_x, fim_y)
            if NumLateral != "":
                algarismo_parte_num[cont_terri] =  NumLateral


            if not cor in jogadores.keys(): jogadores[cor] = 0
            jogadores[cor] += 1


            #definindo a area de leitura
            ini_y -= 3 ; fim_y += 3
            ini_x -= 15 ; fim_x += 15

            #desenhando retangulo na imagem
            cv2.rectangle(img_original, (ini_x, ini_y), (fim_x, fim_y), (0, 255, 0), 2)

            territorios[cont_terri] = [ini_x,ini_y, fim_x,fim_y, -1, cor, cont_terri]
            cont_terri +=1


    ids_ignorar = []
    for id_e, lado_e in algarismo_parte_num.items():
        if id_e in ids_ignorar or not "e" in lado_e: continue
        cont = 0
        while "e" in algarismo_parte_num[id_e] and cont < 100:
            retangulo_e = territorios[id_e][0:4]

            for id_d, lado_d in algarismo_parte_num.items():
                if id_d in ids_ignorar or not "d" in lado_d or id_e == id_d: continue
                retangulo_d = territorios[id_d][0:4]

                meio_d = ((territorios[id_d][2] - territorios[id_d][0])/2 + territorios[id_d][0],
                          (territorios[id_d][3] - territorios[id_d][1])/2 + territorios[id_d][1])
                if retanguloTemPonto(retangulo_e, meio_d):
                    ids_ignorar += [id_d]
                    algarismo_parte_num[id_d] = algarismo_parte_num[id_d].replace("d", "")
                    algarismo_parte_num[id_e] = algarismo_parte_num[id_e].replace("e", "")

                    algarismo_parte_num[id_e] += algarismo_parte_num[id_d]

                    territorios[id_e] = [retangulo_d[0], retangulo_e[1], retangulo_e[2], retangulo_e[3], -1, cor, cont_terri]
                    territorios.pop(id_d)
            cont+=1


    if len(territorios) != 44:
        return img_original,territorios, area_acoes, area_jogador

    #criando dicionario associando cada pais com seu respectivo nome
    nomes = ["vladvostok-2", "alaska", "vancouver", "california", "mexico",
                       "peru", "argentina", "brasil", "venezuela", "nova_york", "ottawa",
                       "labrador", "mackenzie", "groelandia", "islandia", "inglaterra", "frança",
                       "argelia", "congo", "africa_do_sul", "madagascar", "sudao", "egito", "polonia",
                       "alemanha", "suecia", "moscou", "oriente_medio", "aral", "india", "sumatra",
                       "borneo", "australia", "nova_guine", "vietna", "china", "japao",
                       "vladvostok", "alaska-2", "tchita", "mongolia",
                       "omsk", "siberia", "dudinka"]

    #caminho a partir da primeiro pais superior esquerdo
    direcoes = ["l", "s", "s","s", "s", "s", "n", "o", "n", "n", "l", "o", "l","s","s","s","s", "s", "s",
                "l", "n", "n", "n", "o", "n", "s", "s", "l", "s", "s", "l", "s", "n", "o", "n", "l", "n"
                , "l", "o", "s", "o", "l", "o"]

    ordem = listaCaminho(direcoes, territorios)
    paises = {}
    for i, id in enumerate(ordem):
        paises[nomes[i]] = territorios[id]

    if verbose:
        print(paises)
    return img_original, paises, area_acoes, area_jogador

def distanciaPaisPonto(pais, ponto):
    x_pais = pais[0]
    y_pais = pais[1]
    return ((x_pais- ponto[0])**2 + (y_pais - ponto[1])**2)**0.5
def retanguloTemPonto(retangulo, ponto)-> bool:
    ini_x,ini_y, fim_x,fim_y = retangulo

    if ini_x < ponto[0] < fim_x:
        if ini_y < ponto[1] < fim_y:
            return True
    return False

def contarPaisesCorRegião(paises):
    global regioes_macro
    regioes_cor = {}
    for nome, pais in paises.items():
        for regiao, territorios in regioes_macro.items():
            if nome in territorios:
                if regiao not in regioes_cor.keys(): regioes_cor[regiao] = {}
                if pais[5] not in regioes_cor[regiao].keys(): regioes_cor[regiao][pais[5]] = 0
                regioes_cor[regiao][pais[5]]+=1
    return regioes_cor

def tomarDecisao(paises, jogadores, objetivo, m_cor, acao):
    print(contarPaisesCorRegião(paises))

def validaObjetivo(texto):
    if texto == "": return False
    if texto in cores_jogadores.keys():
        return True
    for regiao in texto.split("/"):
        if regiao not in regioes_macro.keys():
            return False
    return True