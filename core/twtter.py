def main():
    vowels = ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u']
    var = input("Input: ").strip()
    var = shorten(var)

    for vowel in vowels:
        var = var.replace(vowel, "")

    print(f"Output: {var}")


def shorten(word):
    vowels = ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u']
    for vowel in vowels:
        word = word.replace(vowel, "")
    return word


if __name__ == "__main__":
    main()
