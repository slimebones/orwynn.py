from orwynn.mongo import Doc
from pykit.str import StringUtils


def test_snake_case():
    class _Doc1(Doc):
        COLLECTION_NAMING = "snake_case"
    assert _Doc1.get_collection() == "_doc1"

    class __Doc2_wow(Doc):
        COLLECTION_NAMING = "snake_case"
    assert __Doc2_wow.get_collection() == "__doc2_wow"

    class Hello_World(Doc):
        COLLECTION_NAMING = "snake_case"
    assert Hello_World.get_collection() == "hello_world"

    class Hello_World_123(Doc):
        COLLECTION_NAMING = "snake_case"
    assert Hello_World_123.get_collection() == "hello_world_123"

    class intro_Hello_World_wow(Doc):
        COLLECTION_NAMING = "snake_case"
    assert intro_Hello_World_wow.get_collection() == "intro_hello_world_wow"

    class HelloWorldXYZ(Doc):
        COLLECTION_NAMING = "snake_case"
    assert HelloWorldXYZ.get_collection() == "hello_world_xyz"

    class HelloWorldXYZGo(Doc):
        COLLECTION_NAMING = "snake_case"
    assert HelloWorldXYZGo.get_collection() == "hello_world_xyz_go"
