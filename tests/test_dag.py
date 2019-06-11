from src.dag import ConflictSet


def test_conflict_set():
    conflict_sets = ConflictSet()
    conflicts = [1, 2, 3]
    assert conflict_sets.get_conflict(conflicts[0]) == set([])
    updated_conflicts = conflict_sets.add_conflict(*conflicts)
    assert updated_conflicts == set(conflicts)
    assert conflict_sets.get_conflict(conflicts[0]) == set(conflicts)
