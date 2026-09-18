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
| 2 | Nível 2 (Intermediário) | Múltiplas contas em memória (Matriz), Transferência PIX, Cofrinhos, Categorização de gastos, Cartão de crédito, Carteira multimoedas, BytePoints e Empréstimos | ✅ Concluído |
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

**Categorização de gastos:** todo saque e todo PIX enviado exigem a escolha de uma categoria (Alimentação, Transporte, Lazer, Contas ou Outros). Cada movimentação é registrada no histórico da conta.

**Relatório por categoria:** a função `relatorio_categoria()` percorre o histórico, soma os gastos de cada categoria e mostra o valor, o percentual sobre o total gasto, o percentual do orçamento mensal consumido e um alerta quando o orçamento é estourado. O orçamento pode ser alterado pelo menu.

**Extrato:** lista todas as movimentações da conta, identificando saídas (-), entradas (+) e movimentos internos de cofrinho ou fatura (~).

**Cartão de crédito:** cada conta tem limite aprovado, fatura em aberto e lista de compras. A função `comprar_no_credito()` aumenta a fatura e reduz o limite disponível sem tocar no saldo da conta corrente, recusando a compra quando o limite não é suficiente. A função `pagar_fatura()` usa o saldo da conta corrente para quitar a fatura, total ou parcialmente, e restabelece o limite. A despesa é reconhecida na compra, então o pagamento da fatura não conta em dobro no relatório de gastos.

**Carteira multimoedas:** além do saldo em reais, cada conta tem saldos em USD, EUR e BTC. As funções `comprar_moeda_estrangeira()` e `vender_moeda_estrangeira()` convertem os valores pelas cotações fixas do dicionário `TAXAS` (1 USD = R$ 5,50 | 1 EUR = R$ 6,00 | 1 BTC = R$ 350.000,00). O câmbio troca um ativo por outro, então não entra no relatório de despesas. Moedas fiduciárias usam 2 casas decimais e o BTC usa 8.

**BytePoints (fidelidade e cashback):** a cada R$ 10,00 gastos em saques e PIX enviados, o cliente acumula 1 ponto. A função `consultar_pontos()` mostra o saldo e a tabela de equivalência, e `resgatar_cashback()` converte os pontos em saldo na conta corrente, à razão de 100 pontos = R$ 5,00, em múltiplos do bloco mínimo.

**Empréstimo pré-aprovado:** o limite é de até 3x o saldo atual da conta. A função `simular_emprestimo()` calcula juros simples de 2% ao mês, o total a pagar e o valor da parcela. `contratar_emprestimo()` credita o valor na conta e gera a dívida como uma lista de parcelas, e `pagar_parcela_emprestimo()` quita a próxima parcela em aberto usando o saldo da conta. Cada parcela separa amortização e juros: só os juros entram como despesa no relatório.

### Estruturas de dados aplicadas

| Estrutura | Onde é usada |
|---|---|
| Matriz (lista de listas) | Cadastro das contas do banco |
| Dicionário aninhado | Cofrinhos e saldos em moeda estrangeira de cada conta |
| Lista de dicionários | Histórico, compras do cartão e parcelas do empréstimo |
| Agregação com dicionário (GROUP BY) | Soma dos gastos por categoria no relatório |
| Condicionais encadeadas | Aprovação de compra no crédito e pagamento da fatura |
| Dicionário de taxas | Cotações do câmbio e tabela de equivalência dos pontos |
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
   [6] Cartão de crédito
   [7] Carteira multimoedas
   [8] BytePoints (fidelidade)
   [9] Empréstimo
   [10] Relatório de gastos por categoria
   [11] Extrato da conta
   [12] Definir orçamento mensal
   [13] Ver contas do banco
   [0] Sair da conta
   ```

> Os dados ficam apenas em memória: ao encerrar o programa, os saldos voltam aos valores iniciais.

## 📁 Estrutura do projeto

```
bytebank/
├── bytebank.py   # Código-fonte do sistema
└── README.md     # Documentação do projeto
```
