#  Copyright 2021 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""
This script is used to generate the full code samples inside the `snippets`
directory, to be then used in Google Compute Engine public documentation.
"""
import argparse
import contextlib
import glob
import os
import subprocess
from collections import defaultdict
from pathlib import Path
import ast
import re
import warnings
import isort
from dataclasses import dataclass, field
from typing import List, Tuple

INGREDIENTS_START = re.compile(r"\s*#\s*<INGREDIENT ([\w\d_-]+)>")
INGREDIENTS_END = re.compile(r"\s*#\s*</INGREDIENT>")

IMPORTS_FILL = re.compile(r"\s*#\s*<IMPORTS/>")
INGREDIENT_FILL = re.compile(r"\s*#\s*<INGREDIENT ([\d\w_-]+)\s?/>")

REGION_START = re.compile(r"#\s*<REGION_START ([\d\w_-]+)>")
REGION_END = re.compile(r"#\s*<REGION_END ([\d\w_-]+)>")

HEADER = """\
# This file is automatically generated. Please do not modify it directly.
# Find the relevant recipe file in the samples/recipes or samples/ingredients 
# directory and apply your changes there.
"""

DEFAULT_OUTPUT_DIR = "snippets"


@dataclass
class ImportItem:
    """
    Represents a single import item in a script, created either by
    `import something as something_else` or
    `from module import something as something_else`.
    """
    name: str
    asname: str

    def __hash__(self):
        return hash(f"{self.name} as {self.asname}")


@dataclass
class Ingredient:
    """
    This class represents a piece of code that can be used as part of a code snippet.
    Each ingredient has a name. It is made of a list of imports that it'll require and
    text that will be pasted into the snippet.
    """
    simple_imports: List[ImportItem] = field(default_factory=list)
    imports_from: List[Tuple[str, ImportItem]] = field(default_factory=list)
    text: str = ""
    name: str = ""

    def __repr__(self):
        return f"<Ingredient: {self.name}>"


IGNORED_OUTPUT_FILES = (
    re.compile(r'.*noxfile\.py$'),
    re.compile(r'.*noxfile_config\.py$'),
    re.compile(r'.*README\.md$'),
    re.compile(r'.*requirements\.txt$'),
    re.compile(r'.*requirements-test\.txt$'),
    re.compile(r'^tests/.*')
)


def parse_imports(script: str) -> Tuple[List[ImportItem], List[Tuple[str, ImportItem]]]:
    """
    Reads a Python script file and analyzes it to extract information
    about the various things it imports. Returns a pair of lists containing
    information about the "simple imports" (`import abc as xyz`) and "imports from"
    (`from collections import deque as ...`).
    """
    parsed_script = ast.parse(script)
    simple_imports = []
    imports_from = []
    for node in parsed_script.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                simple_imports.append(ImportItem(name=alias.name, asname=alias.asname))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports_from.append((node.module, ImportItem(name=alias.name, asname=alias.asname)))
    return simple_imports, imports_from


def load_ingredient(path: Path) -> Ingredient:
    ingredient_lines = []
    in_ingredient = False
    ingredient_name = ""
    with path.open() as file:
        file_content = file.read()
    # Read imports
    simple_imports, imports_from = parse_imports(file_content)
    # Read the script
    for line in file_content.splitlines(keepends=True):
        if in_ingredient and INGREDIENTS_END.match(line):
            break
        elif in_ingredient:
            ingredient_lines.append(line)
        elif match := INGREDIENTS_START.match(line):
            ingredient_name = match.group(1)
            in_ingredient = True
    else:
        warnings.warn(f"The ingredient in {path} has no closing tag.", SyntaxWarning)
    return Ingredient(name=ingredient_name, text="".join(ingredient_lines), simple_imports=simple_imports, imports_from=imports_from)


def load_ingredients(path: Path) -> dict:
    ingredients = {}
    for ipath in path.iterdir():
        if ipath.is_dir():
            ingredients.update(load_ingredients(ipath))
        elif ipath.is_file():
            ingredient = load_ingredient(ipath)
            ingredients[ingredient.name] = ingredient
    return ingredients


def load_recipe(path: Path) -> str:
    with path.open() as file:
        return file.read()


def load_recipes(path: Path) -> dict:
    recipes = {}
    for ipath in path.iterdir():
        if ipath.is_dir():
            recipes.update(load_recipes(ipath))
        elif ipath.is_file():
            recipes[ipath] = load_recipe(ipath)
    return recipes


def render_recipe(recipe: str, ingredients: dict) -> str:
    """
    Replace all `# IMPORTS` and `# INGREDIENT <name>` occurrences in
    the provided recipe, producing a script ready to be saved to a file.
    """
    ingredients_used = []
    file_lines = recipe.splitlines()

    # Scan the file to used ingredients
    for line in file_lines:
        if match := INGREDIENT_FILL.match(line):
            ingredients_used.append(ingredients[match.group(1)])

    simple_imports_used = set()
    for ingredient in ingredients_used:
        for simple_import in ingredient.simple_imports:
            simple_imports_used.add(simple_import)

    from_imports_used = defaultdict(set)
    for ingredient in ingredients_used:
        for import_from in ingredient.imports_from:
            from_imports_used[import_from[0]].add(import_from[1])

    import_lines = set()
    for simple_import in simple_imports_used:
        if simple_import.asname:
            import_lines.add(f"import {simple_import.name} as {simple_import.asname}")
        else:
            import_lines.add(f"import {simple_import.name}")

    for module, from_imports in from_imports_used.items():
        names = set()
        for from_import in from_imports:
            if from_import.asname:
                name = f"{from_import.name} as {from_import.asname}"
            else:
                name = from_import.name
            names.add(name)
        names = ", ".join(names)
        import_lines.add(f"from {module} import {names}")

    import_lines = isort.code("\n".join(import_lines), config=isort.Config(profile='google')).splitlines()

    output_file = []
    header_added = False
    for line in file_lines:
        if IMPORTS_FILL.search(line):
            output_file.extend(import_lines)
        elif match := INGREDIENT_FILL.search(line):
            output_file.append(ingredients[match.group(1)].text)
        elif REGION_START.search(line):
            output_file.append(REGION_START.sub("# [START \\1]", line))
        elif REGION_END.search(line):
            output_file.append(REGION_END.sub("# [END \\1]", line))
        else:
            output_file.append(line)
            continue
        if not header_added:
            end = output_file[-1]
            output_file[-1] = ""
            output_file.append(HEADER)
            output_file.append("")
            output_file.append(end)
            header_added = True

    if output_file and not output_file[-1].endswith('\n'):
        output_file.append('')

    return os.linesep.join(output_file)


def save_rendered_recipe(recipe_path: Path, rendered_recipe: str, output_dir: Path = Path(DEFAULT_OUTPUT_DIR)) -> Path:
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / Path(*recipe_path.parts[1:])
    output_path.parent.mkdir(exist_ok=True)

    with output_path.open(mode='w') as out_file:
        out_file.write(rendered_recipe)

    subprocess.run(["black", str(output_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path


def generate(args: argparse.Namespace):
    ingredients = load_ingredients(Path('ingredients'))
    recipes = load_recipes(Path('recipes'))

    updated_paths = set()

    for path, recipe in recipes.items():
        rendered = render_recipe(recipe, ingredients)
        out = save_rendered_recipe(path, rendered, output_dir=Path(args.output_dir))
        updated_paths.add(str(out))

    print("Generated files:")
    for file in sorted(updated_paths):
        print(f" - {repr(file)}")

    all_files = glob.glob(f"{args.output_dir}/**", recursive=True)
    unknown_files = set()
    for file in all_files:
        if file in updated_paths:
            continue
        if any(pattern.match(file) for pattern in IGNORED_OUTPUT_FILES):
            continue
        pfile = Path(file)
        if pfile.is_dir() and pfile.iterdir():
            # Don't report non-empty dirs.
            continue
        unknown_files.add(file)

    if unknown_files:
        print(f"Found following unknown files: ")
        for file in sorted(unknown_files):
            print(f" - {repr(file)}")



def verify(args: argparse.Namespace):
    # TODO: Needs to check if the files are up to date. Will be used to auto-check every commit.
    pass


def parse_arguments():
    parser = argparse.ArgumentParser(description='Generates full code snippets from their recipes.')
    subparsers = parser.add_subparsers()

    gen_parser = subparsers.add_parser("generate", help="Generates the code samples.")
    gen_parser.set_defaults(func=generate)
    gen_parser.add_argument("--output_dir", default=DEFAULT_OUTPUT_DIR)

    verify_parser = subparsers.add_parser("verify", help="Verify if the generated samples match the sources.")
    verify_parser.set_defaults(func=verify)

    return parser.parse_args()


def main():
    args = parse_arguments()
    args.func(args)


if __name__ == '__main__':
    main()
