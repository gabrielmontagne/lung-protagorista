import getpass
from zipfile import _ZipDecrypter

VIM_CRYPT = b'VimCrypt~01!'


def lines(name):
    f = open(name, 'rb')
    if f.read(12) == VIM_CRYPT:
        print("File", name, "is encrypted, please enter password")
        a = getpass.getpass("key: ").encode('utf-8')
        decoder = _ZipDecrypter(a)
        result = bytes(map(decoder, f.read()))
        try:
            text = result.decode('utf-8')
        except:
            print("bad key for", name, "(skipping)")
            text = ""
    else:
        text = open(name, 'r').read()

    return text.split('\n')


if __name__ == "__main__":
    for line in lines("ae"):
        print(line, "---")

    for line in lines("a"):
        print(line, "---")
