from src.dag import ConflictSet


def test_conflict_set():
    conflict_sets = ConflictSet()
    conflicts = [1, 2, 3]
    assert conflict_sets.get_conflict(conflicts[0]) == set([])
    updated_conflicts = conflict_sets.add_conflict(*conflicts)
    assert updated_conflicts == set(conflicts)
    for tx in conflicts:
        assert conflict_sets.get_conflict(tx) == set(conflicts)

    new_conflicts = [1, 4]
    updated_conflicts = conflict_sets.add_conflict(*new_conflicts)
    for tx in new_conflicts:
        assert conflict_sets.get_conflict(tx) == set(
            conflicts).union(set(new_conflicts))
