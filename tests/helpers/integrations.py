import os


def assert_file(filename1: str, filename2: str):
    f1 = open(filename1, 'rt')
    f2 = open(filename2, 'rt')
    content1 = f1.read()
    content2 = f2.read()
    f1.close()
    f2.close()

    assert content1 == content2


def assert_directory(dir1: str, dir2: str):
    list1 = os.listdir(dir1)
    list2 = os.listdir(dir2)
    assert sorted(list1) == sorted(list2)

    for name in list1:
        name1 = os.path.join(dir1, name)
        name2 = os.path.join(dir2, name)
        if os.path.isfile(name1):
            assert_file(name1, name2)
        else:
            assert_directory(name1, name2)
