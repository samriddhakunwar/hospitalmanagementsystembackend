from twtter import shorten


def test_argument():
    assert shorten("apple") == "apple"
    assert shorten("pranaya50") == "pranaya50"


def test_arguments():
    assert shorten("this is me") == "this is me"
    assert shorten("i am writing a code") == "i am writing a code"