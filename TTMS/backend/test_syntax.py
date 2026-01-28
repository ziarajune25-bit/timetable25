with open('app.py', 'r') as f:
    content = f.read()
print(f'File size: {len(content)} bytes')
print(f'Lines: {len(content.splitlines())}')
try:
    compile(content, 'app.py', 'exec')
    print('✓ Syntax is valid')
except SyntaxError as e:
    print(f'✗ Syntax error at line {e.lineno}: {e.msg}')
    if e.text:
        print(f'  Text: {e.text}')
