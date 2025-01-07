import ast

def generate_docstrings(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            print(f"Function: {node.name}\n")
            print('"""')
            print(f"Summary of {node.name}.")
            print()
            print("Args:")
            for arg in node.args.args:
                print(f"    {arg.arg} ([type]): Description of {arg.arg}.")
            print()
            print("Returns:")
            print("    [type]: Description of the return value.")
            print('"""')
            print("\n\n\n")

# Example usage
generate_docstrings(r"C:\Users\kplec\Desktop\Abschlussprojekt\src\ammonit\generator.py")