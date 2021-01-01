import adapters.sqlmodels as sqlmodels
import domain.core as coremodel
import adapters.sqlrepo as sqlrepo

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers


@pytest.fixture
def db():
    engine = create_engine('sqlite:///:memory:')
    sqlmodels.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(db):
    sqlmodels.start_mappers()
    yield sessionmaker(bind=db)()
    clear_mappers()

@pytest.fixture
def repo(session):
    return sqlrepo.SQLRepository(session)

def test_repository(repo):
    group = coremodel.Group(
        group_id = "123",
        name = "test"
    )
    repo.addGroup(group)
    savedgroup = repo.getGroup("123")
    assert savedgroup.group_id == group.group_id and \
           savedgroup.name == group.name

    memberA = coremodel.Member(
            group = "123",
            member_id = "A",
            name = "test_member"
        )
    repo.addMember(memberA)
    savedm = repo.getMember("123", "A")
    assert savedm.group == memberA.group and \
           savedm.name == memberA.name

    memberB = coremodel.Member(
                group = "123",
                member_id = "B",
                name = "other_test_member"
            )
    repo.addMember(memberB)
        
    repo.addTx(group, memberA, memberB, 50)
    repo.addTx(group, memberA, memberB, 10)
    repo.addTx(group, memberB, memberA, 2)
    assert repo.getMemberBalance(memberA) == 50+10-2
    assert repo.getMemberBalance(memberB) == -50-10+2
    
        