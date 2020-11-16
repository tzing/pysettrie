# Set trie

A trie data struct that is designed for set.

This implemented is optimized for query subsets, sets and supersets among a large batch of sets.

> **NOTE**
> This repo is re-implemented from [mmihaltz/pysettrie](https://github.com/mmihaltz/pysettrie).
> But API is **not** consistent with Márton's implementation.


## Usage

This code provides 2 kinds of implementation: `SetTrie` and `SetTrieDict`.

```py
In  []: import settrie

In  []: trie = settrie.SetTrie()  # use this as `set`
   ...: trie.add([1, 2, 4])
   ...: trie.add([1, 3])
   ...: trie.add([1, 3, 5])
   ...: trie.add([1, 4])

In  []: for aset in trie.iter_supersets( [1,3]):
   ...:     print(aset)
(1, 3)
(1, 3, 5)

In  []: trie = settrie.SetTrieDict()  # use this as `dict`
   ...: trie[1, 2, 4] = "A"
   ...: trie[1, 3] = "B"
   ...: trie[set([1, 3, 5])] = "C"  # type doesn't matter
   ...: trie[list([1, 4])] = "D"

In  []: for aset, key in trie.iter_subsets([1, 2, 4]):
   ...:     print(aset, key)
   ...:
(1, 2, 4) A
(1, 4) D

In  []: (1, 3) in trie
Out []: True

In  []: {1, 2, 3} in trie
Out []: False
```

Both `SetTrie` and `SetTrieDict` provides following members:
* `has_superset`
* `iter_supersets`
* `has_subset`
* `iter_subsets`

Also, they've fully integrated with Python's interface of `set` and `dict` respectively.


## Benchmark

A brief test is measured by using `benchmark/benchmark.py` on my Macbook Air 2019:

```
                      this repo           based
contains             1.0502 sec      8.6181 sec
has_superset        14.8069 sec     17.7916 sec
iter_supersets      26.9799 sec     29.9188 sec
has_subset           9.4474 sec     81.0500 sec
iter_subsets        70.0992 sec     75.4710 sec
```
