def isValid(s):
    stack = []
    valids = {')': '(', ']': '[', '}': '{'}

    for char in s:
        if char in valids:
            top = stack.pop() if stack else None
            if valid[char] != top:
                return False
        else:
            stack.append(char)
        
    return not stack


stack = [1, 2, 3, 4]
valids = {')': '(', ']': '[', '}': '{'}

print("yes" if '(' in valids else "no")


top = stack.pop() if stack else None
print(top)
print(stack)