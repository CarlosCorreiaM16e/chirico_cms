#!/usr/bin/python
#-*- encoding: utf-8 -*-

"""Funções para validar números de bilhete de identidade,
   contribuinte, identificação bancária, segurança social,
   cartão de crédito e ISBN.
   Segundo contribuição de _kk_, B.Baixo, Jorge Buescu,
   Michael Gilleland (Merriam Park Software), Filipe Polido,
   Jeremy Bradbury e Hugo Pires (DRI/DRO, IIESS).
   Estas rotinas são do dominio público (sem copyright).

   versão 0.17, 2009/Nov.10
"""

#-------------------------------------------------------------
# Changes:
#   Nome das funções locais passam a iniciar-se por apenas um
#     underscore ('_')
#   O primeiro dígito de um NIF pode ser 8 (João Correia)
#   Correcção de bug na função controlCreditCard()
#   controlCreditCard() simplificada
#   Adicionada função para somar produto de membros de duas
#     lista, _sumLists(), e outras beneficiações
#   Adicionada função para validar nmero de segurança social:
#     controlNISS()
#   Adicionada funcao para validar IBAN (apenas Portugal),
#     segundo sugestao e contribuicao de Paula Vaz
#   Alterada a funcao controlNIB() conforme codigo em
#     http://download-uk.oracle.com/appsnet/115finpor.pdf
#     contribuicao de Pedro Graca segundo sugestao de
#     Francisco Pereira
#   Adicionada funcao para validar ISBN: controlISBN()
#   Adicionada funcao _toIntList() para converter string
#     lista de inteiros
#   Funcoes verificam validade de cada digito. Controlada a
#     validade do primeiro digito do NIF, contribuicao de
#     Nuno Anes
#   Corrigida a funcao controlCreditCard() segundo
#     sugestao de Pedro Graca.
#   Adicionada funcao para validar numero de cartao de
#     credito: controlCredtiCard()
#   Funcao controlNBI() corrigida por Antonio Manuel Dias
#     apos sugestao de Pedro Graca
#-------------------------------------------------------------


import string

# tamanhos dos nums do BI, contribuinte, NISS, NIB e ISBN
(LEN_NBI, LEN_NIF, LEN_NISS, LEN_NIB, LEN_ISBN) = (9, 9, 11, 21, 10)
# tamanho mínimo e máximo de num cartão de crédito
(MINLEN_CC, MAXLEN_CC) = (7, 19)


def _toIntList(numstr, acceptX = 0):
  """
  Converte string passada para lista de inteiros,
  eliminando todos os caracteres inválidos.
  Recebe string com nmero a converter.
  Segundo parâmetro indica se 'X' e 'x' devem ser
  convertidos para '10' ou nao.
  """
  res = []

  # converter todos os dígitos
  for i in numstr:
    if i in string.digits:
      res.append(int(i))

  # converter dígito de controlo no ISBN
  if acceptX and (numstr[-1] in 'Xx'):
    res.append(10)

  return res


def _valN(num):
  """
  Algoritmo para verificar validade de NBI e NIF.
  Recebe string com número a validar.
  """

  # converter num (string) para lista de inteiros
  num = _toIntList(num)

  # computar soma de controlo
  sum = 0
  for pos,dig in enumerate(num[:-1]):
    sum += dig * (9 - pos)

  # verificar soma de controlo
  return (sum % 11 and (11 - sum % 11) % 10) == num[-1]


def _sumLists(a, b):
  """
  Devolve soma dos produtos, membro a membro, das listas.
  Recebe duas listas de tamanho igual.
  """
  val = 0
  for i in map(lambda a,b: a*b, a, b):
    val += i

  return val


def controlNBI(nbi, control):
  """
  Verifica validade do número do bilhete de identidade.
  Recebe string com número BI e string com dígito de controlo.
  """

  # juntar NBI e dígito de controlo
  # adicionar zero à esquerda de nbi se for de comprimento 7
  nbi = str(nbi) + str(control)
  nbi = '0'*(len(nbi) == 8) + nbi

  # verificar tamanho do número
  if len(nbi) != LEN_NBI:
    return False

  # verificar validade
  return _valN(nbi)


def controlNIF(nif):
  """
  Verifica validade de número de contribuinte.
  Recebe string com NIF.
  """

  # verificar tamanho do número passado
  if len(nif) != LEN_NIF:
    return False

  # verificar validade do carácter inicial do NIF
  if nif[0] not in "125689":
    return False

  # verificar validade
  return _valN(nif)


def controlNISS(niss):
  """
  Verifica validade de número de segurança social.
  Recebe string com NISS.
  """
  table = (29, 23, 19, 17, 13, 11, 7, 5, 3, 2)

  # verificar tamanho do número passado
  if len(niss) != LEN_NISS:
    return False

  # verificar validade do carácter inicial do NISS
  if niss[0] not in "12":
    return False

  # converter número para lista de inteiros
  niss = _toIntList(niss)

  # verificar soma de controlo
  return niss[-1] == 9 - _sumLists(table, niss[:-1]) % 10


def controlNIB(nib):
  """
  Verifica validade de número de identificação bancária.
  Recebe string com NIB.
  """
  table = ( 73, 17, 89, 38, 62, 45, 53, 15, 50,
            5, 49, 34, 81, 76, 27, 90, 9, 30, 3 )

  # converter para lista de inteiros
  nib = _toIntList(nib)

  # verificar tamanho do número passado
  if len(nib) != LEN_NIB:
    return False

  # ultimos dois dígitos são o valor de verificação
  return nib[-2] * 10 + nib[-1] == \
         98 - _sumLists(table, nib[:-2]) % 97


def controlIBAN(iban):
  """
  Verifica validade de número de identificação bancária
  internacional (apenas Portugal).
  Recebe string com IBAN.
  """

  # verificar código IBAN para Portugal
  if iban[:4] == "PT50":
    return controlNIB(iban[5:])
  else:
    raise ValueError, "Código IBAN não suportado: %s" % iban[:4]


def controlCreditCard(ncc):
  """
  Verifica a validade de número de cartão de crédito.
  Recebe string com número do cartão de crédito.
  """

  # converter número para lista de inteiros e inverter lista
  ncc = _toIntList(ncc)
  ncc.reverse()

  # verificar tamanho do número
  if MINLEN_CC > len(ncc) or len(ncc) > MAXLEN_CC:
    return False

  # computar soma de controlo
  sum = 0
  alt = False

  for i in ncc:
    if alt:
      i *= 2
      if i > 9:
        i -= 9
    sum += i
    alt = not alt

  # verificar soma de controlo
  return not (sum % 10)


def controlISBN(isbn):
  "Verifica a validade de ISBN."
  # converter para lista de inteiros
  isbn = _toIntList(isbn, 1)

  # verificar tamanho do número
  if len(isbn) != LEN_ISBN:
    return False

  # computar soma de controlo
  sum = 0
  for pos,dig in enumerate(isbn[:-1]):
    sum += ((pos+1) * dig)

  # verificar soma de controlo
  return sum % 11 == isbn[-1]



#################################################################
# Rotina de teste
#

if __name__ == "__main__":

  print
  print "Testar BI 10039784-0:", \
        controlNBI("10039784", "0")

  print "Testar BI 6617084-2:", \
        controlNBI("6617084", "2")

  print "Testar contribuinte 204716624:", \
        controlNIF("204716624")

  print "Testar segurança social 11234567892:", \
        controlNISS("11234567892")

  print "Testar NIB 0018.0000.40359330001.87:", \
        controlNIB("0018.0000.40359330001.87")

  print "Testar IBAN PT50.0018.0000.40359330001.87:", \
        controlIBAN("PT50.0018.0000.40359330001.87")

  print "Testar cartão de crédito 1234 5678 9999 9993:", \
        controlCreditCard("1234 5678 9999 9993")

  print "Testar ISBN 972-662-792-3:", \
        controlISBN("972-662-792-3")

  print "Testar ISBN 0-471-54891-X:", \
        controlISBN("0-471-54891-X")

  print


