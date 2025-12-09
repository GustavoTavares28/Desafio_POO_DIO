from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


# =====================================================
#                     CLIENTES
# =====================================================
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


# =====================================================
#                     CONTAS
# =====================================================
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor > self._saldo:
            print("\nSaldo insuficiente!")
            return False

        if valor <= 0:
            print("\nValor inválido!")
            return False

        self._saldo -= valor
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\nValor inválido!")
            return False

        self._saldo += valor
        print("\n=== Depósito realizado com sucesso! ===")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([t for t in self.historico.transacoes if t["tipo"] == "Saque"])

        if valor > self.limite:
            print("\nValor excede o limite de saque!")
            return False

        if numero_saques >= self.limite_saques:
            print("\nLimite diário de saques excedido!")
            return False

        return super().sacar(valor)

    def __str__(self):
        return f"""
Agência:{self.agencia}
Conta:{self.numero}
Titular:{self.cliente.nome}
        """


# =====================================================
#                     HISTÓRICO
# =====================================================
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
        )


# =====================================================
#                     TRANSAÇÕES
# =====================================================
class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)


# =====================================================
#                     FUNÇÕES DO MENU
# =====================================================
def menu():
    op = """
======== MENU ========
 [d] Depositar
 [s] Sacar
 [e] Extrato
[nu] Novo Usuário
[nc] Nova Conta
[lu] Listar Usuários
[lc] Listar Contas
 [q] Sair
=> """
    return input(op).lower()


def filtrar_usuario(cpf, usuarios):
    for u in usuarios:
        if u.cpf == cpf:
            return u
    return None


def criar_usuario(usuarios):
    cpf = input("\nCPF: ")

    usuario = filtrar_usuario(cpf, usuarios)
    if usuario:
        print("\nUsuário já existe!")
        return

    nome = input("Nome: ")
    nasc = input("Nascimento (dd-mm-aaaa): ")
    end = input("Endereço: ")

    novo = PessoaFisica(nome, nasc, cpf, end)
    usuarios.append(novo)
    print("\n=== Usuário criado com sucesso! ===")


def criar_conta(contas, usuarios):
    cpf = input("\nCPF do usuário: ")

    usuario = filtrar_usuario(cpf, usuarios)
    if not usuario:
        print("\nUsuário não encontrado!")
        return

    numero = len(contas) + 1
    conta = ContaCorrente(numero, usuario)
    usuario.adicionar_conta(conta)
    contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_usuarios(usuarios):
    if not usuarios:
        print("\nNenhum usuário cadastrado.")
        return

    print("\n===== USUÁRIOS =====")
    for u in usuarios:
        print(f"Nome: {u.nome} | CPF: {u.cpf} | Endereço: {u.endereco}")


def listar_contas(contas):
    if not contas:
        print("\nNenhuma conta cadastrada.")
        return

    print("\n===== CONTAS =====")
    for c in contas:
        print(c)


def exibir_extrato(conta):
    print("\n======= EXTRATO ========")

    transacoes = conta.historico.transacoes

    if not transacoes:
        print("Nenhuma movimentação.")
    else:
        for t in transacoes:
            print(f"{t['tipo']}: R$ {t['valor']:.2f} — {t['data']}")

    print(f"\nSaldo atual: R$ {conta.saldo:.2f}")
    print("===========================")


# =====================================================
#                     PROGRAMA PRINCIPAL
# =====================================================
def main():
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            cpf = input("\nCPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)
            if not usuario or not usuario.contas:
                print("\nUsuário sem conta!")
                continue

            conta = usuario.contas[0]
            valor = float(input("Valor do depósito: "))
            usuario.realizar_transacao(conta, Deposito(valor))

        elif opcao == "s":
            cpf = input("\nCPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)
            if not usuario or not usuario.contas:
                print("\nUsuário sem conta!")
                continue

            conta = usuario.contas[0]
            valor = float(input("Valor do saque: "))
            usuario.realizar_transacao(conta, Saque(valor))

        elif opcao == "e":
            cpf = input("\nCPF do titular: ")
            usuario = filtrar_usuario(cpf, usuarios)
            if not usuario or not usuario.contas:
                print("\nUsuário sem conta!")
                continue

            exibir_extrato(usuario.contas[0])

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            criar_conta(contas, usuarios)

        elif opcao == "lu":
            listar_usuarios(usuarios)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            print("\nSaindo...")
            break

        else:
            print("\nOpção inválida!")

main()
