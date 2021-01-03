import domain.core as core

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
        self.transactions.append(tx)
        
    def getMember(self, group_id, member_id):
        try:
            member = [x for x in self.members if x.member_id == member_id and group_id == x.group][0]
            member.setbalance(self.getMemberBalance(member))
            return member
        except:
            return None

    def getMemberBalance(self, member):
        credit = sum([tx.amount for tx in self.transactions \
            if tx.from_member == member.member_id and tx.group_id == member.group])
        debit = sum([tx.amount for tx in self.transactions \
            if tx.to_member == member.member_id and tx.group_id == member.group])

        return credit - debit
