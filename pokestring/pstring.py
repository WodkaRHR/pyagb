#!/usr/bin/env python3

""" This module can translate any hex encoded string.
(hex -> string, string -> hex)"""

import agb.agbrom


class Triemap_node:
    """ Use a trie structure to store all words and do prefix matching """

    def __init__(self, char):
        """ A Trie node that is reached with a certain character (value)."""
        self.char = char
        self.children = {}
        self.value = None

    def insert(self, word, value):
        """ Inserts a word at this node that maps to value"""
        if not len(word):
            if self.value is None:
                self.value = value
        else:
            next_char = word[0]
            if not next_char in self.children:
                # Create a new child
                self.children[next_char] = Triemap_node(next_char)

            self.children[next_char].insert(word[1:], value)

    def get_longest_prefix(self, stream_func, depth=0):
        """ Finds value of the longest prefix that the trie stores. 
        stream_func is a function( depth : int ) that returns
        characters that are looked up or None if the stream ends.
        Returns: Value of longest prefix, length of longest prefix
        """
        next_char = stream_func(depth)
        if next_char is None:
            # Stream ends here
            return self.value, depth

        # Check if child exists and provides
        # a (longer) prefix
        if next_char not in self.children:
            # Child does not exist
            return self.value, depth

        # Check if child provides a (longer)
        # prefix
        child = self.children[next_char]
        prefix_child, depth_child = child.get_longest_prefix(
            stream_func, depth = depth + 1
        )
        if prefix_child is not None:
            return prefix_child, depth_child
        
        # Child does not provide a prefix
        return self.value, depth

        
                

class Pstring:

    def __init__(self, table, terminator=0xFF):
        """ Initilaizes an object that can translate
        hex -> string and vice versa. The table file
        defines the encoding. """

        with open(table, "r", encoding="utf-8") as f:
            content = f.read()

        self.char_to_hex = Triemap_node("")
        self.hex_to_char = Triemap_node(0)
        self.terminator = terminator

        # Parse the file linewise
        for line in content.splitlines():
            line = line.strip()

            # Remove comments
            line = line.split("@")[0]
            line = line.strip()
            if not len(line): continue

            tokens = line.split("=")
            char, sequence = "=".join(tokens[:-1]).strip(), tokens[-1].strip()

            # Parse char and sequence
            char = char.replace("'", "").replace("\"", "")
            sequence = tuple(map((lambda b: int(b, 16)), sequence.split(" ")))
            self.char_to_hex.insert(char, sequence)
            self.hex_to_char.insert(sequence, char)

    def hex2str(self, rom, offset):
        """ Retrieves a string located at a certain offset in a agb.agbrom.Agbrom rom. """
        
        string = ""
        while True:
            if rom.u8(offset) == self.terminator: return string

            # Find the longest match in the rom file:
            # Create a function that streams bytes from offset
            # and returns those or None if the terminator
            # is encountered.
            def rom_stream(depth):
                byte = rom.u8(offset + depth)
                if byte == self.terminator: return None
                return byte
            seq, len_seq = self.hex_to_char.get_longest_prefix(rom_stream, depth=0)
            string += seq
            offset += len_seq

    
    def str2hex(self, string):
        """ Converts a string into a list of 8-bit integeres. """

        sequence = []
        offset = 0
        while offset < len(string):
            
            # Find the longest match in the string:
            # Create a function that streams chars
            # from the string and returns None
            # if no more bytes can be yielded
            def str_stream(depth):
                if offset + depth < len(string):
                    return string[offset + depth]
                else:
                    return None
            

            seq, len_seq = self.char_to_hex.get_longest_prefix(str_stream, depth=0)
            sequence += seq
            offset += len_seq

        # Append terminator
        sequence.append(self.terminator)
        
        return sequence










