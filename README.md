# Batalhão Inteligência Artificial para jogar WAR
<img src="https://github.com/jeielss/IA-WAR/blob/main/foto.png?raw=true" alt="BIA">

Esse é um projeto de Inteligência Artificial desenvolvido para competição ABII Challenge 2023. O projeto consiste em utilizar visão computacional para realizar a leitura do tabuleiro da [plataforma de WAR da Grow Games](https://play.wargrow.com.br/), processar as informações e gerar jogadas para serem inseridas no tabuleiro.

## Visão computacional
- A leitura da tela é realizada por meio de um "print"
- A biblioteca OpenCV foi utilizada para o pré-processamento gráfico
- Para a leitura das informações foram testados os modelos OCR de: Tesseract, TensorFlow, Keras.
- Os testes consistiram em obter as respostas do modelo para diversas etapas no jogo. Não foi realizado treinamento em nenhum dos modelos.
- O modelo que se sobressaiu foi o Keras OCR, no entanto todos apresentaram erros maiores que 20% na avaliação de textos numéricos unitários, o que não é aceitável, já que pode prejudicar completamente um turno de jogada do jogo.
- A solução desenvolvida foi sempre inserir mais um caractere númerico no pré-processamento da imagem, assim o modelo apresentava um desempenho muito superior (cerca de 95% de acurácia no modelo Keras OCR)

## Inteligência Artifical
- A inteligência do código se baseia no algoritmo de fluxo máximo com profundidade limitada, juntamente a estrátegia do jogo de aumentar seu território com mais tropas, além da predefinição de critérios de ataque e deslocamento de tropas para as fronteiras com o menor caminho possível.
