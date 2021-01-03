import domain.core as core
from domain.core import Group, Member, Transaction, TxExceedsLimits, TxStatus
from tests.utils import FakeRepository
import pytest

@pytest.fixture
def repo():
    """Creates an empty db
    """
    return FakeRepository()

@pytest.fixture
def base_scenario(repo):
    grupo = Group(
        group_id = "123",
        name = "grupo",
        individual_debt_limit = -100,
        individual_credit_limit = 200)
    otrogrupo = Group(group_id = "124", name = "grupo")
    memberA = Member(member_id = "A", name = "A", group = grupo)
    memberB = Member(member_id = "B", name = "B", group = grupo)
    memberC = Member(member_id = "C", name = "C", group = otrogrupo)
    memberA.setbalance(0)
    memberB.setbalance(0)
    memberC.setbalance(0)
    repo.addMember( memberA)
    repo.addMember( memberB)
    repo.addMember( memberC)
    repo.addGroup(grupo)
    repo.addGroup(otrogrupo)
    return {
        "group": grupo,
        "memberA": memberA,
        "memberB": memberB,
        "memberC": memberC
    }

def test_tx_request(repo, base_scenario):
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    group = base_scenario["group"]
    tx = Transaction(group, memberA, memberB, 10)
    assert tx.amount == 10
    assert tx.from_member == memberA.member_id
    assert tx.to_member == memberB.member_id
    assert tx.status == TxStatus.TxRequested

def test_check_valid_transaction_request(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    tx = Transaction(group, memberA, memberB, 10)
    assert core.check_valid_transaction_request(tx)

def test_same_member_borrow(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    with pytest.raises(core.TxSameUser):
        tx = Transaction(group, memberA, memberA, 10)

def test_tx_groups_dont_match(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    memberC = base_scenario["memberC"]
    with pytest.raises(core.GroupsDontMatch):
        tx = Transaction(group, memberA, memberC, 10)

def test_member_requests_receive_credit(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    tx = memberA.request_receive_credit(from_member = memberB, amount = 10)
    assert tx.amount == 10
    assert tx.from_member == memberB.member_id
    assert tx.to_member == memberA.member_id
    assert tx.status == TxStatus.TxRequested

def test_member_requests_give_credit(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    tx = memberA.request_give_credit(to_member = memberB, amount = 10)
    assert tx.amount == 10
    assert tx.from_member == memberA.member_id
    assert tx.to_member == memberB.member_id
    assert tx.status == TxStatus.TxRequested

def test_accept_tx(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    tx = memberB.accept_tx(
             memberA.request_receive_credit(from_member = memberB, amount = 10)
         )
    assert tx.status == TxStatus.TxAccepted

def test_not_my_tx(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    memberC = base_scenario["memberC"]
    with pytest.raises(core.NotMyTransaction):
        memberC.accept_tx(
            memberA.request_receive_credit(from_member = memberB, amount = 10)
        )


def test_cant_accept_tx(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    with pytest.raises(core.CantAcceptTx):
        memberA.accept_tx(
            memberA.request_receive_credit(from_member = memberB, amount = 10)
        )
    with pytest.raises(core.CantAcceptTx):
        memberB.accept_tx(
            memberB.request_receive_credit(from_member = memberA, amount = 10)
        )
    with pytest.raises(core.CantAcceptTx):
        memberA.accept_tx(
            memberA.request_give_credit(to_member = memberB, amount = 10)
        )
    with pytest.raises(core.CantAcceptTx):
        memberB.accept_tx(
            memberB.request_give_credit(to_member = memberA, amount = 10)
        )



"""
# Behaviour 1
# ===========
# Given a base scenario (a Group with member A, member B,
# another Group with member C)
# When member A borrows from B an amount of money
# Then
#       if Group Limits permit transaction
#           a transaction is registered,
#           A's balance decreases by amount,
#           B's balance increases by amount
#           Total balance in group is zero
def test_AborrowsB_within_limits(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]

    initialAbal = repo.getMemberBalance(memberA)
    initialBbal = repo.getMemberBalance(memberB)
    repo.addTx(group, memberA, memberB, 75)
    assert repo.getMemberBalance(memberA) == initialAbal + 75
    assert repo.getMemberBalance(memberB) == initialBbal - 75

#       else
#           transaction is not registered
#           A and B balances remain the same
def test_AborrowsB_exceeds_limits(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]
    # Testing debt limit
    repo.addTx(group, memberA, memberB, 75)
    initialAbal = repo.getMemberBalance(memberA)
    initialBbal = repo.getMemberBalance(memberB)
    with pytest.raises(TxExceedsLimits):
        repo.addTx(group, memberA, memberB, 75)
    assert repo.getMemberBalance(memberA) == initialAbal
    assert repo.getMemberBalance(memberB) == initialBbal
    # Testing credit limit
    group.individual_credit_limit = 80
    with pytest.raises(TxExceedsLimits):
        repo.addTx(group, memberA, memberB, 10)
    assert repo.getMemberBalance(memberA) == initialAbal
    assert repo.getMemberBalance(memberB) == initialBbal
"""
