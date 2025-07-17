import csv  # Importa o módulo padrão para leitura de arquivos CSV

# Função que exibe o menu principal com as opções disponíveis
def menu():
    print("\n=== Calculadora de Custos - MoneyWise ===")  # Título do sistema exibido ao usuário
    print("1. Custo total por departamento")  # Opção para calcular custo total (salário + encargos) por departamento
    print("2. Custo médio por funcionário ativo")  # Opção para calcular custo médio dos funcionários ativos
    print("3. Departamento mais e menos custoso")  # Opção para identificar departamento mais e menos custoso
    print("4. Eficiência por ano de experiência")  # (A implementar) Custo por ano de experiência
    print("5. Melhor custo-benefício")  # (A implementar) Identificar funcionários mais eficientes em custo
    print("6. Projeção de economia")  # (A implementar) Estimar economia com otimizações
    print("99. Ativar função especial")  # Easter egg - código hexadecimal imprime mensagem específica
    print("0. Sair do programa")  # Encerra o programa

# Função que ativa um recurso escondido ao digitar 99
def easter_egg(codigo):
    if codigo == 99:
        # Mensagem em hexadecimal: "o segredo está nos pequenos detalhes..."
        mensagem_hex = "6f207365677265646f20657374c3a1206e6f732070657175656e6f7320646574616c6865732e2e2e"
        print(bytes.fromhex(mensagem_hex).decode())  # Converte hexadecimal para texto e imprime

# Função que carrega e trata os dados do arquivo CSV
def carregar_dados():
    funcionarios = []  # Lista para armazenar dados válidos dos funcionários
    with open("desafio.csv", encoding="utf-8") as arquivo:  # Abre o arquivo CSV com codificação UTF-8
        # Alterado o delimitador de ';' para ',' porque seu CSV usa vírgula
        # O DictReader usa a primeira linha como cabeçalho para as chaves
        leitor = csv.DictReader(arquivo, delimiter=",")
        for linha in leitor:
            # Acessa a coluna 'status_emprego' conforme o cabeçalho do CSV
            if linha["status_emprego"].lower() != "ativo":
                continue
            try:
                # Acessa a coluna 'salario' conforme o cabeçalho do CSV
                # Usa .replace(",", ".") para garantir que flutuantes com vírgula sejam tratados (embora seu CSV use ponto)
                salario = float(linha["salario"].replace(",", "."))
                # Acessa a coluna 'experiencia_anos' conforme o cabeçalho do CSV
                experiencia = max(0, int(linha["experiencia_anos"]))
            except ValueError:
                # Ignora linhas com dados inválidos (ex: salário ou experiência não numéricos)
                continue

            funcionarios.append({
                "nome": linha["nome"],  # Usa 'nome' conforme o cabeçalho do CSV
                "departamento": linha["departamento"],  # Usa 'departamento' conforme o cabeçalho do CSV
                "salario": salario,  # Salário convertido para float
                "experiencia": experiencia  # Experiência em anos
            })
    return funcionarios  # Retorna a lista com dados tratados dos funcionários

# Função que calcula o custo total (salário + encargos de 80%)
def calcular_custo_total(salario):
    return salario * 1.8  # Multiplica salário por 1.8 para incluir encargos

# Função que calcula o custo total por departamento
def custo_por_departamento(funcionarios):
    custos = {}  # Dicionário para armazenar custo acumulado por departamento
    # Alerta se o departamento tem menos de 2 funcionários, conforme os requisitos
    departamento_contagem = {}
    for f in funcionarios:
        dep = f["departamento"]  # Obtém o departamento do funcionário
        departamento_contagem[dep] = departamento_contagem.get(dep, 0) + 1
        custo = calcular_custo_total(f["salario"])  # Calcula o custo total do funcionário
        custos[dep] = custos.get(dep, 0) + custo  # Acumula custo no departamento

    for dep, count in departamento_contagem.items():
        if count < 2:
            print(f"Aviso: O departamento '{dep}' tem menos de 2 funcionários ativos.")
    return custos  # Retorna dicionário com custo por departamento

# Função que calcula o custo médio por funcionário ativo
def custo_medio(funcionarios):
    if not funcionarios:  # Verifica se lista está vazia para evitar divisão por zero
        return 0.0 # Retorna float 0.0 para consistência
    total = sum(calcular_custo_total(f["salario"]) for f in funcionarios)  # Soma custo total de todos funcionários
    return total / len(funcionarios)  # Retorna média

# Função que identifica os departamentos mais e menos custosos
def mais_menos_custoso(custos):
    if not custos:  # Verifica se o dicionário está vazio
        return None, None
    mais = max(custos, key=custos.get)  # Departamento com maior custo
    menos = min(custos, key=custos.get)  # Departamento com menor custo
    return mais, menos  # Retorna uma tupla (mais, menos)

# Função principal que executa o sistema interativo
def executar():
    while True:
        menu()  # Exibe o menu
        escolha = input("Escolha uma opção: ")  # Recebe a escolha do usuário

        if escolha == "0":  # Caso escolha seja 0, encerra o programa
            print("Saindo do programa. Até mais!")
            break

        elif escolha == "99":  # Caso escolha seja 99, ativa easter egg
            easter_egg(99)

        elif escolha == "1":  # Custo total por departamento
            dados = carregar_dados()  # Carrega dados do CSV
            if not dados:
                print("Nenhum funcionário ativo encontrado para calcular o custo por departamento.")
                continue
            custos = custo_por_departamento(dados)  # Calcula custos por departamento
            print("\nCusto total por departamento:")
            if not custos:
                print("Nenhum custo calculado. Verifique os dados dos funcionários.")
            for dep, valor in custos.items():  # Imprime custo de cada departamento formatado
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

        else:  # Para opções ainda não implementadas
            print("Função ainda não implementada. Por favor, escolha uma opção válida.")

# Ponto de entrada da aplicação
if __name__ == "__main__":
    executar()  # Inicia o programa
