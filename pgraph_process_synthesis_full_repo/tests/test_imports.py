def test_imports():
    import pgraph
    from pgraph.core import Material, Operation, StructuralModel
    assert Material is not None
    assert Operation is not None
    assert StructuralModel is not None
