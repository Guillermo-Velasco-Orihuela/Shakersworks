from treelib import Tree
from pathlib import Path

def build(dirpath: Path) -> Tree:
    tree = Tree()
    tree.create_node(dirpath.name, dirpath.as_posix())  # root
    def recurse(p: Path):
        for entry in sorted(p.iterdir()):
            tree.create_node(entry.name, entry.as_posix(), parent=p.as_posix())
            if entry.is_dir():
                recurse(entry)
    recurse(dirpath)
    return tree

if __name__ == "__main__":
    t = build(Path("."))
    t.show()
