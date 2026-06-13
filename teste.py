#nome_atleta = "felipe malandrinha"
#posicao = "ponta direita"
#nota_velocidade = 88
#altura = 1.64
#cadastro_premium = True

#print (f"-----------------------")
#print (f"sistema teste NextDraft")
#print (f"-----------------------")
#print (f"nome do atleta:{nome_atleta}")
#print (f"posição do atleta :{posicao}")
#print (f"nota do vaelocidade do atleta: {nota_velocidade}")
#print (f"altura do atleta: {altura}")
#print (f"cadastro: {cadastro_premium}")

#soma_a = int(input("digite o numero:  "))
#soma_b = int(input("digite um numero: "))
#total = soma_a + soma_b

#print(f"total: {total}")
def classificar_velocidade(nota):
    if velocidade >= 80:
        return  "atleta de elite"

    elif  velocidade >= 70:
        return  "iremos analisar"
    else :
        return  "dispensar atleta"


lista_atletas = [
    {"nome": "felipe malandrinha", "velocidade": 88},
    {"nome": "carlos mandioca", "velocidade": 62},
    {"nome": "lucas lindão", "velocidade": 75}
]

print ("INICIANDO VARREDURA NO SISTEMA NEXTDRAFT")

for atleta in lista_atletas:
    nome = atleta["nome"]
    velocidade = atleta["velocidade"]

    status= classificar_velocidade(velocidade)

   
    print(f"nome: {nome}, velocidade: {velocidade}, status: {status}")



#nome_atleta = "felipe malandrinha"
#nota_velocidade = 88

#print ("--------------- ")
#print ("sistema de scout")
#print ("----------------")

#if nota_velocidade >= 80:
    #status_scout = "atleta promissor iremos analisar"

#elif nota_velocidade >= 70:
    #status_scout = "analisaremos"

#else:
    #status_scout = "atleta ainda precisa melhorar"

#print(f"atleta em questao analisado : {status_scout}")
