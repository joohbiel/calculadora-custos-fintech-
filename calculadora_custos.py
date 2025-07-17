import csv  # Importa o módulo padrão para leitura de arquivos CSV

# --- Funções de Interface do Usuário e Utilitários ---

# Função que exibe o menu principal com as opções disponíveis
def menu():
    print("\n=== Calculadora de Custos - MoneyWise ===")  # Título do sistema exibido ao usuário
    print("1. Custo total por departamento")  # Calcula o custo total (salário + encargos) de cada departamento
    print("2. Custo médio por funcionário ativo")  # Calcula a média de custo dos funcionários com status Ativo
    print("3. Departamento mais e menos custoso")  # Identifica os departamentos com maior e menor custo total
    print("4. Eficiência por ano de experiência")  # Calcula o custo por ano de experiência para cada funcionário
    print("5. Melhor custo-benefício")  # Identifica funcionários com a melhor relação custo por experiência
    print("6. Projeção de economia")  # Estima economia com otimizações de eficiência
    print("0. Sair do programa")  # Encerra o programa

# Função que ativa um recurso escondido ao digitar 99
def easter_egg(codigo):
    """Ativa um recurso escondido ao digitar 99, imprimindo uma mensagem específica."""
    if codigo == 99:
        # Mensagem em hexadecimal: "o segredo está nos pequenos detalhes..."
        mensagem_hex = "6f207365677265646f20657374c3a1206e6f732070657175656e6f7320646574616c6865732e2e2e"
        print(bytes.fromhex(mensagem_hex).decode())  # Converte hexadecimal para texto e imprime

# Função que carrega e trata os dados do arquivo CSV
def carregar_dados():
    """
    Carrega os dados do arquivo desafio.csv, filtrando por funcionários 'Ativo'.
    Realiza o tratamento de salários (vírgula para ponto) e garante experiência >= 0.
    """
    funcionarios = []  # Lista para armazenar dados válidos dos funcionários
    # Abre o arquivo CSV com codificação UTF-8
    with open("desafio.csv", encoding="utf-8") as arquivo:
        # Lê cada linha do CSV como um dicionário, usando ',' como delimitador
        leitor = csv.DictReader(arquivo, delimiter=",")
        for linha in leitor:
            # Filtra apenas funcionários com 'status_emprego' como 'ativo'
            if linha["status_emprego"].lower() != "ativo":
                continue
            try:
                # Converte salário de string para float, tratando vírgula como decimal
                salario = float(linha["salario"].replace(",", "."))
                # Garante que experiência seja um inteiro não negativo
                experiencia = max(0, int(linha["experiencia_anos"]))
            except ValueError:
                # Ignora linhas com dados inválidos (ex: salário ou experiência não numéricos)
                continue

            funcionarios.append({
                "nome": linha["nome"],
                "departamento": linha["departamento"],
                "salario": salario,
                "experiencia": experiencia
            })
    return funcionarios  # Retorna a lista com dados tratados dos funcionários

# --- Funções de Cálculo e Análise Financeira ---

def calcular_custo_total(salario):
    """Calcula o custo total de um funcionário (salário + encargos de 80%)."""
    return salario * 1.8  # Multiplica salário por 1.8 para incluir 80% de encargos

def custo_por_departamento(funcionarios):
    """
    Calcula o custo total por departamento e alerta se um departamento tem <2 funcionários.
    """
    custos = {}  # Dicionário para armazenar o custo acumulado por departamento
    departamento_contagem = {} # Dicionário para contar funcionários por departamento

    for f in funcionarios:
        dep = f["departamento"]
        departamento_contagem[dep] = departamento_contagem.get(dep, 0) + 1
        custo = calcular_custo_total(f["salario"])
        custos[dep] = custos.get(dep, 0) + custo

    # Validação obrigatória: Alertar se departamento tem <2 funcionários
    for dep, count in departamento_contagem.items():
        if count < 2:
            print(f"Aviso: O departamento '{dep}' tem menos de 2 funcionários ativos.")
    return custos

def custo_medio(funcionarios):
    """Calcula o custo médio por funcionário ativo."""
    if not funcionarios:
        return 0.0  # Retorna 0.0 para evitar divisão por zero se não houver funcionários
    total_custo = sum(calcular_custo_total(f["salario"]) for f in funcionarios)
    return total_custo / len(funcionarios)

def mais_menos_custoso(custos):
    """Identifica o departamento mais e menos custoso com base nos custos totais."""
    if not custos:
        return None, None  # Retorna None se não houver custos
    mais = max(custos, key=custos.get)  # Departamento com o maior custo
    menos = min(custos, key=custos.get)  # Departamento com o menor custo
    return mais, menos

def calcular_eficiencia(salario, experiencia):
    """
    Calcula o custo por ano de experiência para um funcionário.
    Fórmula: (Salário + encargos (80%)) / max(Experiência, 1).
    Usa max(experiencia, 1) para evitar divisão por zero para experiência = 0.
    """
    custo_total = salario * 1.8
    return custo_total / max(experiencia, 1)

# NOVA FUNÇÃO: Identifica o(s) funcionário(s) com melhor custo-benefício
def encontrar_melhor_custo_beneficio(funcionarios):
    """
    Identifica o(s) funcionário(s) com o menor custo por ano de experiência.
    Retorna uma lista de funcionários, pois pode haver empates.
    """
    if not funcionarios:
        return []

    melhor_eficiencia = float('inf') # Inicializa com um valor infinito para encontrar o mínimo
    funcionarios_melhor_custo_beneficio = []

    for f in funcionarios:
        eficiencia_atual = calcular_eficiencia(f["salario"], f["experiencia"])
        if eficiencia_atual < melhor_eficiencia:
            melhor_eficiencia = eficiencia_atual
            funcionarios_melhor_custo_beneficio = [f] # Nova melhor, reinicia a lista
        elif eficiencia_atual == melhor_eficiencia:
            funcionarios_melhor_custo_beneficio.append(f) # Empate, adiciona à lista
    return funcionarios_melhor_custo_beneficio, melhor_eficiencia

# NOVA FUNÇÃO: Projeta economia com otimizações
def projetar_economia(funcionarios, num_otimizar=3):
    """
    Projeta a economia potencial se os 'num_otimizar' funcionários menos eficientes
    (maior custo por ano de experiência) tivessem sua eficiência reduzida para a média.
    """
    if not funcionarios:
        return 0.0, "Nenhum funcionário ativo para projetar economia."

    # 1. Calcular a eficiência de todos os funcionários e armazenar com seus dados
    funcionarios_com_eficiencia = []
    for f in funcionarios:
        eficiencia = calcular_eficiencia(f["salario"], f["experiencia"])
        funcionarios_com_eficiencia.append({
            "nome": f["nome"],
            "departamento": f["departamento"],
            "salario": f["salario"],
            "experiencia": f["experiencia"],
            "eficiencia": eficiencia,
            "custo_atual": calcular_custo_total(f["salario"])
        })

    # 2. Calcular a eficiência média de todos os funcionários
    total_eficiencia = sum(f['eficiencia'] for f in funcionarios_com_eficiencia)
    media_eficiencia = total_eficiencia / len(funcionarios_com_eficiencia)

    # 3. Identificar os 'num_otimizar' funcionários menos eficientes (maior custo/experiência)
    # Ordena do menos eficiente (maior 'eficiencia') para o mais eficiente (menor 'eficiencia')
    funcionarios_ordenados = sorted(funcionarios_com_eficiencia, key=lambda x: x["eficiencia"], reverse=True)
    top_ineficientes = funcionarios_ordenados[:num_otimizar]

    economia_projetada = 0.0
    detalhes_otimizacao = []

    if not top_ineficientes:
        return 0.0, "Nenhum funcionário para otimizar ou número de funcionários é menor que o limite."

    for f_ineficiente in top_ineficientes:
        # Se a eficiência do ineficiente já for menor ou igual à média, não há economia
        if f_ineficiente['eficiencia'] <= media_eficiencia:
            detalhes_otimizacao.append(f"- {f_ineficiente['nome']} já é mais eficiente que a média, sem economia projetada.")
            continue

        # Calcula o custo-alvo se a eficiência fosse a média
        # custo_alvo / experiencia = media_eficiencia => custo_alvo = media_eficiencia * experiencia
        custo_alvo = media_eficiencia * f_ineficiente['experiencia']

        # Calcula a economia para este funcionário
        economia_individual = f_ineficiente['custo_atual'] - custo_alvo
        if economia_individual > 0: # Garante que só somamos economias reais
            economia_projetada += economia_individual
            detalhes_otimizacao.append(
                f"- {f_ineficiente['nome']} ({f_ineficiente['departamento']}): Custo atual R$ {f_ineficiente['custo_atual']:.2f}, "
                f"Custo alvo R$ {custo_alvo:.2f}, Economia R$ {economia_individual:.2f}"
            )
        else:
             detalhes_otimizacao.append(f"- {f_ineficiente['nome']} não gera economia neste cenário (custo alvo maior ou igual ao atual).")

    if economia_projetada == 0:
        return 0.0, "Não foi possível projetar economia significativa com este cenário de otimização."
    return economia_projetada, "\n".join(detalhes_otimizacao)


# --- Função Principal de Execução ---

def executar():
    """Função principal que executa o sistema interativo da Calculadora de Custos."""
    while True:
        menu()  # Exibe o menu principal
        escolha = input("Escolha uma opção: ")  # Recebe a escolha do usuário

        if escolha == "0":  # Opção para sair do programa
            print("Saindo do programa. Até mais!")
            break

        elif escolha == "99":  # Opção para ativar a função especial (Easter Egg)
            easter_egg(99)

        elif escolha == "1":  # Custo total por departamento
            dados = carregar_dados()
            if not dados:
                print("Nenhum funcionário ativo encontrado para calcular o custo por departamento.")
                continue
            custos = custo_por_departamento(dados)
            print("\nCusto total por departamento:")
            if not custos:
                print("Nenhum custo calculado. Verifique os dados dos funcionários.")
            for dep, valor in custos.items():
                print(f"{dep}: R$ {valor:.2f}")

        elif escolha == "2":  # Custo médio por funcionário ativo
            dados = carregar_dados()
            if not dados:
                print("Nenhum funcionário ativo encontrado para calcular o custo médio.")
                continue
            media = custo_medio(dados)
            print(f"\nCusto médio por funcionário ativo: R$ {media:.2f}")

        elif escolha == "3":  # Departamento mais e menos custoso
            dados = carregar_dados()
            if not dados:
                print("Nenhum funcionário ativo encontrado para identificar o departamento mais/menos custoso.")
                continue
            custos = custo_por_departamento(dados)
            if not custos:
                print("Nenhum custo por departamento calculado. Não é possível identificar o mais/menos custoso.")
                continue
            mais, menos = mais_menos_custoso(custos)
            print(f"\nDepartamento mais custoso: {mais}")
            print(f"Departamento menos custoso: {menos}")

        elif escolha == "4":  # Eficiência por ano de experiência
            dados = carregar_dados()
            if not dados:
                print("Nenhum funcionário ativo encontrado para calcular a eficiência por experiência.")
                continue
            print("\nEficiência por ano de experiência (Custo / Ano de Experiência):")
            eficiencias = []
            for f in dados:
                eficiencia = calcular_eficiencia(f["salario"], f["experiencia"])
                eficiencias.append({"nome": f["nome"], "departamento": f["departamento"], "eficiencia": eficiencia})

            # Ordena do mais eficiente (menor custo/experiência) para o menos eficiente
            eficiencias_ordenadas = sorted(eficiencias, key=lambda x: x["eficiencia"])

            for item in eficiencias_ordenadas:
                print(f"- {item['nome']} ({item['departamento']}): R$ {item['eficiencia']:.2f} por ano de experiência")

        elif escolha == "5":  # Melhor custo-benefício
            dados = carregar_dados()
            if not dados:
                print("Nenhum funcionário ativo encontrado para identificar o melhor custo-benefício.")
                continue
            
            melhores_funcionarios, melhor_eficiencia = encontrar_melhor_custo_beneficio(dados)

            if not melhores_funcionarios:
                print("Não foi possível identificar funcionários com melhor custo-benefício.")
            else:
                print(f"\nFuncionário(s) com o MELHOR Custo-Benefício (Custo de R$ {melhor_eficiencia:.2f} por ano de experiência):")
                for f in melhores_funcionarios:
                    print(f"- {f['nome']} (Departamento: {f['departamento']})")

        elif escolha == "6":  # Projeção de economia
            dados = carregar_dados()
            if not dados:
                print("Nenhum funcionário ativo encontrado para projetar economia.")
                continue
            
            # Você pode ajustar o número de funcionários a otimizar (ex: 3, 5, etc.)
            economia, detalhes = projetar_economia(dados, num_otimizar=3) # Otimiza os 3 menos eficientes

            print(f"\n--- Projeção de Economia Potencial ({'3' if detalhes and 'Nenhum funcionário para otimizar' not in detalhes else 'N/A'} menos eficientes) ---")
            print(f"Economia total projetada: R$ {economia:.2f}")
            print("\nDetalhes da Otimização:")
            print(detalhes)
            
        else:  # Para opções ainda não implementadas
            print("Função ainda não implementada. Por favor, escolha uma opção válida.")

# Ponto de entrada da aplicação
if __name__ == "__main__":
    executar()  # Inicia o programa
