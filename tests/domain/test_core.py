import domain.core as core
from domain.core import Group, Member, Transaction, TxExceedsLimits
from adapters.repository import FakeRepository
import pytest

@pytest.fixture
def repo():
    """Creates an empty db
    """
    return FakeRepository()

# Behaviour 1
# ===========
# Given a base scenario (a Group with member A, member B, 
# another Group with member C)

@pytest.fixture
def base_scenario(repo):
    grupo = Group(
        group_id = "123", 
        name = "grupo", 
        individual_debt_limit = -100, 
        individual_credit_limit = 200)
    otrogrupo = Group(group_id = "124", name = "grupo")
    memberA = Member(member_id = "A", name = "A", group = "123")
    memberB = Member(member_id = "B", name = "B", group = "123")
    memberC = Member(member_id = "C", name = "C", group = "124")
    memberA.setbalance(0)
    memberB.setbalance(0)
    repo.addMember( memberA)
    repo.addMember( memberB)
    repo.addMember( memberC)
    repo.addGroup(grupo)
    repo.addGroup(otrogrupo)
    return {
        "group": grupo, 
        "memberA": memberA, 
        "memberB": memberB
    }
    
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

def test_same_member_borrow(repo, base_scenario):
    group = base_scenario["group"]
    memberA = base_scenario["memberA"]
    memberB = base_scenario["memberB"]

    # Testing debt limit
    assert core.make_valid_transaction(group, memberA, memberA, 75) is None
    