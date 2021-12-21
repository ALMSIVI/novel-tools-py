from textwrap import dedent

num_dict = {
    "零": 0,
    "〇": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
    "廿": 20,
    "卅": 30,
    "卌": 40,
    "百": 100,
    "千": 1000
}

valid_filenames = dict((ord(char), None) for char in '\\/*?:"<>|\n')


def to_num(num: str) -> int:
    """
    Converts a chinese string to a number.
    """
    num = num.strip()
    try:
        value = 0
        digit = 1

        for i in range(len(num)):
            v = num_dict[num[i]]
            if v >= 10:
                digit *= v
                value += digit
            elif i == len(num) - 1:
                value += v
            else:
                digit = v
    except KeyError:
        value = int(num)

    return value


def purify_name(filename: str) -> str:
    return filename.translate(valid_filenames).strip()


def format_text(text: str) -> str:
    return dedent(text).strip()
