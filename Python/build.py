import os
import http.client
from http import HTTPStatus
import xml.etree.ElementTree as ET


class Node:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.dependencies = []

    def add_dependency(self, dependency):
        self.dependencies.append(dependency)


# get word after last underscore in string
def get_file_name(string):
    return string.split("_")[-1]


# this function adds node to bank
# if this filepath starts with 'Python_', check if filepath without 'Python_' is in bank
# if so, set that node as this node
# if this filepath does not start with 'Python_', check if filepath with 'Python_' is in bank
# if so, set this node as that node
def add_node_to_bank(node_bank, filepath):
    if filepath.startswith("Python_"):
        if filepath[7:] in node_bank:
            node_bank[filepath[7:]] = node_bank[filepath[7:]]
    else:
        if "Python_" + filepath in node_bank:
            node_bank["Python_" + filepath] = node_bank["Python_" + filepath]
    node_bank[filepath] = Node(filepath)


def populate_node_bank(svg_file_name: str = "Python.svg"):
    tree = ET.parse(svg_file_name)
    graph = tree.getroot()[0]
    node_bank = {}
    edge_separator = "->"

    for element in graph:
        # if element attribute class is 'node', get it's title as it's filepath
        if element.attrib.get("class") == "node":
            name = element[0].text
            add_node_to_bank(node_bank, name)
        elif element.attrib.get("class") == "edge":
            name = element[0].text
            # get source and target of edge. source and target are substrings of name separated by edge_separator
            independent = name[: name.index(edge_separator)]
            dependent = name[name.index(edge_separator) + len(edge_separator) :]
            # add target as dependency of source
            node_bank[dependent].add_dependency(node_bank[independent])
    return node_bank


"""
This function populates a node bank and then performs a depth first search on the graph
to find the order of nodes that should be executed."""


def get_file_paths_in_build_order(svg_file_name: str = "Python.svg"):
    print(
        "WARNING: If the dependency graph is not acyclic this program will go on forever."
    )
    node_bank = populate_node_bank(svg_file_name)
    stack = ["Python_main"]
    visited = []
    while stack:
        node = stack.pop()
        visited.append(node)
        for dependency in node_bank[node].dependencies:
            # check nodebank for bother Python_ and non-Python_ filepath of dependency and add to stack
            # the one with more dependencies should be added first
            if dependency.filepath.startswith("Python_"):
                if dependency.filepath[7:] in node_bank:
                    stack.append(dependency.filepath[7:])
                stack.append(dependency.filepath)
            else:
                if "Python_" + dependency.filepath in node_bank:
                    stack.append("Python_" + dependency.filepath)
                stack.append(dependency.filepath)
    # iterate through visited in reverse order, removing duplicates.
    # a word is considered a duplicate if the word after the last underscore is the same
    # in that case the word with the longer length is kept in the results
    # discard names that don't start with 'Python_'
    results = []
    for node in visited[::-1]:
        if node.startswith("Python_"):
            if not any(
                get_file_name(node) == get_file_name(result) for result in results
            ):
                results.append(node)

    # replace all underscores with slashes and add .py to the end
    results = [result.replace("_", "/") + ".py" for result in results]
    return results


# this function pings the server with GET to check if it's active then posts the build
# order to the server as a string
def send_build_order_to_server(port_num: str, build_order: str):
    # Check if server is active
    conn = http.client.HTTPConnection("localhost", port_num)
    conn.request("GET", "/")
    print(conn)
    response = conn.getresponse()
    if response.status != HTTPStatus.OK:
        print("Server is not active")
        return
    else:
        print("Server is active")
    # If server is active, post build order


def main():
    # editor_address=f"http://localhost:{os.environ['EDITOR_PORT']}"
    editor_port = os.environ["EDITOR_PORT"]
    # file_paths_in_build_order = get_file_paths_in_build_order("Python.svg")
    file_paths_in_build_order = ""
    print("Testing...")
    send_build_order_to_server(editor_port, file_paths_in_build_order)


# if __name__ == '__main__':
main()
