"""
LESSON 2.7: EX. 1, 2
"""


class Stack:

    def __init__(self):
        self.stack = []

    def is_empty(self):
        return True if len(self.stack) < 1 else False

    def size(self):
        return len(self.stack)

    def push(self, element):
        self.stack.append(element)

    def pop(self):
        if self.size():
            element = self.stack[self.size() - 1]
            self.stack = self.stack[:-1]
            return element
        return None

    def peek(self):
        return self.stack[self.size() - 1] if self.size() else None


def is_balanced(brackets):
    stack = Stack()
    for bracket in brackets:
        if bracket in '([{':
            stack.push(bracket)
        else:
            if not stack.size():
                return "Несбалансированно"
            top = stack.pop()
            if (top == '(' and bracket != ')') or \
                    (top == '[' and bracket != ']') or \
                    (top == '{' and bracket != '}'):
                return "Сбалансированно"
    return "Сбалансированно"


def main(text):
    result = is_balanced(text)
    print(result)


if __name__ == '__main__':
    string = input("Введите скобочки!")
    main(string)
