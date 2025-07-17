from analisador_csv import CSVAnalyzer # Pega a parte inteligente do programa (o analisador)

def menu():
    """Mostra todas as opções que você pode escolher no programa."""
    print("\n=== Desafio 3: Calculadora de Custos - Fintech ===") # O título do nosso programa
    print("1. Custo total por departamento") # Para ver o custo de cada área
    print("2. Custo médio por funcionário ativo") # Para ver quanto custa um funcionário em média
    print("3. Departamento mais e menos custoso") # Para ver qual área gasta mais e qual gasta menos
    print("4. Eficiência por ano de experiência") # Para ver o custo em relação à experiência de cada um
    print("5. Melhor custo-benefício") # Para achar quem dá o melhor retorno
    print("6. Projeção de economia") # Para ver quanto a gente pode economizar
    print("0. Sair do programa") # Para fechar o programa

def executar():
    """É quem faz o programa rodar! Pede a opção e mostra o resultado."""
    analyzer = CSVAnalyzer() # Liga a parte inteligente do programa
    
    # Ele já tentou pegar e arrumar os dados assim que ligou
    if not analyzer.data: # Se não conseguiu arrumar os dados
        print("Não foi possível começar o programa porque os dados não estão prontos.") # Avisa que não dá para começar
        return # E desliga

    while True: # Fica repetindo para você poder escolher várias opções
        menu() # Mostra as opções
        escolha = input("Escolha uma opção: ") # Pergunta o que você quer fazer

        resultado = analyzer.process_command(escolha) # Manda o que você escolheu para a parte inteligente do programa resolver
        
        print(f"\n{resultado}") # Mostra o que o programa respondeu

        if escolha == "0": # Se você escolheu sair
            break # Desliga o programa

if __name__ == "__main__": # Isso faz o programa começar quando você o executa
    executar() # Inicia o programa
