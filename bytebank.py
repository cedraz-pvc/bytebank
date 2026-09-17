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

Estruturas de dados usadas:
    MATRIZ (lista de listas) -> cada linha é uma conta, cada coluna um dado:
        [numero, nome, chave_pix, senha, saldo, cofrinhos]
    DICIONÁRIO ANINHADO -> a última coluna de cada conta guarda os cofrinhos:
        {"Viagem": 500.0, "Reserva": 1200.0}
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


def criar_contas_iniciais():
    """
    Monta a matriz de contas do banco (lista de listas).
    Os dados abaixo já vêm cadastrados para facilitar os testes.
    """
    return [
        ["0001", "Patricia Cedraz", "patricia@bytebank.com", "1234", 2500.00,
         {"Viagem": 500.00, "Reserva": 1200.00}],
        ["0002", "Vitor Argay", "vitor@bytebank.com", "4321", 1800.00,
         {}],
        ["0003", "Maria Souza", "81999990000", "9999", 350.00,
         {"Bicicleta": 120.00}],
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
    contas.append([numero, nome, chave, senha, 0.0, {}])

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
# TRANSFERÊNCIA PIX (NÍVEL 2)
# ------------------------------------------------------------------
def transferir_pix(contas, indice_origem, chave_destino, valor):
    """
    Transfere um valor da conta de origem para a conta da chave informada.
    Reaproveita sacar() e depositar() do Nível 1.
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

    print(f"[OK] PIX de {formatar_moeda(valor)} enviado para "
          f"{contas[indice_destino][COL_NOME]}.")
    print(f"Novo saldo: {formatar_moeda(contas[indice_origem][COL_SALDO])}\n")
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

    transferir_pix(contas, indice, chave, valor)


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
        print("[6] Ver contas do banco")
        print("[0] Sair da conta")
        print("=" * 44)

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            print(f"\nSaldo em conta:  {formatar_moeda(conta[COL_SALDO])}")
            print(f"Nos cofrinhos:   {formatar_moeda(total_nos_cofrinhos(conta[COL_COFRINHOS]))}")
            print(f"Saldo total:     {formatar_moeda(saldo_total(conta))}")
            print(f"Sua chave PIX:   {conta[COL_CHAVE]}\n")

        elif opcao == "2":
            valor = ler_valor("Valor do depósito: R$ ")
            if valor is not None:
                conta[COL_SALDO] = depositar(conta[COL_SALDO], valor)
                print(f"[OK] Depósito de {formatar_moeda(valor)} realizado.")
                print(f"Novo saldo: {formatar_moeda(conta[COL_SALDO])}\n")

        elif opcao == "3":
            valor = ler_valor("Valor do saque: R$ ")
            if valor is not None:
                novo_saldo, sucesso = sacar(conta[COL_SALDO], valor)
                if sucesso:
                    conta[COL_SALDO] = novo_saldo
                    print(f"[OK] Saque de {formatar_moeda(valor)} realizado.")
                    print(f"Novo saldo: {formatar_moeda(conta[COL_SALDO])}\n")

        elif opcao == "4":
            operacao_pix(contas, indice)

        elif opcao == "5":
            menu_cofrinhos(conta)

        elif opcao == "6":
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
