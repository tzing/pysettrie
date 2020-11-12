import bisect
import collections
import typing

__version__ = "0.2.0"
__all__ = ["SetTrie", "SetTrieDict"]


_KT = typing.TypeVar("_KT")
_VT = typing.TypeVar("_VT")


class SortedDict(collections.OrderedDict):
    """Sorted dict. Iteration order is always sorted by its key."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._klist = list(self)

    def __setitem__(self, k, v) -> None:
        is_update = k in self

        super().__setitem__(k, v)
        if is_update:
            return

        idx = bisect.bisect_right(self._klist, k)
        for key in self._klist[idx:]:
            self.move_to_end(key)
        self._klist.insert(idx, k)

    def __delitem__(self, v) -> None:
        super().__delitem__(v)
        self._klist.pop(bisect.bisect_left(self._klist, v))


class _SimpleNode(typing.Generic[_KT]):
    """Node object used by SetTrie. You probably don't need to use it from
    the outside.
    """

    __slots__ = ("children", "is_leaf", "data")

    children: "typing.Dict[_KT, _SimpleNode[_KT]]"
    is_leaf: "bool"
    data: "_KT"

    def __init__(self, data: "_KT" = None):
        # child nodes a.k.a. children
        self.children = SortedDict()

        # if True, this is the last element of a key set store a
        # member element of the key set. Must be a hashable
        # (i.e. hash(data) should work) and comparable/orderable
        # (i.e. data1 < data2 should work; see
        # https://wiki.python.org/moin/HowTo/Sorting/) type.
        self.is_leaf = False

        self.data = data

    def __repr__(self):
        return "<Node %s>" % self.data

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return self.data != other.data

    def __lt__(self, other):
        return self.data < other.data

    def __le__(self, other):
        return self.data <= other.data

    def __gt__(self, other):
        return self.data > other.data

    def __ge__(self, other):
        return self.data >= other.data

    def __hash__(self) -> int:
        return hash(self.data)


class _ValueNode(_SimpleNode, typing.Generic[_KT, _VT]):
    """Node with value."""

    __slots__ = ("value",)

    children: "typing.Dict[_KT, _ValueNode[_KT]]"
    value: "_VT"

    def __init__(self, data: "_KT" = None, value: "_VT" = None):
        super().__init__(data)
        # the value associated to the key set if is_leaf ==
        # True, otherwise None
        self.value = None


_T_NODE = typing.Union[_SimpleNode, _ValueNode]
_T_KEYSET = typing.Tuple[_KT]
_T_KEYSET_COMPITABLE = typing.Iterable[_KT]
_T_KEY_ITER = typing.Iterator[_KT]


class _SetTrie(typing.Generic[_KT, _VT]):
    """Abstracted set trie implement."""

    Node: "_T_NODE"

    @staticmethod
    def _to_keyset(akey: "_T_KEYSET_COMPITABLE") -> "_T_KEY_ITER":
        """Convert any input to a valid iterator type for internal use."""
        return iter(sorted(set(akey)))

    def __len__(self):
        """Trie size."""

        def dfs(node: "_T_NODE"):
            size = 0
            if node.is_leaf:
                size += 1
            for child in node.children.values():
                size += dfs(child)
            return size

        return dfs(self.root)

    def __iter__(self):
        """iter through the trie."""
        for aset, _ in self._iter(self.root, []):
            yield aset

    @classmethod
    def _iter(cls, node, path):
        # type: (_T_NODE, list) -> typing.Generator[typing.Tuple[_T_KEYSET, _T_NODE]]
        if node.data is not None:
            path.append(node.data)
        if node.is_leaf:
            yield tuple(path), node
        for child in node.children.values():
            yield from cls._iter(child, path)
        if node.data is not None:
            path.pop()

    @classmethod
    def _add(cls, node: "_T_NODE", it: "_T_KEY_ITER") -> "_T_NODE":
        try:
            data = next(it)
        except StopIteration:  # end of set to add
            node.is_leaf = True
            return node
        else:
            nextnode = node.children.get(data)
            if not nextnode:
                nextnode = cls.Node(data)
                node.children[data] = nextnode
            return cls._add(nextnode, it)  # recurse

    def __contains__(self, aset: "_T_KEYSET_COMPITABLE") -> bool:
        """Check if the given set is in the trie."""
        node = self._get(self.root, self._to_keyset(aset))
        return node is not None and node.is_leaf

    @classmethod
    def _get(cls, node: "_T_NODE", it: "_T_KEY_ITER") -> "_T_NODE":
        try:
            data = next(it)
        except StopIteration:
            return node

        matchnode = node.children.get(data)
        if not matchnode:
            return None
        else:
            return cls._get(matchnode, it)

    def has_superset(self, aset: "_T_KEYSET_COMPITABLE") -> "bool":
        """Check if any set in the trie is superset of given aset."""
        return self._has_superset(self.root, sorted(set(aset)), 0)

    @classmethod
    def _has_superset(cls, node, setarr, idx):
        """(internal) Used by has_superset."""
        if idx > len(setarr) - 1:
            return True
        found = False
        for key, child in node.children.items():
            if key > setarr[idx]:
                break
            if key == setarr[idx]:
                found = cls._has_superset(child, setarr, idx + 1)
            else:
                found = cls._has_superset(child, setarr, idx)
            if found:
                break
        return found

    @classmethod
    def _iter_supersets(
        cls, node: "_T_NODE", setarr: "_T_KEYSET", idx: "int", path: "list"
    ) -> "typing.Generator[typing.Tuple[_T_KEYSET, _T_NODE]]":
        """(internal) for yielding supersets of a given setarr."""
        if node.data is not None:
            path.append(node.data)
        if node.is_leaf and idx > len(setarr) - 1:
            yield tuple(path), node

        if idx < len(setarr):
            for key, child in node.children.items():
                if key > setarr[idx]:
                    break
                if key == setarr[idx]:
                    yield from cls._iter_supersets(child, setarr, idx + 1, path)
                elif key < setarr[idx]:
                    yield from cls._iter_supersets(child, setarr, idx, path)
        else:
            # no more elements to find: just traverse this subtree to get
            # all supersets
            for child in node.children.values():
                yield from cls._iter_supersets(child, setarr, idx, path)

        if node.data is not None:
            path.pop()

    def has_subset(self, aset: "_T_KEYSET_COMPITABLE") -> "bool":
        """Check if any set in the trie is subset of given aset."""
        return self._has_subset(self.root, sorted(set(aset)), 0)

    @classmethod
    def _has_subset(cls, node: "_T_NODE", setarr: "_T_KEYSET", idx: "int"):
        """(internal) Used by has_subset."""
        if node.is_leaf:
            return True
        if idx >= len(setarr):
            return False

        found = False
        child = node.children.get(setarr[idx])
        if child:
            found = cls._has_subset(child, setarr, idx + 1)

        if not found:
            return cls._has_subset(node, setarr, idx + 1)
        else:
            return True

    @classmethod
    def _iter_subsets(
        cls, node: "_T_NODE", setarr: "_T_KEYSET", idx: "int", path: "list"
    ) -> "typing.Generator[typing.Tuple[_T_KEYSET, _T_NODE]]":
        if node.data is not None:
            path.append(node.data)
        if node.is_leaf:
            yield tuple(path), node
        for key, child in node.children.items():
            if idx >= len(setarr):
                break
            if key == setarr[idx]:
                yield from cls._iter_subsets(child, setarr, idx + 1, path)
            else:
                # advance in search set until we find child (or get to
                # the end, or get to an element > child)
                for jdx in range(idx + 1, len(setarr)):
                    if key < setarr[jdx]:
                        break
                    if key == setarr[jdx]:
                        yield from cls._iter_subsets(child, setarr, jdx, path)
                        break
        if node.data is not None:
            path.pop()

    @classmethod
    def _remove(cls, node, it):
        # type: (_T_NODE, _T_KEY_ITER) -> typing.Tuple[bool, _T_NODE]
        """(internal) for remove a node."""
        try:
            data = next(it)
        except StopIteration:
            if not node.is_leaf:
                return False, None
            else:
                node.is_leaf = False
                if node.children:
                    return False, node
                else:
                    return True, node

        matchnode = node.children.get(data)
        if not matchnode:
            return False, None
        else:
            recursive_del, node = cls._remove(matchnode, it)
            if recursive_del:
                node.children.pop(data)
                recursive_del &= len(node.children) == 0
            return recursive_del, node


class SetTrie(_SetTrie, typing.MutableSet[_KT]):
    """Set-trie container of sets for efficient supersets/subsets of a set
    over a set of sets queries."""

    Node = _SimpleNode

    def __init__(self, iterable=None):
        self.root = self.Node()
        if iterable is not None:
            for key in iterable:
                self.add(key)

    def __repr__(self):
        return f"<SetTrie with {len(self)} sets>"

    def add(self, aset: "_T_KEYSET_COMPITABLE") -> None:
        self._add(self.root, self._to_keyset(aset))

    def discard(self, aset: "_T_KEYSET_COMPITABLE"):
        self._remove(self.root, self._to_keyset(aset))

    def iter_supersets(self, aset):
        # type: (_T_KEYSET_COMPITABLE) -> typing.Generator[_T_KEYSET]
        """Visit each supersets of given aset in the trie."""
        for rset, _ in self._iter_supersets(self.root, sorted(set(aset)), 0, []):
            yield rset

    def iter_subsets(self, aset):
        # type: (_T_KEYSET_COMPITABLE) -> typing.Generator[_T_KEYSET]
        """Visit each subsets of given aset in the trie."""
        for rset, _ in self._iter_subsets(self.root, sorted(set(aset)), 0, []):
            yield rset


class SetTrieDict(_SetTrie, typing.MutableMapping[_KT, _VT]):
    """Mapping container for efficient storage of key-value pairs where the keys
    are sets.  Uses efficient trie implementation. Supports querying for values
    associated to subsets or supersets of stored key sets."""

    Node = _ValueNode

    __marker = object()

    def __init__(self, iterable=None):
        self.root = self.Node()
        if iterable is not None:
            for key, value in iterable:
                self.assign(key, value)

    def __repr__(self):
        return f"<SetTrieDict with {len(self)} sets>"

    def items(self) -> "typing.Generator[_T_KEYSET, _VT]":
        for aset, node in self._iter(self.root, []):
            yield aset, node.value

    def assign(self, akey: "_T_KEYSET_COMPITABLE", avalue: "_VT") -> None:
        self[akey] = avalue

    def __setitem__(self, akey: "_T_KEYSET_COMPITABLE", avalue: "_VT") -> None:
        node = self._add(self.root, self._to_keyset(akey))
        node.value = avalue

    def get(self, akey: "_T_KEYSET_COMPITABLE", default=None) -> "_VT":
        node = self._get(self.root, self._to_keyset(akey))
        if node is None or not node.is_leaf:
            return default
        return node.value

    def __getitem__(self, akey: "_T_KEYSET_COMPITABLE") -> "_VT":
        node = self._get(self.root, self._to_keyset(akey))
        if node is None or not node.is_leaf:
            return KeyError(akey)
        return node.value

    def __delitem__(self, akey: "_T_KEYSET_COMPITABLE"):
        _, node = self._remove(self.root, self._to_keyset(akey))
        if not node:
            raise KeyError(akey)

    def pop(self, akey: "_T_KEYSET_COMPITABLE", default: "_VT" = __marker) -> "_VT":
        _, node = self._remove(self.root, self._to_keyset(akey))
        if node:
            return node.value
        elif default is self.__marker:
            raise KeyError(akey)
        else:
            return default

    def iter_supersets(self, aset):
        # type: (_T_KEYSET_COMPITABLE) -> typing.Generator[typing.Tuple[_T_KEYSET, _VT]]
        """Visit each supersets of given aset in the trie."""
        for rset, node in self._iter_supersets(self.root, sorted(set(aset)), 0, []):
            yield rset, node.value

    def iter_subsets(self, aset):
        # type: (_T_KEYSET_COMPITABLE) -> typing.Generator[_T_KEYSET]
        """Visit each subsets of given aset in the trie."""
        for rset, node in self._iter_subsets(self.root, sorted(set(aset)), 0, []):
            yield rset, node.value
