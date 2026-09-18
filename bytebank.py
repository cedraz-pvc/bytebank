"""
ByteBank - Nível 2 (Intermediário)
CESAR School | BD015 - Algoritmos e Estruturas de Dados

Funcionalidades:
    Nível 1 (MVP)
        - Autenticação por senha (máximo de 3 tentativas)
        - Consulta de saldo, Depósito e Saque
        - Validações de segurança em todas as entradas do usuário

    Nível 2 (Intermediário)
        - Gerenciamento de várias contas em uma MATRIZ em memória
        - Abertura de novas contas
        - Transferência PIX com verificação da chave de destino
        - Cofrinhos (caixinhas de investimento) em DICIONÁRIO ANINHADO
        - Simulação de rendimento por juros simples
        - Categorização obrigatória dos gastos e relatório por categoria
        - Cartão de crédito: limite, fatura e lista de compras
        - Carteira multimoedas com compra e venda por taxas fixas
        - BytePoints: acúmulo de pontos por gasto e resgate em cashback
        - Empréstimo pré-aprovado com parcelamento em lista

Estruturas de dados usadas:
    MATRIZ (lista de listas) -> cada linha é uma conta, cada coluna um dado:
        [numero, nome, chave_pix, senha, saldo, cofrinhos]
    DICIONÁRIO ANINHADO -> uma das colunas guarda os cofrinhos da conta:
        {"Viagem": 500.0, "Reserva": 1200.0}
    LISTA DE DICIONÁRIOS -> o histórico de movimentações da conta
    AGREGAÇÃO COM DICIONÁRIO -> soma dos gastos por categoria (GROUP BY em memória)
    LISTA DE TRANSAÇÕES -> compras feitas no cartão de crédito
    DICIONÁRIO DE TAXAS -> cotação de cada moeda estrangeira
    LISTA DE PARCELAS -> dívida do empréstimo dividida em parcelas
"""

import math

# ------------------------------------------------------------------
# CONFIGURAÇÕES DO SISTEMA
# ------------------------------------------------------------------
MAX_TENTATIVAS = 3              # Tentativas de senha antes do bloqueio
LIMITE_POR_OPERACAO = 10000.00  # Valor máximo por operação
TAMANHO_SENHA = 4               # Quantidade de dígitos da senha
TAXA_RENDIMENTO_MENSAL = 0.005  # 0,5% ao mês (juros simples nos cofrinhos)
MAX_MESES_SIMULACAO = 120       # Limite de meses na simulação de rendimento
ORCAMENTO_PADRAO = 3000.00      # Orçamento mensal de gastos usado no relatório
LIMITE_CREDITO_PADRAO = 1500.00 # Limite de crédito aprovado ao abrir a conta

# Cotações fixas usadas no câmbio: quantos reais vale 1 unidade da moeda
TAXAS = {"USD": 5.50, "EUR": 6.00, "BTC": 350000.00}

# Casas decimais de cada moeda (cripto exige mais precisão que moeda fiduciária)
CASAS_DECIMAIS = {"USD": 2, "EUR": 2, "BTC": 8}

# Programa de fidelidade BytePoints
GASTO_POR_PONTO = 10.00         # A cada R$ 10,00 gastos, 1 ponto
PONTOS_POR_RESGATE = 100        # Resgate mínimo (e múltiplo) de pontos
VALOR_POR_RESGATE = 5.00        # 100 pontos = R$ 5,00 de cashback

# Empréstimo pré-aprovado
MULTIPLICADOR_LIMITE = 3        # Limite pré-aprovado: até 3x o saldo atual
TAXA_JUROS_EMPRESTIMO = 0.02    # 2% ao mês, juros simples
MAX_PARCELAS = 24               # Número máximo de parcelas

# Categorias disponíveis para classificar cada gasto
CATEGORIAS = ["Alimentação", "Transporte", "Lazer", "Contas", "Outros"]

# ------------------------------------------------------------------
# COLUNAS DA MATRIZ DE CONTAS
# Usar constantes deixa o código legível: conta[COL_SALDO] em vez de conta[4]
# ------------------------------------------------------------------
COL_NUMERO = 0
COL_NOME = 1
COL_CHAVE = 2
COL_SENHA = 3
COL_SALDO = 4
COL_COFRINHOS = 5
COL_HISTORICO = 6
COL_ORCAMENTO = 7
COL_LIMITE = 8
COL_FATURA = 9
COL_COMPRAS = 10
COL_MOEDAS = 11
COL_PONTOS = 12
COL_EMPRESTIMO = 13


def criar_contas_iniciais():
    """
    Monta a matriz de contas do banco (lista de listas).
    Os dados abaixo já vêm cadastrados para facilitar os testes.
    """
    return [
        ["0001", "Patricia Cedraz", "patricia@bytebank.com", "1234", 2500.00,
         {"Viagem": 500.00, "Reserva": 1200.00},
         [  # histórico já com alguns lançamentos, para o relatório ter conteúdo
             {"tipo": "Saque", "natureza": "saida",
              "categoria": "Alimentação", "valor": 320.00},
             {"tipo": "PIX enviado", "natureza": "saida",
              "categoria": "Transporte", "valor": 180.00},
             {"tipo": "Saque", "natureza": "saida",
              "categoria": "Lazer", "valor": 150.00},
             {"tipo": "PIX enviado", "natureza": "saida",
              "categoria": "Contas", "valor": 430.00},
             {"tipo": "Compra crédito", "natureza": "saida",
              "categoria": "Alimentação", "valor": 240.00},
         ],
         ORCAMENTO_PADRAO, LIMITE_CREDITO_PADRAO, 240.00,
         [{"estabelecimento": "Supermercado Bom Preco",
           "categoria": "Alimentação", "valor": 240.00}],
         {"USD": 100.00, "EUR": 0.0, "BTC": 0.0}, 120, {}],
        ["0002", "Vitor Argay", "vitor@bytebank.com", "4321", 1800.00,
         {}, [], ORCAMENTO_PADRAO, LIMITE_CREDITO_PADRAO, 0.0, [],
         {"USD": 0.0, "EUR": 0.0, "BTC": 0.0}, 0, {}],
        ["0003", "Maria Souza", "81999990000", "9999", 350.00,
         {"Bicicleta": 120.00}, [], ORCAMENTO_PADRAO,
         LIMITE_CREDITO_PADRAO, 0.0, [],
         {"USD": 0.0, "EUR": 0.0, "BTC": 0.0}, 0, {}],
    ]


# ------------------------------------------------------------------
# FUNÇÕES UTILITÁRIAS
# ------------------------------------------------------------------
def formatar_moeda(valor):
    """Formata um número no padrão brasileiro. Ex: 1234.5 -> 'R$ 1.234,50'."""
    texto = f"{valor:,.2f}"  # formato americano: 1,234.50
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def ler_valor(mensagem):
    """
    Lê um valor monetário digitado pelo usuário e aplica as validações.
    Retorna o valor (float) se for válido, ou None se for inválido.
    Aceita vírgula ou ponto como separador decimal (ex: 150,75 ou 150.75).
    """
    entrada = input(mensagem).strip().replace(",", ".")

    # Validação 1: precisa ser um número
    try:
        valor = float(entrada)
    except ValueError:
        print("[ERRO] Valor inválido. Digite apenas números (ex: 150,00).")
        return None

    # Validação 2: bloqueia 'nan' e 'inf', que o float() aceita
    if not math.isfinite(valor):
        print("[ERRO] Valor inválido. Digite apenas números (ex: 150,00).")
        return None

    # Validação 3: não aceita zero nem valores negativos
    if valor <= 0:
        print("[ERRO] O valor deve ser maior que zero.")
        return None

    # Validação 4: no máximo 2 casas decimais (centavos)
    if round(valor, 2) != valor:
        print("[ERRO] Use no máximo 2 casas decimais (centavos).")
        return None

    # Validação 5: respeita o limite por operação
    if valor > LIMITE_POR_OPERACAO:
        print(f"[ERRO] O limite por operação é {formatar_moeda(LIMITE_POR_OPERACAO)}.")
        return None

    return valor


def ler_texto(mensagem, tamanho_maximo=40):
    """
    Lê um texto digitado pelo usuário (nome, chave PIX, nome de cofrinho).
    Retorna o texto se for válido, ou None se estiver vazio ou longo demais.
    """
    texto = input(mensagem).strip()

    if texto == "":
        print("[ERRO] O campo não pode ficar em branco.")
        return None

    if len(texto) > tamanho_maximo:
        print(f"[ERRO] Use no máximo {tamanho_maximo} caracteres.")
        return None

    return texto


def ler_meses(mensagem):
    """Lê a quantidade de meses da simulação. Retorna int ou None."""
    entrada = input(mensagem).strip()

    if not entrada.isdigit():
        print("[ERRO] Digite um número inteiro de meses (ex: 12).")
        return None

    meses = int(entrada)
    if meses < 1 or meses > MAX_MESES_SIMULACAO:
        print(f"[ERRO] Informe de 1 até {MAX_MESES_SIMULACAO} meses.")
        return None

    return meses


# ------------------------------------------------------------------
# BUSCA NA MATRIZ (percorre linha por linha)
# ------------------------------------------------------------------
def buscar_indice_por_chave(contas, chave):
    """
    Procura a conta pela chave PIX. Retorna o índice da linha na matriz
    ou -1 se a chave não existir no banco.
    """
    for i in range(len(contas)):
        if contas[i][COL_CHAVE].lower() == chave.lower():
            return i
    return -1


def buscar_indice_por_numero(contas, numero):
    """
    Procura a conta pelo número. Retorna o índice da linha na matriz
    ou -1 se o número não existir.
    """
    for i in range(len(contas)):
        if contas[i][COL_NUMERO] == numero:
            return i
    return -1


def listar_contas(contas):
    """Mostra as contas do banco sem expor saldo nem senha."""
    print("\n--- Contas cadastradas no ByteBank ---")
    print(f"{'Conta':<8}{'Titular':<20}{'Chave PIX'}")
    for conta in contas:
        print(f"{conta[COL_NUMERO]:<8}{conta[COL_NOME]:<20}{conta[COL_CHAVE]}")
    print()


# ------------------------------------------------------------------
# SEGURANÇA E CADASTRO
# ------------------------------------------------------------------
def autenticar(contas):
    """
    Pede número de conta e senha. Retorna o índice da conta na matriz
    se o login der certo, ou -1 se a conta for bloqueada.
    """
    numero = input("Número da conta (ex: 0001): ").strip()
    tentativas = 0

    while tentativas < MAX_TENTATIVAS:
        senha = input("Digite sua senha: ").strip()
        indice = buscar_indice_por_numero(contas, numero)

        # A mesma mensagem serve para conta inexistente e senha errada,
        # para não revelar quais contas existem no banco.
        if indice != -1 and contas[indice][COL_SENHA] == senha:
            print(f"\n[OK] Acesso liberado! Bem-vindo(a), {contas[indice][COL_NOME]}.\n")
            return indice

        tentativas += 1
        restantes = MAX_TENTATIVAS - tentativas
        if restantes > 0:
            print(f"[ERRO] Conta ou senha incorreta. Tentativas restantes: {restantes}")

    print("[BLOQUEADO] Acesso bloqueado por excesso de tentativas.\n")
    return -1


def gerar_numero_conta(contas):
    """Gera o próximo número de conta com 4 dígitos. Ex: 0004."""
    return f"{len(contas) + 1:04d}"


def abrir_conta(contas):
    """Cadastra uma nova linha na matriz de contas."""
    print("\n--- Abertura de conta ---")

    nome = ler_texto("Nome do titular: ")
    if nome is None:
        return

    chave = ler_texto("Chave PIX (e-mail ou telefone): ")
    if chave is None:
        return

    # Validação de segurança: a chave PIX não pode se repetir no banco
    if buscar_indice_por_chave(contas, chave) != -1:
        print("[ERRO] Esta chave PIX já está cadastrada em outra conta.\n")
        return

    senha = input(f"Crie uma senha de {TAMANHO_SENHA} dígitos: ").strip()
    if len(senha) != TAMANHO_SENHA or not senha.isdigit():
        print(f"[ERRO] A senha deve ter exatamente {TAMANHO_SENHA} dígitos numéricos.\n")
        return

    numero = gerar_numero_conta(contas)
    contas.append([numero, nome, chave, senha, 0.0, {}, [], ORCAMENTO_PADRAO,
                   LIMITE_CREDITO_PADRAO, 0.0, [],
                   {"USD": 0.0, "EUR": 0.0, "BTC": 0.0}, 0, {}])

    print(f"[OK] Conta {numero} criada para {nome}.")
    print("Saldo inicial: R$ 0,00. Já pode entrar com o número e a senha.\n")


# ------------------------------------------------------------------
# OPERAÇÕES BANCÁRIAS (NÍVEL 1)
# ------------------------------------------------------------------
def depositar(saldo, valor):
    """Soma o valor ao saldo e retorna o novo saldo."""
    return round(saldo + valor, 2)


def sacar(saldo, valor):
    """
    Tenta subtrair o valor do saldo.
    Retorna uma tupla (novo_saldo, sucesso).
    Se não houver saldo suficiente, o saldo não muda e sucesso = False.
    """
    if valor > saldo:
        print(f"[ERRO] Saldo insuficiente. Saldo disponível: {formatar_moeda(saldo)}")
        return saldo, False

    return round(saldo - valor, 2), True



# ------------------------------------------------------------------
# CATEGORIZAÇÃO DE GASTOS E HISTÓRICO (NÍVEL 2)
# Cada movimentação vira um dicionário dentro da lista de histórico
# ------------------------------------------------------------------
def escolher_categoria():
    """
    Mostra as categorias e pede que o usuário escolha uma.
    Retorna o nome da categoria ou None se a escolha for inválida.
    """
    print("\nCategorias disponíveis:")
    for i in range(len(CATEGORIAS)):
        print(f"[{i + 1}] {CATEGORIAS[i]}")

    escolha = input("Categoria do gasto: ").strip()

    if not escolha.isdigit():
        print("[ERRO] Digite o número da categoria.")
        return None

    numero = int(escolha)
    if numero < 1 or numero > len(CATEGORIAS):
        print(f"[ERRO] Escolha de 1 a {len(CATEGORIAS)}.")
        return None

    return CATEGORIAS[numero - 1]


def formatar_percentual(valor):
    """Formata percentual no padrão brasileiro. Ex: 36.4 -> '36,4%'."""
    return f"{valor:.1f}".replace(".", ",") + "%"


def registrar_movimento(conta, tipo, natureza, categoria, valor):
    """
    Guarda a movimentação no histórico da conta.
    natureza: 'saida' (gasto), 'entrada' (recebimento) ou 'interna' (cofrinho).
    Apenas as saídas entram no relatório de gastos.
    """
    conta[COL_HISTORICO].append({
        "tipo": tipo,
        "natureza": natureza,
        "categoria": categoria,
        "valor": valor,
    })


def exibir_extrato(conta):
    """Lista todas as movimentações da conta, da mais antiga para a mais nova."""
    historico = conta[COL_HISTORICO]

    if len(historico) == 0:
        print("\nNenhuma movimentação registrada ainda.\n")
        return

    print("\n--- Extrato da conta ---")
    print(f"{'#':<4}{'Movimentação':<18}{'Categoria':<16}{'Valor':>14}")

    for i in range(len(historico)):
        movimento = historico[i]
        if movimento["natureza"] == "saida":
            sinal = "-"
        elif movimento["natureza"] == "entrada":
            sinal = "+"
        else:
            sinal = "~"  # movimento interno (cofrinho)
        print(f"{i + 1:<4}{movimento['tipo']:<18}{movimento['categoria']:<16}"
              f"{sinal + formatar_moeda(movimento['valor']):>14}")
    print()


def relatorio_categoria(conta):
    """
    Percorre o histórico, soma os gastos por categoria (GROUP BY em memória)
    e mostra o percentual de cada categoria e do orçamento consumido.
    """
    historico = conta[COL_HISTORICO]
    orcamento = conta[COL_ORCAMENTO]

    # AGREGAÇÃO: o dicionário acumula o total de cada categoria
    gastos_por_categoria = {}
    total_gasto = 0.0

    for movimento in historico:
        if movimento["natureza"] == "saida":
            categoria = movimento["categoria"]
            if categoria not in gastos_por_categoria:
                gastos_por_categoria[categoria] = 0.0
            gastos_por_categoria[categoria] += movimento["valor"]
            total_gasto += movimento["valor"]

    if total_gasto == 0:
        print("\nVocê ainda não tem gastos registrados para analisar.\n")
        return

    total_gasto = round(total_gasto, 2)

    # Ordena da maior para a menor despesa
    categorias_ordenadas = sorted(gastos_por_categoria.items(),
                                  key=lambda item: item[1], reverse=True)

    print("\n--- Relatório de gastos por categoria ---")
    print(f"Orçamento mensal: {formatar_moeda(orcamento)}")
    print(f"{'Categoria':<16}{'Valor':>13}{'% gastos':>11}{'% orçam.':>11}  Consumo")

    for categoria, valor in categorias_ordenadas:
        valor = round(valor, 2)
        percentual_gastos = valor / total_gasto * 100
        percentual_orcamento = valor / orcamento * 100 if orcamento > 0 else 0.0
        barra = "#" * int(percentual_gastos / 5)  # cada # vale 5%
        print(f"{categoria:<16}{formatar_moeda(valor):>13}"
              f"{formatar_percentual(percentual_gastos):>11}"
              f"{formatar_percentual(percentual_orcamento):>11}  {barra}")

    percentual_total = total_gasto / orcamento * 100 if orcamento > 0 else 0.0
    print(f"{'TOTAL':<16}{formatar_moeda(total_gasto):>13}"
          f"{formatar_percentual(100.0):>11}"
          f"{formatar_percentual(percentual_total):>11}")

    # Alerta de controle orçamentário
    if orcamento > 0:
        saldo_orcamento = round(orcamento - total_gasto, 2)
        if saldo_orcamento < 0:
            print(f"[ALERTA] Orçamento estourado em {formatar_moeda(-saldo_orcamento)}.")
        else:
            print(f"Ainda cabem {formatar_moeda(saldo_orcamento)} no orçamento do mês.")
    print()


def definir_orcamento(conta):
    """Permite ao usuário alterar o orçamento mensal usado no relatório."""
    print(f"\nOrçamento atual: {formatar_moeda(conta[COL_ORCAMENTO])}")
    valor = ler_valor("Novo orçamento mensal: R$ ")
    if valor is not None:
        conta[COL_ORCAMENTO] = valor
        print(f"[OK] Orçamento definido em {formatar_moeda(valor)}.\n")


# ------------------------------------------------------------------
# TRANSFERÊNCIA PIX (NÍVEL 2)
# ------------------------------------------------------------------
def transferir_pix(contas, indice_origem, chave_destino, valor, categoria):
    """
    Transfere um valor da conta de origem para a conta da chave informada.
    Reaproveita sacar() e depositar() do Nível 1 e registra a movimentação
    no histórico das duas contas.
    Retorna True se a transferência acontecer, False caso contrário.
    """
    indice_destino = buscar_indice_por_chave(contas, chave_destino)

    # Verificação da chave de destino
    if indice_destino == -1:
        print("[ERRO] Chave PIX não encontrada. Confira a chave e tente de novo.")
        return False

    if indice_destino == indice_origem:
        print("[ERRO] Não é possível transferir para a própria conta.")
        return False

    # Debita da origem (só acontece se houver saldo suficiente)
    novo_saldo, sucesso = sacar(contas[indice_origem][COL_SALDO], valor)
    if not sucesso:
        return False

    contas[indice_origem][COL_SALDO] = novo_saldo

    # Credita no destino
    contas[indice_destino][COL_SALDO] = depositar(
        contas[indice_destino][COL_SALDO], valor
    )

    # Registra o gasto na origem e o recebimento no destino
    registrar_movimento(contas[indice_origem], "PIX enviado", "saida",
                        categoria, valor)
    registrar_movimento(contas[indice_destino], "PIX recebido", "entrada",
                        "Entrada", valor)

    print(f"[OK] PIX de {formatar_moeda(valor)} enviado para "
          f"{contas[indice_destino][COL_NOME]}.")
    print(f"Novo saldo: {formatar_moeda(contas[indice_origem][COL_SALDO])}")
    creditar_pontos(contas[indice_origem], valor)
    print()
    return True


def operacao_pix(contas, indice):
    """Pede os dados do PIX ao usuário e chama a transferência."""
    print("\n--- Transferência PIX ---")

    chave = ler_texto("Chave PIX de destino: ")
    if chave is None:
        return

    valor = ler_valor("Valor do PIX: R$ ")
    if valor is None:
        return

    # Categoria obrigatória: todo gasto precisa ser classificado
    categoria = escolher_categoria()
    if categoria is None:
        return

    transferir_pix(contas, indice, chave, valor, categoria)


# ------------------------------------------------------------------
# COFRINHOS / CAIXINHAS DE INVESTIMENTO (NÍVEL 2)
# Cada conta guarda seus cofrinhos em um dicionário aninhado
# ------------------------------------------------------------------
def total_nos_cofrinhos(cofrinhos):
    """Soma o valor guardado em todas as caixinhas."""
    total = 0.0
    for valor in cofrinhos.values():
        total += valor
    return round(total, 2)


def saldo_total(conta):
    """Saldo principal somado ao que está guardado nos cofrinhos."""
    return round(conta[COL_SALDO] + total_nos_cofrinhos(conta[COL_COFRINHOS]), 2)


def exibir_cofrinhos(cofrinhos):
    """Lista as caixinhas e o total guardado."""
    if len(cofrinhos) == 0:
        print("\nVocê ainda não tem cofrinhos. Crie o primeiro no menu!\n")
        return

    print("\n--- Seus cofrinhos ---")
    for nome in cofrinhos:
        print(f"{nome:<20}{formatar_moeda(cofrinhos[nome])}")
    print(f"{'TOTAL GUARDADO':<20}{formatar_moeda(total_nos_cofrinhos(cofrinhos))}\n")


def criar_cofrinho(cofrinhos, nome):
    """Cria uma caixinha nova com saldo zero. Retorna True se criar."""
    if nome in cofrinhos:
        print("[ERRO] Você já tem um cofrinho com esse nome.")
        return False

    cofrinhos[nome] = 0.0
    print(f"[OK] Cofrinho '{nome}' criado com R$ 0,00.")
    return True


def guardar_no_cofrinho(conta, nome_caixinha, valor):
    """
    Move dinheiro do saldo principal para a caixinha.
    Retorna True se der certo.
    """
    cofrinhos = conta[COL_COFRINHOS]

    if nome_caixinha not in cofrinhos:
        print("[ERRO] Cofrinho não encontrado.")
        return False

    novo_saldo, sucesso = sacar(conta[COL_SALDO], valor)
    if not sucesso:
        return False

    conta[COL_SALDO] = novo_saldo
    cofrinhos[nome_caixinha] = round(cofrinhos[nome_caixinha] + valor, 2)

    registrar_movimento(conta, "Guardar cofrinho", "interna",
                        nome_caixinha, valor)

    print(f"[OK] {formatar_moeda(valor)} guardados em '{nome_caixinha}'.")
    print(f"Cofrinho: {formatar_moeda(cofrinhos[nome_caixinha])} | "
          f"Saldo em conta: {formatar_moeda(conta[COL_SALDO])}\n")
    return True


def resgatar_do_cofrinho(conta, nome_caixinha, valor):
    """
    Move dinheiro da caixinha de volta para o saldo principal.
    Retorna True se der certo.
    """
    cofrinhos = conta[COL_COFRINHOS]

    if nome_caixinha not in cofrinhos:
        print("[ERRO] Cofrinho não encontrado.")
        return False

    if valor > cofrinhos[nome_caixinha]:
        print(f"[ERRO] O cofrinho '{nome_caixinha}' tem apenas "
              f"{formatar_moeda(cofrinhos[nome_caixinha])}.")
        return False

    cofrinhos[nome_caixinha] = round(cofrinhos[nome_caixinha] - valor, 2)
    conta[COL_SALDO] = depositar(conta[COL_SALDO], valor)

    registrar_movimento(conta, "Resgate cofrinho", "interna",
                        nome_caixinha, valor)

    print(f"[OK] {formatar_moeda(valor)} resgatados de '{nome_caixinha}'.")
    print(f"Cofrinho: {formatar_moeda(cofrinhos[nome_caixinha])} | "
          f"Saldo em conta: {formatar_moeda(conta[COL_SALDO])}\n")
    return True


def simular_rendimento(cofrinhos, meses, taxa=TAXA_RENDIMENTO_MENSAL):
    """
    Simula o rendimento das caixinhas por juros SIMPLES:
        juros = valor guardado x taxa x meses
    A simulação não altera os saldos: é apenas uma projeção.
    """
    if len(cofrinhos) == 0:
        print("\nVocê ainda não tem cofrinhos para simular.\n")
        return

    taxa_texto = f"{taxa * 100:.1f}".replace(".", ",")
    print(f"\n--- Simulação de rendimento ({taxa_texto}% ao mês, "
          f"juros simples, {meses} mês(es)) ---")
    print(f"{'Cofrinho':<20}{'Hoje':>14}{'Juros':>14}{'Projetado':>14}")

    total_hoje = 0.0
    total_juros = 0.0

    for nome in cofrinhos:
        valor = cofrinhos[nome]
        juros = round(valor * taxa * meses, 2)
        total_hoje += valor
        total_juros += juros
        print(f"{nome:<20}{formatar_moeda(valor):>14}"
              f"{formatar_moeda(juros):>14}{formatar_moeda(valor + juros):>14}")

    print(f"{'TOTAL':<20}{formatar_moeda(total_hoje):>14}"
          f"{formatar_moeda(total_juros):>14}"
          f"{formatar_moeda(total_hoje + total_juros):>14}")
    print("Projeção informativa: os saldos dos cofrinhos não foram alterados.\n")


# ------------------------------------------------------------------
# CARTÃO DE CRÉDITO E FATURA (NÍVEL 2)
# limite aprovado, fatura em aberto e lista de compras do cartão
# ------------------------------------------------------------------
def limite_disponivel(conta):
    """Limite aprovado menos o que já está na fatura."""
    return round(conta[COL_LIMITE] - conta[COL_FATURA], 2)


def exibir_cartao(conta):
    """Mostra a situação do cartão de crédito."""
    print("\n--- Cartão de crédito ---")
    print(f"Limite aprovado:    {formatar_moeda(conta[COL_LIMITE])}")
    print(f"Fatura em aberto:   {formatar_moeda(conta[COL_FATURA])}")
    print(f"Limite disponível:  {formatar_moeda(limite_disponivel(conta))}")
    print(f"Compras na fatura:  {len(conta[COL_COMPRAS])}\n")


def comprar_no_credito(conta, valor, estabelecimento, categoria):
    """
    Registra uma compra no cartão: aumenta a fatura e reduz o limite
    disponível. Não mexe no saldo da conta corrente.
    Retorna True se a compra for aprovada.
    """
    # Condicionais encadeadas: cada regra reprova a compra por um motivo
    if conta[COL_LIMITE] <= 0:
        print("[ERRO] Este cartão não tem limite aprovado.")
        return False

    elif valor > limite_disponivel(conta):
        print(f"[ERRO] Compra recusada. Limite disponível: "
              f"{formatar_moeda(limite_disponivel(conta))}.")
        return False

    else:
        conta[COL_FATURA] = round(conta[COL_FATURA] + valor, 2)
        conta[COL_COMPRAS].append({
            "estabelecimento": estabelecimento,
            "categoria": categoria,
            "valor": valor,
        })
        # A despesa é reconhecida na hora da compra, não no pagamento da fatura
        registrar_movimento(conta, "Compra crédito", "saida", categoria, valor)

        print(f"[OK] Compra de {formatar_moeda(valor)} aprovada em {estabelecimento}.")
        print(f"Fatura: {formatar_moeda(conta[COL_FATURA])} | "
              f"Limite disponível: {formatar_moeda(limite_disponivel(conta))}\n")
        return True


def pagar_fatura(conta, valor):
    """
    Usa o saldo da conta corrente para quitar (total ou parcialmente) a fatura,
    restabelecendo o limite. Retorna True se o pagamento acontecer.
    """
    # Condicionais encadeadas: fatura zerada, valor acima da fatura, saldo curto
    if conta[COL_FATURA] == 0:
        print("[OK] Não há fatura em aberto para pagar.\n")
        return False

    elif valor > conta[COL_FATURA]:
        print(f"[ERRO] A fatura em aberto é de {formatar_moeda(conta[COL_FATURA])}.")
        return False

    novo_saldo, sucesso = sacar(conta[COL_SALDO], valor)
    if not sucesso:
        return False

    conta[COL_SALDO] = novo_saldo
    conta[COL_FATURA] = round(conta[COL_FATURA] - valor, 2)

    # Fatura quitada: a lista de compras do período é encerrada
    if conta[COL_FATURA] == 0:
        conta[COL_COMPRAS].clear()

    # Pagamento de fatura é quitação de dívida, não um gasto novo:
    # entra como movimento interno para não contar em dobro no relatório
    registrar_movimento(conta, "Pagto fatura", "interna", "Cartão", valor)

    print(f"[OK] Pagamento de {formatar_moeda(valor)} realizado.")
    print(f"Fatura: {formatar_moeda(conta[COL_FATURA])} | "
          f"Saldo em conta: {formatar_moeda(conta[COL_SALDO])} | "
          f"Limite disponível: {formatar_moeda(limite_disponivel(conta))}\n")
    return True


def exibir_compras(conta):
    """Lista as compras que formam a fatura atual."""
    compras = conta[COL_COMPRAS]

    if len(compras) == 0:
        print("\nNenhuma compra na fatura atual.\n")
        return

    print("\n--- Compras da fatura ---")
    print(f"{'#':<4}{'Estabelecimento':<26}{'Categoria':<16}{'Valor':>13}")

    for i in range(len(compras)):
        compra = compras[i]
        print(f"{i + 1:<4}{compra['estabelecimento']:<26}{compra['categoria']:<16}"
              f"{formatar_moeda(compra['valor']):>13}")

    print(f"{'':<4}{'TOTAL DA FATURA':<42}{formatar_moeda(conta[COL_FATURA]):>13}\n")


def menu_cartao(conta):
    """Submenu do cartão de crédito."""
    while True:
        print("-" * 44)
        print("           CARTÃO DE CRÉDITO")
        print("-" * 44)
        print("[1] Ver limite e fatura")
        print("[2] Comprar no crédito")
        print("[3] Pagar fatura")
        print("[4] Compras da fatura")
        print("[0] Voltar")
        print("-" * 44)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            exibir_cartao(conta)

        elif opcao == "2":
            estabelecimento = ler_texto("Estabelecimento: ", 25)
            if estabelecimento is not None:
                valor = ler_valor("Valor da compra: R$ ")
                if valor is not None:
                    categoria = escolher_categoria()
                    if categoria is not None:
                        comprar_no_credito(conta, valor, estabelecimento, categoria)

        elif opcao == "3":
            exibir_cartao(conta)
            if conta[COL_FATURA] > 0:
                print("Para quitar a fatura inteira, digite "
                      f"{formatar_moeda(conta[COL_FATURA])}.")
                valor = ler_valor("Valor a pagar: R$ ")
                if valor is not None:
                    pagar_fatura(conta, valor)

        elif opcao == "4":
            exibir_compras(conta)

        elif opcao == "0":
            return

        else:
            print("[ERRO] Opção inválida.\n")


# ------------------------------------------------------------------
# CARTEIRA MULTIMOEDAS / CÂMBIO (NÍVEL 2)
# O dicionário TAXAS guarda a cotação e cada conta guarda seus saldos
# ------------------------------------------------------------------
def formatar_quantidade(moeda, quantidade):
    """Formata a quantidade da moeda no padrão brasileiro. Ex: '1.234,56 USD'."""
    casas = CASAS_DECIMAIS[moeda]
    texto = f"{quantidade:,.{casas}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{texto} {moeda}"


def escolher_moeda():
    """Mostra as moedas disponíveis e retorna a escolhida, ou None."""
    moedas = list(TAXAS.keys())

    print("\nMoedas disponíveis:")
    for i in range(len(moedas)):
        moeda = moedas[i]
        print(f"[{i + 1}] {moeda} - 1 {moeda} = {formatar_moeda(TAXAS[moeda])}")

    escolha = input("Escolha a moeda: ").strip()

    if not escolha.isdigit():
        print("[ERRO] Digite o número da moeda.")
        return None

    numero = int(escolha)
    if numero < 1 or numero > len(moedas):
        print(f"[ERRO] Escolha de 1 a {len(moedas)}.")
        return None

    return moedas[numero - 1]


def ler_quantidade(moeda, mensagem):
    """
    Lê a quantidade de moeda estrangeira a vender.
    Retorna float ou None. Respeita as casas decimais de cada moeda.
    """
    entrada = input(mensagem).strip().replace(",", ".")

    try:
        quantidade = float(entrada)
    except ValueError:
        print("[ERRO] Quantidade inválida. Digite apenas números.")
        return None

    if not math.isfinite(quantidade) or quantidade <= 0:
        print("[ERRO] A quantidade deve ser maior que zero.")
        return None

    casas = CASAS_DECIMAIS[moeda]
    if round(quantidade, casas) != quantidade:
        print(f"[ERRO] {moeda} aceita no máximo {casas} casas decimais.")
        return None

    return quantidade


def valor_em_reais(saldos_moedas):
    """Converte todos os saldos em moeda estrangeira para reais."""
    total = 0.0
    for moeda in saldos_moedas:
        total += saldos_moedas[moeda] * TAXAS[moeda]
    return round(total, 2)


def exibir_carteira(conta):
    """Mostra os saldos em moeda estrangeira e o equivalente em reais."""
    saldos_moedas = conta[COL_MOEDAS]

    print("\n--- Carteira multimoedas ---")
    print(f"{'Moeda':<8}{'Cotação':>14}{'Saldo':>20}{'Em reais':>16}")

    for moeda in saldos_moedas:
        equivalente = round(saldos_moedas[moeda] * TAXAS[moeda], 2)
        print(f"{moeda:<8}{formatar_moeda(TAXAS[moeda]):>14}"
              f"{formatar_quantidade(moeda, saldos_moedas[moeda]):>20}"
              f"{formatar_moeda(equivalente):>16}")

    print(f"{'TOTAL':<8}{'':>14}{'':>20}"
          f"{formatar_moeda(valor_em_reais(saldos_moedas)):>16}\n")


def comprar_moeda_estrangeira(conta, moeda, valor_brl):
    """
    Compra moeda estrangeira usando o saldo em reais da conta.
    quantidade = valor em reais / cotação da moeda.
    Retorna True se a compra acontecer.
    """
    if moeda not in TAXAS:
        print("[ERRO] Moeda não disponível para câmbio.")
        return False

    novo_saldo, sucesso = sacar(conta[COL_SALDO], valor_brl)
    if not sucesso:
        return False

    quantidade = round(valor_brl / TAXAS[moeda], CASAS_DECIMAIS[moeda])

    conta[COL_SALDO] = novo_saldo
    if moeda not in conta[COL_MOEDAS]:
        conta[COL_MOEDAS][moeda] = 0.0
    conta[COL_MOEDAS][moeda] = round(
        conta[COL_MOEDAS][moeda] + quantidade, CASAS_DECIMAIS[moeda]
    )

    # Câmbio troca um ativo por outro: não é despesa, é movimento interno
    registrar_movimento(conta, "Compra " + moeda, "interna", "Câmbio", valor_brl)

    print(f"[OK] Compra de {formatar_quantidade(moeda, quantidade)} "
          f"por {formatar_moeda(valor_brl)}.")
    print(f"Saldo em {moeda}: {formatar_quantidade(moeda, conta[COL_MOEDAS][moeda])} | "
          f"Saldo em conta: {formatar_moeda(conta[COL_SALDO])}\n")
    return True


def vender_moeda_estrangeira(conta, moeda, quantidade):
    """
    Vende moeda estrangeira e credita o valor em reais na conta.
    valor em reais = quantidade x cotação da moeda.
    Retorna True se a venda acontecer.
    """
    if moeda not in TAXAS:
        print("[ERRO] Moeda não disponível para câmbio.")
        return False

    saldo_moeda = conta[COL_MOEDAS].get(moeda, 0.0)
    if quantidade > saldo_moeda:
        print(f"[ERRO] Saldo insuficiente. Você tem "
              f"{formatar_quantidade(moeda, saldo_moeda)}.")
        return False

    valor_brl = round(quantidade * TAXAS[moeda], 2)

    conta[COL_MOEDAS][moeda] = round(saldo_moeda - quantidade, CASAS_DECIMAIS[moeda])
    conta[COL_SALDO] = depositar(conta[COL_SALDO], valor_brl)

    registrar_movimento(conta, "Venda " + moeda, "interna", "Câmbio", valor_brl)

    print(f"[OK] Venda de {formatar_quantidade(moeda, quantidade)} "
          f"por {formatar_moeda(valor_brl)}.")
    print(f"Saldo em {moeda}: {formatar_quantidade(moeda, conta[COL_MOEDAS][moeda])} | "
          f"Saldo em conta: {formatar_moeda(conta[COL_SALDO])}\n")
    return True


def menu_cambio(conta):
    """Submenu da carteira multimoedas."""
    while True:
        print("-" * 44)
        print("           CARTEIRA MULTIMOEDAS")
        print("-" * 44)
        print("[1] Ver carteira e cotações")
        print("[2] Comprar moeda estrangeira")
        print("[3] Vender moeda estrangeira")
        print("[0] Voltar")
        print("-" * 44)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            exibir_carteira(conta)

        elif opcao == "2":
            moeda = escolher_moeda()
            if moeda is not None:
                print(f"Saldo em conta: {formatar_moeda(conta[COL_SALDO])}")
                valor = ler_valor(f"Quantos reais aplicar em {moeda}? R$ ")
                if valor is not None:
                    comprar_moeda_estrangeira(conta, moeda, valor)

        elif opcao == "3":
            exibir_carteira(conta)
            moeda = escolher_moeda()
            if moeda is not None:
                quantidade = ler_quantidade(moeda, f"Quantidade de {moeda} a vender: ")
                if quantidade is not None:
                    vender_moeda_estrangeira(conta, moeda, quantidade)

        elif opcao == "0":
            return

        else:
            print("[ERRO] Opção inválida.\n")


# ------------------------------------------------------------------
# PROGRAMA DE FIDELIDADE - BYTEPOINTS (NÍVEL 2)
# Pontos atribuídos dinamicamente a cada gasto e trocados por cashback
# ------------------------------------------------------------------
def calcular_pontos(valor):
    """1 ponto a cada R$ 10,00 gastos. A sobra não gera ponto."""
    return int(valor // GASTO_POR_PONTO)


def creditar_pontos(conta, valor):
    """Credita na conta os pontos gerados por um gasto. Retorna os pontos."""
    pontos = calcular_pontos(valor)

    if pontos > 0:
        conta[COL_PONTOS] += pontos
        print(f"[BytePoints] +{pontos} ponto(s). "
              f"Total: {conta[COL_PONTOS]} pontos.")

    return pontos


def valor_do_cashback(pontos):
    """Converte pontos em reais pela tabela de equivalência."""
    return round(pontos / PONTOS_POR_RESGATE * VALOR_POR_RESGATE, 2)


def consultar_pontos(conta):
    """Mostra o saldo de pontos e quanto ele vale em cashback."""
    pontos = conta[COL_PONTOS]
    resgatavel = pontos // PONTOS_POR_RESGATE * PONTOS_POR_RESGATE

    print("\n--- BytePoints ---")
    print(f"Saldo de pontos:     {pontos}")
    print(f"Regra de acúmulo:    1 ponto a cada {formatar_moeda(GASTO_POR_PONTO)} "
          f"em saques e PIX")
    print(f"Equivalência:        {PONTOS_POR_RESGATE} pontos = "
          f"{formatar_moeda(VALOR_POR_RESGATE)}")
    print(f"Disponível p/ saque: {resgatavel} pontos = "
          f"{formatar_moeda(valor_do_cashback(resgatavel))}\n")


def resgatar_cashback(conta, pontos):
    """
    Troca pontos por saldo na conta corrente.
    O resgate é feito em múltiplos do bloco mínimo. Retorna True se resgatar.
    """
    if pontos > conta[COL_PONTOS]:
        print(f"[ERRO] Você tem apenas {conta[COL_PONTOS]} pontos.")
        return False

    elif pontos < PONTOS_POR_RESGATE:
        print(f"[ERRO] O resgate mínimo é de {PONTOS_POR_RESGATE} pontos.")
        return False

    elif pontos % PONTOS_POR_RESGATE != 0:
        print(f"[ERRO] Resgate em múltiplos de {PONTOS_POR_RESGATE} pontos.")
        return False

    valor = valor_do_cashback(pontos)
    conta[COL_PONTOS] -= pontos
    conta[COL_SALDO] = depositar(conta[COL_SALDO], valor)

    registrar_movimento(conta, "Cashback", "entrada", "Entrada", valor)

    print(f"[OK] {pontos} pontos trocados por {formatar_moeda(valor)}.")
    print(f"Pontos restantes: {conta[COL_PONTOS]} | "
          f"Saldo em conta: {formatar_moeda(conta[COL_SALDO])}\n")
    return True


def menu_pontos(conta):
    """Submenu do programa de fidelidade."""
    while True:
        print("-" * 44)
        print("           BYTEPOINTS")
        print("-" * 44)
        print("[1] Consultar pontos")
        print("[2] Resgatar cashback")
        print("[0] Voltar")
        print("-" * 44)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            consultar_pontos(conta)

        elif opcao == "2":
            consultar_pontos(conta)
            entrada = input("Quantos pontos resgatar? ").strip()
            if entrada.isdigit():
                resgatar_cashback(conta, int(entrada))
            else:
                print("[ERRO] Digite um número inteiro de pontos.\n")

        elif opcao == "0":
            return

        else:
            print("[ERRO] Opção inválida.\n")


# ------------------------------------------------------------------
# EMPRÉSTIMO PRÉ-APROVADO (NÍVEL 2)
# A dívida é guardada como uma LISTA DE PARCELAS dentro da conta
# ------------------------------------------------------------------
def limite_emprestimo(conta):
    """Limite pré-aprovado: até 3x o saldo atual da conta corrente."""
    return round(conta[COL_SALDO] * MULTIPLICADOR_LIMITE, 2)


def tem_emprestimo_ativo(conta):
    """Retorna True se ainda houver parcelas em aberto."""
    return len(conta[COL_EMPRESTIMO]) > 0


def simular_emprestimo(valor, parcelas):
    """
    Calcula o empréstimo por juros SIMPLES: juros = valor x taxa x parcelas.
    Retorna um dicionário com os números da simulação.
    """
    juros = round(valor * TAXA_JUROS_EMPRESTIMO * parcelas, 2)
    total = round(valor + juros, 2)
    valor_parcela = round(total / parcelas, 2)

    return {
        "valor": valor,
        "parcelas": parcelas,
        "juros": juros,
        "total": total,
        "valor_parcela": valor_parcela,
    }


def exibir_simulacao(simulacao):
    """Mostra as condições do empréstimo simulado."""
    taxa_texto = f"{TAXA_JUROS_EMPRESTIMO * 100:.1f}".replace(".", ",")

    print("\n--- Simulação de empréstimo ---")
    print(f"Valor solicitado:  {formatar_moeda(simulacao['valor'])}")
    print(f"Prazo:             {simulacao['parcelas']} parcela(s)")
    print(f"Taxa:              {taxa_texto}% ao mês (juros simples)")
    print(f"Juros totais:      {formatar_moeda(simulacao['juros'])}")
    print(f"Total a pagar:     {formatar_moeda(simulacao['total'])}")
    print(f"Valor da parcela:  {formatar_moeda(simulacao['valor_parcela'])}\n")


def contratar_emprestimo(conta, valor, parcelas):
    """
    Credita o valor na conta corrente e gera a dívida parcelada.
    Retorna True se o empréstimo for contratado.
    """
    # Condicionais encadeadas: uma regra de recusa por vez
    if tem_emprestimo_ativo(conta):
        print("[ERRO] Você já tem um empréstimo em andamento.")
        return False

    elif valor > limite_emprestimo(conta):
        print(f"[ERRO] Limite pré-aprovado: "
              f"{formatar_moeda(limite_emprestimo(conta))}.")
        return False

    elif parcelas < 1 or parcelas > MAX_PARCELAS:
        print(f"[ERRO] O prazo deve ser de 1 a {MAX_PARCELAS} parcelas.")
        return False

    simulacao = simular_emprestimo(valor, parcelas)

    # Monta a LISTA DE PARCELAS da dívida
    lista_parcelas = []
    amortizacao = round(valor / parcelas, 2)
    juros_parcela = round(simulacao["juros"] / parcelas, 2)

    for numero in range(1, parcelas + 1):
        lista_parcelas.append({
            "numero": numero,
            "valor": simulacao["valor_parcela"],
            "amortizacao": amortizacao,
            "juros": juros_parcela,
            "paga": False,
        })

    conta[COL_EMPRESTIMO] = lista_parcelas
    conta[COL_SALDO] = depositar(conta[COL_SALDO], valor)

    # O dinheiro emprestado não é receita: é caixa entrando contra uma dívida
    registrar_movimento(conta, "Empréstimo", "entrada", "Entrada", valor)

    print(f"[OK] Empréstimo de {formatar_moeda(valor)} contratado em "
          f"{parcelas}x de {formatar_moeda(simulacao['valor_parcela'])}.")
    print(f"Saldo em conta: {formatar_moeda(conta[COL_SALDO])}\n")
    return True


def saldo_devedor(conta):
    """Soma as parcelas que ainda não foram pagas."""
    total = 0.0
    for parcela in conta[COL_EMPRESTIMO]:
        if not parcela["paga"]:
            total += parcela["valor"]
    return round(total, 2)


def exibir_emprestimo(conta):
    """Mostra a situação do empréstimo e a lista de parcelas."""
    if not tem_emprestimo_ativo(conta):
        print(f"\nVocê não tem empréstimo ativo.")
        print(f"Limite pré-aprovado: {formatar_moeda(limite_emprestimo(conta))}\n")
        return

    print("\n--- Meu empréstimo ---")
    print(f"{'Parcela':<10}{'Valor':>13}{'Amortização':>15}{'Juros':>12}{'Situação':>12}")

    for parcela in conta[COL_EMPRESTIMO]:
        situacao = "Paga" if parcela["paga"] else "Em aberto"
        print(f"{parcela['numero']:<10}{formatar_moeda(parcela['valor']):>13}"
              f"{formatar_moeda(parcela['amortizacao']):>15}"
              f"{formatar_moeda(parcela['juros']):>12}{situacao:>12}")

    print(f"Saldo devedor: {formatar_moeda(saldo_devedor(conta))}\n")


def pagar_parcela_emprestimo(conta):
    """
    Paga a próxima parcela em aberto usando o saldo da conta corrente.
    Retorna True se a parcela for paga.
    """
    if not tem_emprestimo_ativo(conta):
        print("[OK] Você não tem parcelas a pagar.\n")
        return False

    # Procura a primeira parcela em aberto
    proxima = None
    for parcela in conta[COL_EMPRESTIMO]:
        if not parcela["paga"]:
            proxima = parcela
            break

    novo_saldo, sucesso = sacar(conta[COL_SALDO], proxima["valor"])
    if not sucesso:
        return False

    conta[COL_SALDO] = novo_saldo
    proxima["paga"] = True

    # A amortização quita dívida (movimento interno) e os juros são despesa
    registrar_movimento(conta, "Amortização", "interna", "Empréstimo",
                        proxima["amortizacao"])
    registrar_movimento(conta, "Juros empréstimo", "saida", "Juros",
                        proxima["juros"])

    print(f"[OK] Parcela {proxima['numero']} paga: "
          f"{formatar_moeda(proxima['valor'])}.")
    print(f"Saldo em conta: {formatar_moeda(conta[COL_SALDO])}")

    if saldo_devedor(conta) == 0:
        conta[COL_EMPRESTIMO] = []
        print("[OK] Empréstimo quitado! Parabéns.\n")
    else:
        print(f"Saldo devedor: {formatar_moeda(saldo_devedor(conta))}\n")

    return True


def menu_emprestimo(conta):
    """Submenu do empréstimo pré-aprovado."""
    while True:
        print("-" * 44)
        print("           EMPRÉSTIMO")
        print("-" * 44)
        print("[1] Ver meu empréstimo / limite")
        print("[2] Simular")
        print("[3] Contratar")
        print("[4] Pagar próxima parcela")
        print("[0] Voltar")
        print("-" * 44)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            exibir_emprestimo(conta)

        elif opcao == "2" or opcao == "3":
            print(f"\nLimite pré-aprovado: "
                  f"{formatar_moeda(limite_emprestimo(conta))}")
            valor = ler_valor("Valor do empréstimo: R$ ")
            if valor is not None:
                entrada = input(f"Em quantas parcelas (1 a {MAX_PARCELAS})? ").strip()
                if not entrada.isdigit():
                    print("[ERRO] Digite um número inteiro de parcelas.\n")
                else:
                    parcelas = int(entrada)
                    if parcelas < 1 or parcelas > MAX_PARCELAS:
                        print(f"[ERRO] O prazo deve ser de 1 a {MAX_PARCELAS} "
                              f"parcelas.\n")
                    else:
                        exibir_simulacao(simular_emprestimo(valor, parcelas))
                        if opcao == "3":
                            confirma = input("Confirma a contratação? (s/n) ").strip()
                            if confirma.lower() == "s":
                                contratar_emprestimo(conta, valor, parcelas)
                            else:
                                print("Contratação cancelada.\n")

        elif opcao == "4":
            exibir_emprestimo(conta)
            if tem_emprestimo_ativo(conta):
                pagar_parcela_emprestimo(conta)

        elif opcao == "0":
            return

        else:
            print("[ERRO] Opção inválida.\n")


# ------------------------------------------------------------------
# INTERFACE (MENUS)
# ------------------------------------------------------------------
def menu_cofrinhos(conta):
    """Submenu das caixinhas de investimento."""
    while True:
        print("-" * 44)
        print("           COFRINHOS")
        print("-" * 44)
        print("[1] Ver meus cofrinhos")
        print("[2] Criar cofrinho")
        print("[3] Guardar dinheiro")
        print("[4] Resgatar dinheiro")
        print("[5] Simular rendimento")
        print("[0] Voltar")
        print("-" * 44)

        opcao = input("Escolha uma opção: ").strip()
        cofrinhos = conta[COL_COFRINHOS]

        if opcao == "1":
            exibir_cofrinhos(cofrinhos)

        elif opcao == "2":
            nome = ler_texto("Nome do cofrinho (ex: Viagem): ", 20)
            if nome is not None:
                criar_cofrinho(cofrinhos, nome)

        elif opcao == "3":
            exibir_cofrinhos(cofrinhos)
            nome = ler_texto("Em qual cofrinho guardar? ", 20)
            if nome is not None:
                valor = ler_valor("Valor a guardar: R$ ")
                if valor is not None:
                    guardar_no_cofrinho(conta, nome, valor)

        elif opcao == "4":
            exibir_cofrinhos(cofrinhos)
            nome = ler_texto("De qual cofrinho resgatar? ", 20)
            if nome is not None:
                valor = ler_valor("Valor a resgatar: R$ ")
                if valor is not None:
                    resgatar_do_cofrinho(conta, nome, valor)

        elif opcao == "5":
            meses = ler_meses("Simular por quantos meses? ")
            if meses is not None:
                simular_rendimento(cofrinhos, meses)

        elif opcao == "0":
            return

        else:
            print("[ERRO] Opção inválida.\n")


def menu_conta(contas, indice):
    """Menu da conta logada. Retorna quando o usuário sai da conta."""
    conta = contas[indice]

    while True:
        print("=" * 44)
        print(f"  BYTEBANK | Conta {conta[COL_NUMERO]} - {conta[COL_NOME]}")
        print("=" * 44)
        print("[1] Consultar saldo")
        print("[2] Depositar")
        print("[3] Sacar")
        print("[4] Transferir via PIX")
        print("[5] Cofrinhos")
        print("[6] Cartão de crédito")
        print("[7] Carteira multimoedas")
        print("[8] BytePoints (fidelidade)")
        print("[9] Empréstimo")
        print("[10] Relatório de gastos por categoria")
        print("[11] Extrato da conta")
        print("[12] Definir orçamento mensal")
        print("[13] Ver contas do banco")
        print("[0] Sair da conta")
        print("=" * 44)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            print(f"\nSaldo em conta:  {formatar_moeda(conta[COL_SALDO])}")
            print(f"Nos cofrinhos:   {formatar_moeda(total_nos_cofrinhos(conta[COL_COFRINHOS]))}")
            print(f"Saldo total:     {formatar_moeda(saldo_total(conta))}")
            print(f"Em moedas (R$): {formatar_moeda(valor_em_reais(conta[COL_MOEDAS])):>16}")
            print(f"Fatura do cartão:{formatar_moeda(conta[COL_FATURA]):>15}")
            print(f"Limite disponív.:{formatar_moeda(limite_disponivel(conta)):>15}")
            print(f"BytePoints:      {conta[COL_PONTOS]} pontos")
            if tem_emprestimo_ativo(conta):
                print(f"Saldo devedor:  {formatar_moeda(saldo_devedor(conta)):>16}")
            print(f"Sua chave PIX:   {conta[COL_CHAVE]}\n")

        elif opcao == "2":
            valor = ler_valor("Valor do depósito: R$ ")
            if valor is not None:
                conta[COL_SALDO] = depositar(conta[COL_SALDO], valor)
                registrar_movimento(conta, "Depósito", "entrada", "Entrada", valor)
                print(f"[OK] Depósito de {formatar_moeda(valor)} realizado.")
                print(f"Novo saldo: {formatar_moeda(conta[COL_SALDO])}\n")

        elif opcao == "3":
            valor = ler_valor("Valor do saque: R$ ")
            if valor is not None:
                # Categoria obrigatória: todo gasto precisa ser classificado
                categoria = escolher_categoria()
                if categoria is not None:
                    novo_saldo, sucesso = sacar(conta[COL_SALDO], valor)
                    if sucesso:
                        conta[COL_SALDO] = novo_saldo
                        registrar_movimento(conta, "Saque", "saida", categoria, valor)
                        print(f"[OK] Saque de {formatar_moeda(valor)} "
                              f"em {categoria} realizado.")
                        print(f"Novo saldo: {formatar_moeda(conta[COL_SALDO])}")
                        creditar_pontos(conta, valor)
                        print()

        elif opcao == "4":
            operacao_pix(contas, indice)

        elif opcao == "5":
            menu_cofrinhos(conta)

        elif opcao == "6":
            menu_cartao(conta)

        elif opcao == "7":
            menu_cambio(conta)

        elif opcao == "8":
            menu_pontos(conta)

        elif opcao == "9":
            menu_emprestimo(conta)

        elif opcao == "10":
            relatorio_categoria(conta)

        elif opcao == "11":
            exibir_extrato(conta)

        elif opcao == "12":
            definir_orcamento(conta)

        elif opcao == "13":
            listar_contas(contas)

        elif opcao == "0":
            print(f"Até logo, {conta[COL_NOME]}!\n")
            return

        else:
            print("[ERRO] Opção inválida.\n")


def main():
    contas = criar_contas_iniciais()

    print("=" * 44)
    print("       Bem-vindo(a) ao ByteBank!")
    print("=" * 44)

    while True:
        print("[1] Entrar na minha conta")
        print("[2] Abrir uma conta")
        print("[3] Ver contas do banco")
        print("[0] Encerrar")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            indice = autenticar(contas)
            if indice != -1:
                menu_conta(contas, indice)

        elif opcao == "2":
            abrir_conta(contas)

        elif opcao == "3":
            listar_contas(contas)

        elif opcao == "0":
            print("Obrigado por usar o ByteBank. Até logo!")
            break

        else:
            print("[ERRO] Opção inválida. Escolha 0, 1, 2 ou 3.\n")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Evita que o programa "quebre" com erro se o usuário apertar Ctrl+C
        print("\n\nSessão encerrada. Até logo!")
