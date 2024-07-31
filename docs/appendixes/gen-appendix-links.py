from markdown_it.tree import SyntaxTreeNode
from markdown_it import MarkdownIt

import os
import fnmatch
import click

@click.command()
@click.argument('dir', required=True)
def parse_markdown_files(dir):
    all_href = get_all_hrefs(dir)
    with open(f"{dir}/appendixes/appendix-links.md", "w") as appendix:
        appendix.write("""<!-- this file is generated by toolings -->
# Appendix "All links"
               
This is a collection of all the links from this website:

"""
        )
        for e in all_href:
            appendix.write(f"- {e}\n")
        appendix.write("\n")

def get_all_hrefs(dir):
    md = MarkdownIt("commonmark")
    all_href = []
    for root, _, files in os.walk(dir):
        for filename in fnmatch.filter(files, '*.md'):
            if filename == "appendix-links.md":
                continue # skip appendix-links file itself
            with open(f"{root}/{filename}", "r") as f:
                tokens = md.parse(f.read())
                node = SyntaxTreeNode(tokens)
                for n in node.walk():
                    if n.type == "link":
                        all_href.append(n.attrs["href"])
    all_href.sort()
    print(all_href)
    return all_href

if __name__ == '__main__':
    parse_markdown_files()
