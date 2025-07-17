#menu_principal.py
%%writefile menu_principal.py
# Importa a classe CSVAnalyzer do arquivo analisador_csv.py
from analisador_csv import CSVAnalyzer 

def menu():
    """Exibe o menu principal com as opções disponíveis."""
    print("\n=== Calculadora de Custos - MoneyWise ===")
    print("1. Custo total por departamento")
    print("2. Custo médio por funcionário ativo")
    print("3. Departamento mais e menos custoso")
    print("4. Eficiência por ano de experiência")
    print("5. Melhor custo-benefício")
    print("6. Projeção de economia")
    print("0. Sair do programa")
    # A linha do Easter Egg foi removida daqui

def executar():
    """Função principal que executa o sistema interativo da Calculadora de Custos."""
    # Cria uma única instância de CSVAnalyzer que será usada durante toda a execução
    analyzer = CSVAnalyzer()

    while True:
        menu() # Exibe o menu principal
        escolha = input("Escolha uma opção: ") # Recebe a escolha do usuário

        # Usa o método process_command da classe CSVAnalyzer para lidar com a escolha
        # Ele já tenta carregar os dados do Google Sheets e valida automaticamente
        resultado = analyzer.process_command(escolha)
        
        print(f"\n{resultado}") # Imprime o resultado retornado pelo process_command

        # Condição de saída para o loop
        if escolha == "0":
            break # Se a escolha for '0', sai do loop e encerra o programa

# Ponto de entrada da aplicação
if __name__ == "__main__":
    executar() # Inicia o programa interativo
