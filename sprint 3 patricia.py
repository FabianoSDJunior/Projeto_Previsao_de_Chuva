import csv

arquivo = [
    "posto 504 - Perus.csv",
    "posto 515 - Pirituba.csv",
    "posto 509 - Freguesia do Ó.csv",
    "posto 510 - Santana - Tucuruvi.csv",
    "posto 1000944 - Tremembé.csv",
    "posto 540 - Vila Maria - Guilherme.csv",
    "posto 1000852 - Santo Amaro.csv",
    "posto 1000850 - M Boi Mirim.csv",
    "posto 592 - Cidade Ademar.csv",
    "posto 507 - Barragem Parelheiros.csv",
    "posto 1000300 - Marsilac.csv",
    "posto 1000854 - Campo Limpo.csv",
    "posto 846 - Capela do Socorro - Subprefeitura.csv",
    "posto 1000857 - Capela do Socorro.csv",
    "posto 495 - Vila Mariana.csv",
    "posto 634 - Jabaquara.csv",
    "posto 1000887 - Penha.csv",
    "posto 1000862 - São Miguel Paulista.csv",
    "posto 1000882 - Itaim Paulista.csv",
    "posto 1000859 - Vila Formosa.csv",
    "posto 1000864 - Itaquera.csv",
    "posto 524 - Vila Prudente.csv",
    "posto 1000842 - Butantã.csv",
    "posto 1000848 - Lapa.csv",
    "posto 1000635 - Pinheiros.csv",
    "posto 503 - Sé - CGE.csv",
    "posto 1000840 - Ipiranga.csv",
    "posto 1000860 - Móoca.csv",
    "posto 400 - Riacho Grande.csv",
    "posto 1000876 - Mauá - Paço Municipal.csv",
    "posto 1000880 - Santana do Parnaíba.csv"
]

dados = []
for CSV in arquivo:
     with open(f'C:\\Users\\labsfiap\\PycharmProjects\\pythonProject\\clima_SP_zonas\\{CSV}','r',encoding='UTF-8') as arq:
        teste1 = csv.reader(arq)
        for linha in teste1:
            print(linha)
            dados.append(linha)
