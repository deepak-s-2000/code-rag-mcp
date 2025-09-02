from tree_sitter import Language, Parser
import tree_sitter_python as ts_python
import tree_sitter_cpp as ts_cpp
import tree_sitter_java as ts_java
import tree_sitter_javascript as ts_javascript
import os
import csv
import json
from app.beans.chunks import Chunks

class FileParser:
    def __init__(self, file_path):
        self.file_path = file_path

        PY_LANGUAGE = Language(ts_python.language())
        CPP_LANGUAGE = Language(ts_cpp.language())
        JAVA_LANGUAGE = Language(ts_java.language())
        JAVASCRIPT_LANGUAGE = Language(ts_javascript.language())
        
        self.LANGUAGE_PARSERS = {
                ".py": PY_LANGUAGE,
                ".cpp": CPP_LANGUAGE,
                ".java": JAVA_LANGUAGE,
                ".js": JAVASCRIPT_LANGUAGE,
            }
        self.parser = Parser()

    async def parse_file(self):
        """
    Parse a file based on its extension and extract meaningful chunks.
    """
        _, ext = os.path.splitext(self.file_path)
        if ext in self.LANGUAGE_PARSERS:
            # Tree-sitter parsing for supported languages
            parser = Parser(self.LANGUAGE_PARSERS[ext])
            with open(self.file_path, "r", encoding="utf-8") as file:
                code = file.read()
            tree = parser.parse(bytes(code, "utf8"))
            root_node = tree.root_node
            return self.extract_chunks(node=root_node, code=code)
        elif ext == ".csv":
            return self.parse_csv(self.file_path)
        elif ext == ".json":
            return self.parse_json(self.file_path)
        else:
            print(f"Unsupported file type: {ext}")
            return []

    def extract_chunks(self, node, code, chunks=None):
        """
        Recursively extract meaningful chunks from the AST.
        """
        if chunks is None:
            chunks = []
        if node.type in ["function_definition", "class_definition"]:
            chunk = Chunks(
                type=node.type,
                content=node.text.decode('utf-8'),
                file_path=self.file_path,
                start_point=node.start_point,
                end_point=node.end_point,
                name=node.child_by_field_name("name").text.decode('utf-8') if node.child_by_field_name("name") else None,
                hash=hash(node.text.decode('utf-8'))
            )
            chunks.append(chunk)
        for child in node.children:
            self.extract_chunks(child, code, chunks)
        return chunks

    def parse_csv(self):
        """
        Parse CSV files and extract rows as chunks.
        """
        chunks = []
        with open(self.file_path, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                chunk = Chunks(
                    type="csv_row",
                    content=", ".join(row),
                    file_path=self.file_path
                )
                chunks.append(chunk)
        return chunks

    def parse_json(self):
        """
        Parse JSON files and extract key-value pairs as chunks.
        """
        chunks = []
        with open(self.file_path, "r") as file:
            data = json.load(file)
            for key, value in data.items():
                chunk = Chunks(
                    type="json_key_value",
                    content=f"{key}: {value}",
                    file_path=self.file_path
                )
                chunks.append(chunk)
        return chunks
