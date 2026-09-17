# 🏦 ByteBank

Projeto avaliativo da disciplina **BD015 - Algoritmos e Estruturas de Dados** — CESAR School.

O ByteBank é um sistema bancário em Python, executado no terminal, construído em 3 Sprints incrementais. Cada nível é pré-requisito para o próximo.

## 👥 Integrantes da equipe

- Patrícia Cedraz
- Vitor Argay

## 🗺️ Roadmap

| Sprint | Nível | Entrega | Status |
|---|---|---|---|
| 1 | Nível 1 (MVP) | Operações básicas (Saldo, Depósito, Saque) e validações de segurança | ✅ Concluído |
| 2 | Nível 2 (Intermediário) | Múltiplas contas em memória (Matriz), Transferência PIX e Cofrinhos | ✅ Concluído |
| 3 | Nível 3 | Pilha de estorno e fila de boletos | ⏳ Em breve |

## ⚙️ Funcionalidades (Nível 1)

**Autenticação:** o acesso exige número da conta e senha. Após 3 tentativas incorretas, o acesso é bloqueado.

**Consultar saldo:** exibe o saldo atual no formato brasileiro (ex: R$ 1.500,50).

**Depositar:** adiciona um valor ao saldo da conta.

**Sacar:** retira um valor do saldo, desde que haja saldo suficiente.

**Validações de segurança** aplicadas a todo valor digitado:

- Aceita apenas números (textos, `nan` e `inf` são recusados)
- Não aceita valores zerados ou negativos
- Aceita no máximo 2 casas decimais (centavos)
- Respeita o limite de R$ 10.000,00 por operação
- Bloqueia saques maiores que o saldo disponível
- Aceita vírgula ou ponto como separador decimal (`150,75` ou `150.75`)
- Encerra a sessão com segurança se o usuário pressionar `Ctrl+C`

## ⚙️ Funcionalidades (Nível 2)

**Múltiplas contas:** as contas ficam em uma matriz em memória, com número, titular, chave PIX, senha, saldo e cofrinhos.

**Abertura de conta:** o usuário pode criar uma conta nova, com chave PIX única e senha de 4 dígitos.

**Transferência PIX:** envio de valores entre contas com verificação da chave de destino. Recusa chave inexistente, transferência para a própria conta e valor acima do saldo.

**Cofrinhos (caixinhas de investimento):** cada conta pode criar caixinhas personalizadas, guardar dinheiro (sai do saldo principal), resgatar (volta para o saldo) e simular o rendimento por juros simples de 0,5% ao mês. A simulação é apenas uma projeção e não altera os saldos.

### Estruturas de dados aplicadas

| Estrutura | Onde é usada |
|---|---|
| Matriz (lista de listas) | Cadastro das contas do banco |
| Dicionário aninhado | Cofrinhos de cada conta |
| Busca linear | Localização da conta pela chave PIX ou pelo número |

### Contas para teste

| Conta | Titular | Senha | Chave PIX |
|---|---|---|---|
| 0001 | Patricia Cedraz | 1234 | patricia@bytebank.com |
| 0002 | Vitor Argay | 4321 | vitor@bytebank.com |
| 0003 | Maria Souza | 9999 | 81999990000 |

## ▶️ Como executar

**Pré-requisito:** Python 3.8 ou superior instalado. Nenhuma biblioteca externa é necessária.

1. Clone o repositório:
   ```bash
   git clone https://github.com/cedraz-pvc/bytebank.git
   cd bytebank
   ```

2. Execute o programa:
   ```bash
   python bytebank.py
   ```
   > No Linux/macOS, pode ser necessário usar `python3 bytebank.py`.

3. No menu inicial, escolha `[1] Entrar na minha conta` e use uma das contas da tabela acima (ex: conta `0001`, senha `1234`).

4. Navegue pelo menu da conta:
   ```
   [1] Consultar saldo
   [2] Depositar
   [3] Sacar
   [4] Transferir via PIX
   [5] Cofrinhos
   [6] Ver contas do banco
   [0] Sair da conta
   ```

> Os dados ficam apenas em memória: ao encerrar o programa, os saldos voltam aos valores iniciais.

## 📁 Estrutura do projeto

```
bytebank/
├── bytebank.py   # Código-fonte do sistema
└── README.md     # Documentação do projeto
```
