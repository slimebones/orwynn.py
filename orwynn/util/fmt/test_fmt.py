from orwynn.util.fmt import camelfy, snakefy


def test_snakefy():
    assert snakefy("HelloWorld") == "hello_world"
    assert snakefy("hello_world") == "hello_world"
    assert snakefy("StandardHTTPS") == "standard_https"
    assert snakefy("standardHTTPS") == "standard_https"
    assert snakefy("standardHTTPSToHTTP") == "standard_https_to_http"
    assert snakefy("HTTPSToHTTPGen") == "standard_https_to_http_gen"
    assert snakefy("HelloWorldD") == "hello_world_d"
    assert snakefy("H") == "h"
    assert snakefy("HE") == "he"
    assert snakefy("HE_WO") == "he_wo"


def test_camelfy():
    assert camelfy("hello_world") == "helloWorld"
    assert camelfy("HelloWorld") == "HelloWorld"
    assert camelfy("hello_WORLD_AGAIN") == "HelloWORLDAGAIN"
    assert camelfy("_helloworld_again_") == "_helloworldAgain_"
    assert camelfy("h") == "h"
    assert camelfy("h_e") == "hE"
    assert camelfy("h_e_world") == "hEWorld"
