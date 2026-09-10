# ByteBank

Projeto avaliativo da disciplina **BD015 - Algoritmos e Estruturas de Dados** — CESAR School.

O ByteBank é um sistema bancário em Python, executado no terminal, construído em 3 Sprints incrementais. Cada nível é pré-requisito para o próximo.

## Integrantes da equipe

- Patrícia Cedraz
- Vitor Argay

## Roadmap

| Sprint | Nível | Entrega | Status |
|---|---|---|---|
| 1 | Nível 1 (MVP) | Operações básicas (Saldo, Depósito, Saque) e validações de segurança | ✅ Concluído |
| 2 | Nível 2 (Intermediário) | Múltiplas contas em memória (Matriz) e Transferência PIX | ⏳ Em breve |
| 3 | Nível 3 | Pilha de estorno e fila de boletos | ⏳ Em breve |

## Funcionalidades (Nível 1)

**Autenticação:** o acesso exige senha. Após 3 tentativas incorretas, a conta é bloqueada.

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

3. Digite a senha de acesso: **`1234`**

4. Use o menu numérico para navegar:
   ```
   [1] Consultar saldo
   [2] Depositar
   [3] Sacar
   [0] Sair
   ```

## 📁 Estrutura do projeto

```
bytebank/
├── bytebank.py   # Código-fonte do sistema
└── README.md     # Documentação do projeto
```
