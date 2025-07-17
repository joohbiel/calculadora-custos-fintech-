import csv # Para ler e escrever arquivos de tabela (CSV)
import urllib.request # Para acessar coisas na internet, como planilhas do Google
import io # Para trabalhar com textos como se fossem arquivos

class CSVAnalyzer:
    """
    Essa é a parte inteligente do programa. Ela pega os dados dos funcionários,
    faz todas as contas de custo e eficiência.
    """
    def __init__(self, sheets_url="https://docs.google.com/spreadsheets/d/1gIFTAgtLZIPCXqy5CaQxQ8s6MVFH2IGl-uG45N1MFJs/edit?usp=sharing"):
        self.data = [] # Aqui vamos guardar os dados limpos dos funcionários que vamos usar
        self.headers = [] # Aqui ficam os nomes das colunas da tabela
        self.raw_data = [] # Dados brutos, como vieram da tabela antes de serem arrumados
        self.google_sheets_url = sheets_url # Onde sua planilha do Google está na internet
        self._load_and_validate_initial_data() # Logo que o programa começa, ele já tenta pegar e arrumar os dados

    def _load_and_validate_initial_data(self):
        """
        Primeiro, a gente tenta pegar os dados da planilha na internet.
        Se não der certo, a gente usa uns dados de emergência que já vêm no programa.
        Depois, a gente dá uma olhada se esses dados estão certinhos.
        """
        load_success, load_message = self._load_from_sheets(self.google_sheets_url) # Tenta pegar os dados da planilha
        
        if not load_success: # Se não conseguiu pegar da internet
            print(f"Aviso: Não consegui pegar os dados da internet ({load_message}). Vou tentar usar os dados de segurança.")
            try:
                # Aqui estão os dados de segurança, caso a planilha da internet não funcione
                csv_content = """nome,idade,cidade,profissao,salario,experiencia_anos,nivel_educacao,status_emprego,data_contratacao,departamento
João Silva,28,São Paulo,Desenvolvedor,5500,3,Superior,Ativo,2021-03-15,TI
Maria Santos,32,Rio de Janeiro,Designer,4200,5,Superior,Ativo,2020-07-22,Marketing
Carlos Oliveira,45,Belo Horizonte,Gerente,8500,12,Pós-graduação,Ativo,2018-11-10,Vendas
Ana Costa,29,Porto Alegre,Analista,3800,2,Superior,Inativo,2022-01-08,Financeiro
Pedro Lima,35,Fortaleza,Desenvolvedor,7200,8,Superior,Ativo,2019-05-18,TI"""
                csv_file = io.StringIO(csv_content) # Transforma o texto dos dados em um arquivo de mentira
                reader = csv.DictReader(csv_file) # Prepara para ler os dados, linha por linha
                self.headers = reader.fieldnames # Guarda os nomes das colunas
                self.raw_data = [row for row in reader] # Pega todas as informações dos funcionários
                load_success = True # Deu certo com os dados de segurança
                load_message = "Dados carregados dos dados de segurança."
            except Exception as e:
                print(f"Erro grave: Não consegui pegar os dados de lugar nenhum: {e}") # Se nem os dados de segurança funcionam
                return False, f"Erro grave: {e}"

        validate_success, validate_message = self._validate_data() # Agora, a gente verifica se os dados estão corretos
        if not validate_success: # Se os dados não estão certinhos
            print(f"Erro ao arrumar os dados: {validate_message}") # Avisa que não conseguiu arrumar
            self.data = [] # Limpa os dados se estiverem bagunçados
        else:
            print(f"Dados prontos para usar! {load_message}. {validate_message}") # Avisa que está tudo certo
        
        return validate_success, validate_message # Diz se deu tudo certo no final

    def _load_from_sheets(self, url):
        """Pega a tabela direto da sua planilha do Google Sheets."""
        if "docs.google.com/spreadsheets/d/" not in url: # Vê se é mesmo uma URL de planilha do Google
            return False, "Essa não parece ser uma URL de Planilha Google."

        sheet_id_part = url.split("d/")[1].split("/")[0] # Pega o pedacinho que identifica sua planilha
        gid_param = f"&gid={url.split('#gid=')[1].split('&')[0]}" if "#gid=" in url else "" # Vê se tem um código para uma aba específica
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id_part}/export?format=csv{gid_param}" # Monta o link para baixar a planilha como CSV

        try:
            with urllib.request.urlopen(csv_url) as response: # Tenta abrir o link
                csv_content = response.read().decode('utf-8') # Lê o que veio e transforma em texto que a gente entende
                csv_file = io.StringIO(csv_content) # Transforma o texto em um arquivo de mentira
                
                reader = csv.DictReader(csv_file) # Prepara para ler a tabela
                self.headers = reader.fieldnames # Guarda os nomes das colunas
                self.raw_data = [row for row in reader] # Pega todas as linhas da tabela
                return True, "Dados da planilha do Google pegos com sucesso." # Avisa que deu tudo certo
        except urllib.error.URLError as e: # Se não conseguiu conectar na internet
            return False, f"Problema para conectar na internet: {e}"
        except Exception as e: # Se deu algum outro problema inesperado
            return False, f"Não consegui pegar os dados: {e}"

    def _validate_data(self):
        """Dá uma geral nos dados, filtra só quem importa e arruma os números."""
        required_headers = ["nome", "departamento", "salario", "experiencia_anos", "status_emprego"] # Nomes de colunas que não podem faltar
        
        if not self.headers or not all(h in self.headers for h in required_headers): # Vê se todas as colunas importantes estão lá
            return False, f"Faltam colunas importantes. Precisa ter: {required_headers}"

        processed_funcionarios = [] # Lista para guardar só os funcionários que servem
        warnings = [] # Lista para avisar sobre problemas em alguma linha
        for i, linha in enumerate(self.raw_data): # Olha cada linha de funcionário
            if linha.get("status_emprego", "").lower() != "ativo": # Se o funcionário não está 'ativo', ignora
                continue
            
            try:
                salario = float(linha.get("salario", "0").replace(",", ".")) # Pega o salário, troca vírgula por ponto e transforma em número
                experiencia = max(0, int(linha.get("experiencia_anos", "0"))) # Pega a experiência, transforma em número e garante que não é negativo

                processed_funcionarios.append({ # Adiciona o funcionário arrumado na lista
                    "nome": linha.get("nome"),
                    "departamento": linha.get("departamento"),
                    "salario": salario,
                    "experiencia": experiencia
                })
            except (ValueError, KeyError) as e: # Se o salário ou experiência vierem bagunçados
                warnings.append(f"Aviso: A linha {i+2} está com algum dado bagunçado (salário ou experiência). Vou ignorar. Erro: {e}") # Avisa que ignorou a linha
                continue # Pula para o próximo funcionário
        
        self.data = processed_funcionarios # Guarda só os funcionários que estão ok
        if not self.data: # Se não sobrou nenhum funcionário depois de arrumar
            return False, "Nenhum funcionário ativo e com dados válidos foi encontrado. Não tem como fazer as contas."
        return True, "Dados arrumados e prontos para as contas!" + ("\n" + "\n".join(warnings) if warnings else "") # Avisa que está tudo certo ou mostra os avisos

    # --- As contas e análises que o programa faz ---

    def _calcular_custo_total(self, salario):
        """Calcula quanto custa um funcionário para a empresa (salário mais todos os extras)."""
        return salario * 1.8 # Multiplica por 1.8 porque são 80% a mais de custos

    def _calcular_eficiencia(self, salario, experiencia):
        """Calcula o custo de um funcionário por cada ano de experiência que ele tem."""
        custo_total = self._calcular_custo_total(salario) # Pega o custo total do funcionário
        return custo_total / max(experiencia, 1) # Divide pelo tempo de experiência (no mínimo 1 para não dividir por zero)

    def custo_por_departamento(self):
        """Mostra o custo total de cada área da empresa e avisa se alguma está com pouca gente."""
        if not self.data: # Vê se tem dados para calcular
            return "Não tem dados de funcionários para calcular o custo por área."
        
        custos = {} # Aqui vamos somar o custo de cada área
        departamento_contagem = {} # Aqui vamos contar quantos funcionários tem em cada área

        for f in self.data: # Para cada funcionário
            dep = f["departamento"] # Pega a área dele
            departamento_contagem[dep] = departamento_contagem.get(dep, 0) + 1 # Conta mais um funcionário para a área
            custos[dep] = custos.get(dep, 0) + self._calcular_custo_total(f["salario"]) # Soma o custo do funcionário no total da área

        output = ["Quanto cada área da empresa custa:"] # Monta a mensagem final
        for dep, count in departamento_contagem.items(): # Para cada área
            if count < 2: # Se a área tem menos de 2 funcionários
                output.append(f"Aviso: A área '{dep}' tem menos de 2 funcionários. Fique de olho!") # Dá um alerta
        
        if not custos: # Se não conseguiu calcular nada
            output.append("Nenhum custo calculado. Será que tem dados de funcionários?")
        else:
            for dep, valor in custos.items(): # Mostra o custo de cada área
                output.append(f"{dep}: R$ {valor:.2f}") # Formata bonitinho o valor
        return "\n".join(output) # Junta tudo em uma mensagem só

    def custo_medio(self):
        """Calcula quanto custa em média cada funcionário ativo na empresa."""
        if not self.data: # Vê se tem dados para calcular
            return "Não tem dados de funcionários para calcular o custo médio."
        total_custo = sum(self._calcular_custo_total(f["salario"]) for f in self.data) # Soma o custo de todos os funcionários
        media = total_custo / len(self.data) # Divide pelo número de funcionários para ter a média
        return f"Custo médio por funcionário ativo: R$ {media:.2f}" # Mostra o resultado

    def mais_menos_custoso(self):
        """Descobre qual área da empresa custa mais e qual custa menos."""
        if not self.data: # Vê se tem dados para calcular
            return "Não tem dados de funcionários para ver qual área custa mais/menos."
        
        custos = {} # Aqui vamos somar o custo de cada área
        for f in self.data: # Para cada funcionário
            dep = f["departamento"] # Pega a área dele
            custos[dep] = custos.get(dep, 0) + self._calcular_custo_total(f["salario"]) # Soma o custo no total da área

        if not custos: # Se não tem custo de área nenhuma
            return "Nenhum custo por área calculado. Não consigo dizer qual custa mais/menos."
        
        mais = max(custos, key=custos.get) # Pega a área com o maior custo
        menos = min(custos, key=custos.get) # Pega a área com o menor custo
        return f"A área que custa mais é: {mais}\nA área que custa menos é: {menos}" # Mostra os resultados

    def eficiencia_por_experiencia(self):
        """Mostra o custo de cada funcionário em relação ao tempo de experiência dele."""
        if not self.data: # Vê se tem dados para calcular
            return "Não tem dados de funcionários para calcular a eficiência por experiência."
        
        eficiencias = [] # Lista para guardar a eficiência de cada um
        for f in self.data: # Para cada funcionário
            if f['experiencia'] == 0 and f['salario'] == 0: # Se o funcionário não tem salário nem experiência, pula
                continue
            eficiencias.append({ # Adiciona o nome, área e a eficiência dele
                "nome": f["nome"],
                "departamento": f["departamento"],
                "eficiencia": self._calcular_eficiencia(f["salario"], f["experiencia"])
            })

        if not eficiencias: # Se não conseguiu calcular a eficiência de ninguém
            return "Não há dados válidos para calcular a eficiência."
        
        eficiencias_ordenadas = sorted(eficiencias, key=lambda x: x["eficiencia"]) # Organiza do mais eficiente para o menos eficiente
        output = ["Quem tem o melhor custo em relação à experiência (Custo por Ano de Experiência):"] # Começa a mensagem
        for item in eficiencias_ordenadas: # Para cada um na lista organizada
            output.append(f"- {item['nome']} ({item['departamento']}): R$ {item['eficiencia']:.2f} por ano de experiência") # Mostra o nome, área e a eficiência
        return "\n".join(output) # Junta tudo em uma mensagem só

    def melhor_custo_beneficio(self):
        """Descobre qual funcionário ou funcionários dão o maior retorno pelo menor custo."""
        if not self.data: # Vê se tem dados para calcular
            return "Não tem dados de funcionários para ver o melhor custo-benefício."

        melhor_eficiencia = float('inf') # Começa com um valor bem alto para achar o menor depois
        funcionarios_melhor_custo_beneficio = [] # Lista para guardar quem é o melhor

        for f in self.data: # Para cada funcionário
            if f['experiencia'] == 0 and f['salario'] == 0: # Se não tem salário nem experiência, pula
                continue
            
            eficiencia_atual = self._calcular_eficiencia(f["salario"], f["experiencia"]) # Calcula a eficiência dele
            if eficiencia_atual < melhor_eficiencia: # Se achou alguém mais eficiente que o melhor até agora
                melhor_eficiencia = eficiencia_atual # Esse é o novo melhor
                funcionarios_melhor_custo_beneficio = [f] # Começa a lista com ele
            elif eficiencia_atual == melhor_eficiencia: # Se achou alguém tão eficiente quanto o melhor
                funcionarios_melhor_custo_beneficio.append(f) # Adiciona ele na lista (empatou)
        
        if not funcionarios_melhor_custo_beneficio: # Se não conseguiu encontrar ninguém
            return "Não consegui achar funcionários com melhor custo-benefício. Vê se os dados de salário e experiência estão certos."
        else:
            output = [f"O(s) funcionário(s) com o MELHOR Custo-Benefício (gastando R$ {melhor_eficiencia:.2f} por ano de experiência):"] # Monta a mensagem
            for f in funcionarios_melhor_custo_beneficio: # Para cada um dos melhores
                output.append(f"- {f['nome']} (Área: {f['departamento']})") # Mostra o nome e a área
            return "\n".join(output) # Junta tudo em uma mensagem só

    def projetar_economia(self, num_otimizar=3):
        """
        Calcula quanto dinheiro a empresa poderia economizar se os funcionários
        menos eficientes melhorassem para a média.
        """
        if not self.data: # Vê se tem dados para calcular
            return "Não tem funcionários para projetar economia."

        funcionarios_com_eficiencia = [] # Lista para guardar todos com a eficiência calculada
        for f in self.data: # Para cada funcionário
            if f['experiencia'] == 0 and f['salario'] == 0: # Se não tem salário nem experiência, pula
                continue
            eficiencia = self._calcular_eficiencia(f["salario"], f["experiencia"]) # Calcula a eficiência
            funcionarios_com_eficiencia.append({ # Adiciona todas as informações e a eficiência
                "nome": f["nome"],
                "departamento": f["departamento"],
                "salario": f["salario"],
                "experiencia": f["experiencia"],
                "eficiencia": eficiencia,
                "custo_atual": self._calcular_custo_total(f["salario"])
            })
        
        if not funcionarios_com_eficiencia: # Se não tem dados para projetar
            return "Não consegui projetar nenhuma economia com o que temos."

        total_eficiencia = sum(f['eficiencia'] for f in funcionarios_com_eficiencia) # Soma a eficiência de todo mundo
        media_eficiencia = total_eficiencia / len(funcionarios_com_eficiencia) # Calcula a eficiência média

        funcionarios_ordenados = sorted(funcionarios_com_eficiencia, key=lambda x: x["eficiencia"], reverse=True) # Organiza do menos eficiente para o mais eficiente
        top_ineficientes = funcionarios_ordenados[:num_otimizar] # Pega os funcionários que precisam melhorar mais

        economia_projetada = 0.0 # Começa a economia em zero
        detalhes_otimizacao = [] # Lista para explicar a economia de cada um
        
        if not top_ineficientes: # Se não achou ninguém para otimizar
            return "Não consegui achar funcionários para otimizar com esses critérios."
        
        for f_ineficiente in top_ineficientes: # Para cada funcionário que pode melhorar
            if f_ineficiente['eficiencia'] <= media_eficiencia: # Se ele já está bom ou melhor que a média
                detalhes_otimizacao.append(f"- {f_ineficiente['nome']} já é bom (custo de R$ {media_eficiencia:.2f} por ano). Não tem economia para ele neste caso.")
                continue # Pula para o próximo

            custo_alvo = media_eficiencia * f_ineficiente['experiencia'] # Quanto ele custaria se fosse eficiente como a média
            economia_individual = f_ineficiente['custo_atual'] - custo_alvo # Quanto a gente economizaria com ele

            if economia_individual > 0: # Se realmente dá para economizar
                economia_projetada += economia_individual # Soma na economia total
                detalhes_otimizacao.append( # Mostra os detalhes da economia com ele
                    f"- {f_ineficiente['nome']} (Área: {f_ineficiente['departamento']}): "
                    f"Custo agora R$ {f_ineficiente['custo_atual']:.2f}, "
                    f"Custo se for eficiente R$ {custo_alvo:.2f}, Economia R$ {economia_individual:.2f}"
                )
            else:
                detalhes_otimizacao.append(f"- {f_ineficiente['nome']} não gera economia neste cenário (já está bom ou não há diferença significativa).") # Não tem economia

        if economia_projetada == 0 and not detalhes_otimizacao: # Se não teve economia e nem detalhes para mostrar
            return "Não consegui projetar economia significativa neste cenário."
        elif economia_projetada == 0: # Se a economia é zero mas tem detalhes (ex: todos já eram eficientes)
            return "\n".join(detalhes_otimizacao)
        
        return f"Economia total que a gente pode ter: R$ {economia_projetada:.2f}\n\nDetalhes de quem pode melhorar:\n" + "\n".join(detalhes_otimizacao) # Mostra o resultado final

    def easter_egg(self, codigo):
        """Um segredo escondido! Digite 99 para ver."""
        if codigo == 99: # Se alguém digitou o código secreto
            mensagem_hex = "6f207365677265646f20657374c3a1206e6f732070657175656e6f7320646574616c6865732e2e2e" # A mensagem secreta em código
            return bytes.fromhex(mensagem_hex).decode() # Revela a mensagem secreta
        return "Esse código não serve para o segredo." # Se digitou errado

    def process_command(self, command):
        """Recebe o que você digitou e decide o que fazer."""
        if not self.data: # Se não tem dados carregados
            return "Ops! Não tem dados de funcionários. Não consigo fazer nada agora."

        command_lower = str(command).lower() # Deixa o que você digitou em letras minúsculas para comparar
        
        if command_lower in ["0", "sair"]: # Se você quer ir embora
            return "Já vai? Espero ter ajudado, até a próxima!"
        elif command_lower == "99": # Se você digitou o código secreto
            return self.easter_egg(99)
        elif command_lower in ["1", "custo total por departamento"]: # Se você pediu a opção 1
            return self.custo_por_departamento()
        elif command_lower in ["2", "custo medio por funcionario ativo"]: # Se você pediu a opção 2
            return self.custo_medio()
        elif command_lower in ["3", "departamento mais e menos custoso"]: # Se você pediu a opção 3
            return self.mais_menos_custoso()
        elif command_lower in ["4", "eficiencia por ano de experiencia"]: # Se você pediu a opção 4
            return self.eficiencia_por_experiencia()
        elif command_lower in ["5", "melhor custo-beneficio"]: # Se você pediu a opção 5
            return self.melhor_custo_beneficio()
        elif command_lower in ["6", "projecao de economia", "custos"]: # Se você pediu a opção 6
            return self.projetar_economia()
        else: # Se o que você digitou não é nenhuma opção
            return "Não entendi o que você pediu. Por favor, escolha um número de 0 a 6 ou o comando '99'."
