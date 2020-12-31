import domain.core as core

class DuplicateTx(Exception):
    pass

class FakeRepository:
    def __init__(self):
        self.groups = []
        self.members = []
        self.transactions = []
    def addGroup(self, group):
        self.groups.append(group)

    def addMember(self, member):
        self.members.append(member)

    def addTx(self, group, mA, mB, amount):
        self.transactions.append(core.make_valid_transaction(group, mA, mB, amount))
        mA.setbalance(self.getMemberBalance(mA))
        mB.setbalance(self.getMemberBalance(mB))

    def getMemberBalance(self, member):
        credit = sum([tx.amount for tx in self.transactions \
            if tx.from_member == member.member_id and tx.group_id == member.group])
        debit = sum([tx.amount for tx in self.transactions \
            if tx.to_member == member.member_id and tx.group_id == member.group]) 

        return credit - debit