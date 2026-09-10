"""
ByteBank - Nível 1 (MVP)
CESAR School | BD015 - Algoritmos e Estruturas de Dados

Funcionalidades do Nível 1:
    - Autenticação por senha (máximo de 3 tentativas)
    - Consulta de saldo
    - Depósito
    - Saque
    - Validações de segurança em todas as entradas do usuário
"""

import math

# ------------------------------------------------------------------
# CONFIGURAÇÕES DO SISTEMA
# ------------------------------------------------------------------
SENHA_CORRETA = "1234"          # Senha de acesso da conta
MAX_TENTATIVAS = 3              # Tentativas de senha antes do bloqueio
SALDO_INICIAL = 0.0             # Saldo com que a conta começa
LIMITE_POR_OPERACAO = 10000.00  # Valor máximo por depósito ou saque


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


# ------------------------------------------------------------------
# SEGURANÇA
# ------------------------------------------------------------------
def autenticar():
    """
    Pede a senha ao usuário. Retorna True se acertar dentro do limite
    de tentativas, ou False se a conta for bloqueada.
    """
    tentativas = 0

    while tentativas < MAX_TENTATIVAS:
        senha = input("Digite sua senha: ").strip()

        if senha == SENHA_CORRETA:
            print("[OK] Acesso liberado!\n")
            return True

        tentativas += 1
        restantes = MAX_TENTATIVAS - tentativas
        if restantes > 0:
            print(f"[ERRO] Senha incorreta. Tentativas restantes: {restantes}")

    print("[BLOQUEADO] Conta bloqueada por excesso de tentativas.")
    return False


# ------------------------------------------------------------------
# OPERAÇÕES BANCÁRIAS
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
# INTERFACE (MENU)
# ------------------------------------------------------------------
def exibir_menu():
    print("=" * 40)
    print("           BYTEBANK - MENU")
    print("=" * 40)
    print("[1] Consultar saldo")
    print("[2] Depositar")
    print("[3] Sacar")
    print("[0] Sair")
    print("=" * 40)


def main():
    print("=" * 40)
    print("      Bem-vindo(a) ao ByteBank!")
    print("=" * 40)

    if not autenticar():
        return

    saldo = SALDO_INICIAL

    while True:
        exibir_menu()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            print(f"\nSaldo atual: {formatar_moeda(saldo)}\n")

        elif opcao == "2":
            valor = ler_valor("Valor do depósito: R$ ")
            if valor is not None:
                saldo = depositar(saldo, valor)
                print(f"[OK] Depósito de {formatar_moeda(valor)} realizado.")
                print(f"Novo saldo: {formatar_moeda(saldo)}\n")

        elif opcao == "3":
            valor = ler_valor("Valor do saque: R$ ")
            if valor is not None:
                saldo, sucesso = sacar(saldo, valor)
                if sucesso:
                    print(f"[OK] Saque de {formatar_moeda(valor)} realizado.")
                    print(f"Novo saldo: {formatar_moeda(saldo)}\n")

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
