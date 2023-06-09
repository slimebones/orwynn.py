from orwynn.utils.fmt import kebabify, pascalify, snakefy


def test_kebabify():
    assert kebabify("wow_hello") == "wow-hello"


def test_snakefy():
    assert snakefy("HelloWorld") == "hello_world"
    assert snakefy("hello_world") == "hello_world"
    assert snakefy("StandardHTTPS") == "standard_https"
    assert snakefy("standardHTTPS") == "standard_https"
    assert snakefy("standardHTTPSToHTTP") == "standard_https_to_http"
    assert snakefy("HTTPSToHTTPGen") == "https_to_http_gen"
    assert snakefy("HelloWorldD") == "hello_world_d"
    assert snakefy("H") == "h"
    assert snakefy("HE") == "he"
    assert snakefy("HE_WO") == "he_wo"
    assert snakefy("_hello_worldAgain_") == "_hello_world_again_"


def test_pascalify():
    assert pascalify("hello_world") == "HelloWorld"
    assert pascalify("HelloWorld") == "HelloWorld"
    assert pascalify("hello_WORLD_AGAIN") == "HelloWORLDAGAIN"
    assert pascalify("_helloworld_again_") == "_HelloworldAgain_"
    assert pascalify("h") == "H"
    assert pascalify("h_e") == "HE"
    assert pascalify("h_e_world") == "HEWorld"
    assert pascalify("____hello_world____") == "____HelloWorld____"
    assert pascalify("____hello123_w23orld____") == "____Hello123W23orld____"
    assert pascalify("____56hello1_w23orld____") == "____56hello1W23orld____"
