class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        # Remembers the word exactly as it was typed when inserted
        # (for example "Viman Nagar"), because the path itself is lowercase.
        self.original_word = None


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str):
        """
        Inserts a word into the trie.

        Time Complexity: O(L) where L is the length of the word.
        """
        original_word = word
        node = self.root

        # The path through the trie is lowercase so searching ignores casing
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_end_of_word = True
        node.original_word = original_word

    def search_prefix(self, prefix: str) -> list:
        """
        Returns all words that start with the given prefix,
        in alphabetical order, with their original casing.

        Time Complexity: O(P) to walk down the prefix, plus O(V) to collect
        the matches, where V is the number of nodes under the prefix.
        """
        node = self.root
        prefix = prefix.lower()

        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results = []
        self._dfs_collect(node, results)
        return results

    def _dfs_collect(self, node: TrieNode, results: list):
        """Depth-first search that collects every complete word below node."""
        if node.is_end_of_word:
            results.append(node.original_word)

        # sorted() keeps the suggestions in alphabetical order
        for char in sorted(node.children.keys()):
            self._dfs_collect(node.children[char], results)