%%writefile analisador_csv.py
import csv  # Importa o módulo padrão para leitura e escrita de arquivos CSV
import urllib.request  # Importa o módulo para abrir URLs (usado para acessar Google Sheets)
import io  # Importa o módulo io para trabalhar com streams de I/O na memória (como um arquivo)

class CSVAnalyzer:
    """
    Classe para analisar dados de funcionários, focada em cálculos de custos
    e eficiência a partir de um CSV.
    """
    def __init__(self):
        self.data = []  # Armazenará os dados dos funcionários ativos e validados após o processamento
        self.headers = []  # Armazenará os cabeçalhos (nomes das colunas) do CSV
        self.raw_data = []  # Armazenará os dados brutos lidos do CSV antes de qualquer validação
        # A URL do seu Google Sheets está definida diretamente aqui:
        self.google_sheets_url = "https://docs.google.com/spreadsheets/d/1gIFTAgtLZIPCXqy5CaQxQ8s6MVFH2IGl-uG45N1MFJs/edit?usp=sharing"


    def load_from_sheets(self, url):
        """
        Carrega dados de uma URL de planilha do Google Sheets, convertendo-a
        para o formato de exportação CSV.
        """
        # Verifica se a URL é de uma planilha do Google Sheets
        if "docs.google.com/spreadsheets/d/" in url:
            sheet_id_part = url.split("d/")[1].split("/")[0] # Extrai o ID da planilha da URL
            gid_param = "" # Inicializa o parâmetro GID (ID da aba específica)
            if "#gid=" in url:
                gid_part = url.split("#gid=")[1].split("&")[0] # Extrai o GID se presente na URL
                gid_param = f"&gid={gid_part}" # Adiciona o GID como parâmetro
            
            # Constrói a URL de exportação CSV da planilha
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id_part}/export?format=csv{gid_param}"
        else:
            return False, "URL do Google Sheets inválida." # Retorna erro se a URL não for reconhecida

        try:
            with urllib.request.urlopen(csv_url) as response: # Abre a URL
                csv_content = response.read().decode('utf-8') # Lê o conteúdo e decodifica para UTF-8
                csv_file = io.StringIO(csv_content) # Cria um objeto de arquivo na memória a partir do conteúdo
                
                reader = csv.DictReader(csv_file) # Cria um leitor de CSV que trata cada linha como um dicionário
                self.headers = reader.fieldnames # Armazena os nomes das colunas (cabeçalhos)
                self.raw_data = [row for row in reader] # Lê todas as linhas e armazena como dados brutos
                return True, "Dados brutos carregados com sucesso." # Sucesso
        except urllib.error.URLError as e: # Captura erros de URL (ex: sem internet, URL errada)
            return False, f"Erro de conexão ao carregar dados da URL: {e}"
        except Exception as e: # Captura outros erros inesperados
            return False, f"Erro inesperado ao carregar dados: {e}"

    def validate_data(self):
        """
        Valida a estrutura dos dados carregados (raw_data).
        Verifica a presença de headers obrigatórios.
        Filtra funcionários 'Ativo', trata salários (vírgula para ponto) e
        garante que a experiência seja >= 0.
        Popula 'self.data' apenas com registros válidos.
        """
        required_headers = ["nome", "departamento", "salario", "experiencia_anos", "status_emprego"] # Cabeçalhos obrigatórios
        
        # Verifica se todos os cabeçalhos obrigatórios estão presentes
        if not self.headers or not all(header in self.headers for header in required_headers):
            return False, f"Headers obrigatórios faltando ou incorretos. Esperados: {required_headers}, Encontrados: {self.headers}"

        processed_funcionarios = [] # Lista para armazenar funcionários válidos e processados
        warnings = [] # Lista para armazenar avisos sobre dados inválidos
        for i, linha in enumerate(self.raw_data): # Itera sobre cada linha dos dados brutos
            status = linha.get("status_emprego", "").lower() # Pega o status do emprego e converte para minúsculas
            if status != "ativo": # Se o status não for 'ativo', pula para a próxima linha
                continue
            
            try:
                salario_str = linha.get("salario", "").replace(",", ".") # Pega o salário e substitui vírgula por ponto (para float)
                salario = float(salario_str) # Converte o salário para float
                experiencia_str = linha.get("experiencia_anos", "") # Pega a experiência
                experiencia = max(0, int(experiencia_str)) # Converte experiência para int e garante que seja no mínimo 0

                processed_funcionarios.append({ # Adiciona o funcionário processado à lista
                    "nome": linha.get("nome"),
                    "departamento": linha.get("departamento"),
                    "salario": salario,
                    "experiencia": experiencia
                })
            except (ValueError, KeyError) as e: # Captura erros se salário ou experiência não forem numéricos ou cabeçalho faltar
                warnings.append(f"Aviso: Linha {i+2} com dados inválidos/faltando (ignorada): {linha}. Erro: {e}") # Adiciona um aviso
                continue # Pula para a próxima linha
        
        self.data = processed_funcionarios # Armazena os funcionários validados
        if not self.data: # Se nenhuma funcionário válido foi encontrado
            return False, "Nenhum funcionário ativo e válido encontrado após a validação."
        return True, "\n".join(warnings) if warnings else "Dados validados e prontos para análise." # Retorna sucesso ou avisos

    # --- Funções de Cálculo e Análise Financeira (agora são métodos da classe) ---

    def _calcular_custo_total(self, salario):
        """Calcula o custo total de um funcionário (salário + encargos de 80%)."""
        return salario * 1.8 # Multiplica o salário por 1.8 para incluir 80% de encargos

    def _calcular_eficiencia(self, salario, experiencia):
        """Custo por ano de experiência: (Salário + encargos (80%)) / max(Experiência, 1)."""
        custo_total = self._calcular_custo_total(salario) # Calcula o custo total do funcionário
        return custo_total / max(experiencia, 1) # Divide o custo total pela experiência (mínimo 1 para evitar divisão por zero)

    def custo_por_departamento(self):
        """Calcula o custo total por departamento e alerta se um departamento tem <2 funcionários."""
        if not self.data: # Verifica se há dados de funcionários
            return "Nenhum funcionário ativo encontrado para calcular o custo por departamento."
        
        custos = {} # Dicionário para armazenar o custo total de cada departamento
        departamento_contagem = {} # Dicionário para contar o número de funcionários por departamento

        for f in self.data: # Itera sobre os funcionários validados
            dep = f["departamento"] # Pega o departamento do funcionário
            departamento_contagem[dep] = departamento_contagem.get(dep, 0) + 1 # Incrementa a contagem de funcionários para o departamento
            custo = self._calcular_custo_total(f["salario"]) # Calcula o custo total do funcionário
            custos[dep] = custos.get(dep, 0) + custo # Adiciona o custo ao total do departamento

        output = ["Custo total por departamento:"] # Lista para construir a saída
        for dep, count in departamento_contagem.items(): # Itera sobre a contagem de departamentos
            if count < 2: # Se um departamento tem menos de 2 funcionários
                output.append(f"Aviso: O departamento '{dep}' tem menos de 2 funcionários ativos.") # Adiciona um aviso
        
        if not custos: # Se nenhum custo foi calculado
            output.append("Nenhum custo calculado. Verifique os dados dos funcionários.")
        else:
            for dep, valor in custos.items(): # Itera sobre os custos por departamento
                output.append(f"{dep}: R$ {valor:.2f}") # Adiciona o custo formatado à saída
        return "\n".join(output) # Retorna a string com todos os resultados

    def custo_medio(self):
        """Calcula o custo médio por funcionário ativo."""
        if not self.data: # Verifica se há dados de funcionários
            return "Nenhum funcionário ativo encontrado para calcular o custo médio."
        total_custo = sum(self._calcular_custo_total(f["salario"]) for f in self.data) # Soma o custo total de todos os funcionários
        media = total_custo / len(self.data) # Calcula a média
        return f"Custo médio por funcionário ativo: R$ {media:.2f}" # Retorna a média formatada

    def mais_menos_custoso(self):
        """Identifica o departamento mais e menos custoso com base nos custos totais."""
        if not self.data: # Verifica se há dados de funcionários
            return "Nenhum funcionário ativo encontrado para identificar o departamento mais/menos custoso."
        
        custos = {} # Dicionário para armazenar o custo total de cada departamento
        for f in self.data: # Itera sobre os funcionários
            dep = f["departamento"] # Pega o departamento
            custo = self._calcular_custo_total(f["salario"]) # Calcula o custo do funcionário
            custos[dep] = custos.get(dep, 0) + custo # Acumula o custo por departamento

        if not custos: # Se não há custos por departamento
            return "Nenhum custo por departamento calculado. Não é possível identificar o mais/menos custoso."
        
        mais = max(custos, key=custos.get) # Encontra o departamento com o maior custo
        menos = min(custos, key=custos.get) # Encontra o departamento com o menor custo
        return f"Departamento mais custoso: {mais}\nDepartamento menos custoso: {menos}" # Retorna os resultados

    def eficiencia_por_experiencia(self):
        """Calcula a eficiência por ano de experiência para cada funcionário."""
        if not self.data: # Verifica se há dados de funcionários
            return "Nenhum funcionário ativo encontrado para calcular a eficiência por experiência."
        
        output = ["Eficiência por ano de experiência (Custo / Ano de Experiência):"] # Lista para construir a saída
        eficiencias = [] # Lista para armazenar a eficiência de cada funcionário
        for f in self.data: # Itera sobre os funcionários
            if f['experiencia'] == 0 and f['salario'] == 0: # Evita divisão por zero se ambos forem zero
                continue
            eficiencia = self._calcular_eficiencia(f["salario"], f["experiencia"]) # Calcula a eficiência
            eficiencias.append({"nome": f["nome"], "departamento": f["departamento"], "eficiencia": eficiencia}) # Adiciona à lista

        eficiencias_ordenadas = sorted(eficiencias, key=lambda x: x["eficiencia"]) # Ordena por eficiência (menor é melhor)

        if not eficiencias_ordenadas: # Se não há dados válidos para eficiência
            output.append("Não há dados válidos para calcular a eficiência.")
        else:
            for item in eficiencias_ordenadas: # Itera sobre os itens ordenados
                output.append(f"- {item['nome']} ({item['departamento']}): R$ {item['eficiencia']:.2f} por ano de experiência") # Adiciona formatado
        return "\n".join(output) # Retorna a string com todos os resultados

    def melhor_custo_beneficio(self):
        """
        Identifica o(s) funcionário(s) com o menor custo por ano de experiência.
        Retorna uma lista de funcionários, pois pode haver empates.
        """
        if not self.data: # Verifica se há dados de funcionários
            return "Nenhum funcionário ativo encontrado para identificar o melhor custo-benefício."

        melhor_eficiencia = float('inf') # Inicializa com um valor muito alto para encontrar o menor
        funcionarios_melhor_custo_beneficio = [] # Lista para armazenar os funcionários com melhor custo-benefício

        for f in self.data: # Itera sobre os funcionários
            if f['experiencia'] == 0 and f['salario'] == 0: # Evita cálculo se ambos são zero
                continue
            
            eficiencia_atual = self._calcular_eficiencia(f["salario"], f["experiencia"]) # Calcula a eficiência atual
            if eficiencia_atual < melhor_eficiencia: # Se encontrou uma eficiência melhor
                melhor_eficiencia = eficiencia_atual # Atualiza a melhor eficiência
                funcionarios_melhor_custo_beneficio = [f] # Começa uma nova lista (pois é a nova melhor)
            elif eficiencia_atual == melhor_eficiencia: # Se encontrou uma eficiência igual à melhor
                funcionarios_melhor_custo_beneficio.append(f) # Adiciona à lista (é um empate)
        
        if not funcionarios_melhor_custo_beneficio: # Se não encontrou funcionários com custo-benefício
            return "Não foi possível identificar funcionários com melhor custo-benefício. Verifique se há dados de salário e experiência válidos."
        else:
            output = [f"Funcionário(s) com o MELHOR Custo-Benefício (Custo de R$ {melhor_eficiencia:.2f} por ano de experiência):"] # Título da saída
            for f in funcionarios_melhor_custo_beneficio: # Itera sobre os funcionários com melhor custo-benefício
                output.append(f"- {f['nome']} (Departamento: {f['departamento']})") # Adiciona formatado
            return "\n".join(output) # Retorna a string

    def projetar_economia(self, num_otimizar=3):
        """
        Projeta a economia potencial se os 'num_otimizar' funcionários menos eficientes
        tivessem sua eficiência reduzida para a média.
        """
        if not self.data: # Verifica se há dados de funcionários
            return "Nenhum funcionário ativo para projetar economia."

        funcionarios_com_eficiencia = [] # Lista para armazenar funcionários com seus dados de eficiência
        for f in self.data: # Itera sobre os funcionários
            if f['experiencia'] == 0 and f['salario'] == 0: # Evita cálculo se ambos são zero
                continue
            eficiencia = self._calcular_eficiencia(f["salario"], f["experiencia"]) # Calcula a eficiência
            funcionarios_com_eficiencia.append({ # Adiciona todos os dados e a eficiência calculada
                "nome": f["nome"],
                "departamento": f["departamento"],
                "salario": f["salario"],
                "experiencia": f["experiencia"],
                "eficiencia": eficiencia,
                "custo_atual": self._calcular_custo_total(f["salario"])
            })
        
        if not funcionarios_com_eficiencia: # Se não há funcionários com dados válidos de eficiência
            return "Não foi possível projetar economia significativa com este cenário de otimização."

        total_eficiencia = sum(f['eficiencia'] for f in funcionarios_com_eficiencia) # Soma todas as eficiências
        media_eficiencia = total_eficiencia / len(funcionarios_com_eficiencia) # Calcula a média da eficiência

        # Ordena os funcionários pela eficiência (do menos eficiente ao mais eficiente)
        funcionarios_ordenados = sorted(funcionarios_com_eficiencia, key=lambda x: x["eficiencia"], reverse=True)
        top_ineficientes = funcionarios_ordenados[:num_otimizar] # Pega os 'num_otimizar' funcionários menos eficientes

        economia_projetada = 0.0 # Inicializa a economia total projetada
        detalhes_otimizacao = [] # Lista para armazenar os detalhes da otimização

        if not top_ineficientes: # Se não há funcionários para otimizar (ex: num_otimizar maior que o total de funcionários)
             return "Não foi possível identificar funcionários para otimização com os critérios atuais."
        
        for f_ineficiente in top_ineficientes: # Itera sobre os funcionários menos eficientes
            if f_ineficiente['eficiencia'] <= media_eficiencia: # Se a eficiência já é melhor ou igual à média
                detalhes_otimizacao.append(f"- {f_ineficiente['nome']} já é mais eficiente que a média ({media_eficiencia:.2f} R$/ano), sem economia projetada neste cenário.")
                continue # Pula para o próximo

            custo_alvo = media_eficiencia * f_ineficiente['experiencia'] # Calcula o custo que o funcionário teria se atingisse a eficiência média
            economia_individual = f_ineficiente['custo_atual'] - custo_alvo # Calcula a economia individual
            
            if economia_individual > 0: # Se há uma economia real (valor positivo)
                economia_projetada += economia_individual # Soma à economia total
                detalhes_otimizacao.append( # Adiciona os detalhes da economia individual
                    f"- {f_ineficiente['nome']} (Dep: {f_ineficiente['departamento']}): "
                    f"Custo atual R$ {f_ineficiente['custo_atual']:.2f}, "
                    f"Custo alvo R$ {custo_alvo:.2f}, Economia R$ {economia_individual:.2f}"
                )
            else:
                 detalhes_otimizacao.append(f"- {f_ineficiente['nome']} não gera economia neste cenário (custo alvo maior ou igual ao atual).") # Não há economia

        if economia_projetada == 0 and not detalhes_otimizacao: # Se não houve economia e nenhum detalhe de otimização
             return "Não foi possível projetar economia significativa com este cenário de otimização."
        elif economia_projetada == 0: # Se a economia é zero mas há detalhes (ex: todos já eficientes)
            return "\n".join(detalhes_otimizacao)
        
        return f"Economia total projetada: R$ {economia_projetada:.2f}\n\nDetalhes da Otimização:\n" + "\n".join(detalhes_otimizacao) # Retorna o resultado final

    def easter_egg(self, codigo):
        """Ativa um recurso escondido ao digitar 99, imprimindo uma mensagem específica."""
        if codigo == 99: # Verifica se o código é 99
            mensagem_hex = "6f207365677265646f20657374c3a1206e6f732070657175656e6f7320646574616c6865732e2e2e" # Mensagem em hexadecimal
            return bytes.fromhex(mensagem_hex).decode() # Decodifica e retorna a mensagem
        return "Código inválido para o easter egg." # Mensagem para código inválido

    def process_command(self, command):
        """
        Processa comandos específicos (números ou palavras-chave) e retorna uma resposta.
        Esta é a interface principal para o chatbot.
        """
        # Primeiro, tentar carregar e validar os dados de forma automática
        load_success, load_message = self.load_from_sheets(self.google_sheets_url) # Tenta carregar os dados da URL
        if not load_success: # Se o carregamento falhou
            # Se não conseguir carregar da URL, tenta carregar do arquivo local 'desafio.csv' como fallback
            try:
                # O arquivo 'desafio.csv' foi fornecido como input, então o conteúdo completo está disponível
                csv_content = """nome,idade,cidade,profissao,salario,experiencia_anos,nivel_educacao,status_emprego,data_contratacao,departamento
João Silva,28,São Paulo,Desenvolvedor,5500,3,Superior,Ativo,2021-03-15,TI
Maria Santos,32,Rio de Janeiro,Designer,4200,5,Superior,Ativo,2020-07-22,Marketing
Carlos Oliveira,45,Belo Horizonte,Gerente,8500,12,Pós-graduação,Ativo,2018-11-10,Vendas
Ana Costa,29,Porto Alegre,Analista,3800,2,Superior,Inativo,2022-01-08,Financeiro
Pedro Lima,35,Fortaleza,Desenvolvedor,7200,8,Superior,Ativo,2019-05-18,TI"""
                csv_file = io.StringIO(csv_content)
                reader = csv.DictReader(csv_file)
                self.headers = reader.fieldnames
                self.raw_data = [row for row in reader]
                load_success = True
                load_message = "Dados carregados do conteúdo fornecido para 'desafio.csv' (URL falhou ou não fornecida)."
            except Exception as e:
                return f"Erro ao carregar dados: {load_message}. Erro ao ler 'desafio.csv' a partir do conteúdo fornecido: {e}"

        validate_success, validate_message = self.validate_data() # Tenta validar os dados carregados
        # Se a validação falhou, mesmo após o fallback, retorna o erro
        if not validate_success:
            return f"Erro ao validar dados: {validate_message}"
        
        # Se os dados foram carregados e validados com sucesso, processa o comando do usuário
        response = "" # Inicializa a variável de resposta
        command_lower = str(command).lower() # Garante que o comando seja uma string e em minúsculas para comparação

        if command_lower in ["0", "sair"]: # Verifica se o comando é para sair
            response = "Já vai? Espero ter ajudado, até a próxima!" # Frase atualizada
        elif command_lower == "99": # Verifica se o comando é o easter egg
            response = self.easter_egg(99)
        elif command_lower in ["1", "custo total por departamento"]: # Verifica o comando para custo por departamento
            response = self.custo_por_departamento()
        elif command_lower in ["2", "custo medio por funcionario ativo"]: # Verifica o comando para custo médio
            response = self.custo_medio()
        elif command_lower in ["3", "departamento mais e menos custoso"]: # Verifica o comando para mais/menos custoso
            response = self.mais_menos_custoso()
        elif command_lower in ["4", "eficiencia por ano de experiencia"]: # Verifica o comando para eficiência por experiência
            response = self.eficiencia_por_experiencia()
        elif command_lower in ["5", "melhor custo-beneficio"]: # Verifica o comando para melhor custo-benefício
            response = self.melhor_custo_beneficio()
        elif command_lower in ["6", "projecao de economia", "custos"]: # Verifica o comando para projeção de economia (ou "custos")
            response = self.projetar_economia()
        else: # Se o comando não for reconhecido
            response = "Opção inválida ou comando não reconhecido. Por favor, escolha uma opção válida do menu (0-6) ou o comando '99'."
        
        return response # Retorna a resposta gerada
