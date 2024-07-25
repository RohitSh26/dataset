import os
import ast
import json
from collections import defaultdict
from typing import List, Dict, Any

class PydanticFieldExtractor(ast.NodeVisitor):
    def __init__(self):
        self.numeric_fields = defaultdict(list)

    def visit_ClassDef(self, node: ast.ClassDef):
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseModel":
                for stmt in node.body:
                    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                        field_name = stmt.target.id
                        if isinstance(stmt.annotation, ast.Name):
                            field_type = stmt.annotation.id
                            if field_type in {"int", "float"}:
                                self.numeric_fields[node.name].append({"field": field_name, "type": field_type})
        self.generic_visit(node)

def extract_numeric_fields_from_file(file_path: str) -> Dict[str, List[Dict[str, str]]]:
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())
    
    extractor = PydanticFieldExtractor()
    extractor.visit(tree)
    
    return extractor.numeric_fields

def extract_numeric_fields_from_directory(directory_path: str) -> Dict[str, List[Dict[str, str]]]:
    all_numeric_fields = defaultdict(list)
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_numeric_fields = extract_numeric_fields_from_file(file_path)
                for class_name, fields in file_numeric_fields.items():
                    all_numeric_fields[class_name].extend(fields)
    return all_numeric_fields

if __name__ == "__main__":
    directory_path = "path/to/your/directory"
    numeric_fields = extract_numeric_fields_from_directory(directory_path)
    print(json.dumps(numeric_fields, indent=4))