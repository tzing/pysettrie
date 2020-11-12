import pathlib
import sys
import timeit

BASEDIR = pathlib.Path(__file__).resolve().parent
sys.path.append(BASEDIR.parent.as_posix())

SCRIPT_SETUP = """
import pickle
import settrie

with open("%(filename)s", "rb") as fp:
    asets = pickle.load(fp)

trie = settrie.SetTrie()
for aset in asets:
    trie.add(aset)
""" % {
    "filename": BASEDIR / "data.pickle"
}

SCRIPT_CONTAINS = """\
[144008, 150010, 422353, 148004, 148036, 148046, 148133, 10008, 25137, 41003, 42003] in trie
[144008, 150010, 422353, 148004, 148036, 148046, 148133, 10008, 25137, 41003] in trie
[144008, 150010, 422353, 148004, 148036, 148046, 148133, 10008, 25137, 41003, 42003, 9999] in trie
"""

BENCHMARK_HAS_SUPERSET = """
trie.has_superset([140002, 142027, 111600, 111602, 536546, 111603, 111601, 190978, 148004, 148046, 148133, 10008, 41003, 42000])
"""

BENCHMARK_ITER_SUPERSETS = """
for _ in trie.iter_supersets([140002, 142027, 111600, 111602, 536546, 111603, 111601, 190978, 148004, 148046, 148133, 10008, 41003, 42000]):
    ...
"""

LARGE_SET = """700931, 705031, 150544, 42003, 702997, 704534, 700955, 700446, 704545, 148004, 704548, 861222, 703014, 113704, 20020, 861240, 20028, 864318, 702530, 148036, 702532, 700488, 148042, 701522, 22103, 121432, 701019, 700001, 701541, 704103, 704104, 701548, 704114, 703607, 702075, 700029, 187005, 704134, 704135, 188038, 701072, 701079, 700570, 705179, 105630, 704676, 704164, 188070, 703140, 148133, 106660, 703148, 700077, 701104, 121528, 188114, 141011, 861910, 188118, 188119, 704220, 703712, 700644, 841957, 863464, 780008, 702700, 140012, 780013, 842479, 701681, 841971, 106230, 705271, 704247, 863993, 705272, 700163, 703236, 705285, 702728, 703241, 704783, 121105, 701720, 780058, 702746, 704287, 188199, 106280, 121131, 701231, 860979, 701751, 703801, 704827, 704318, 701247, 702786, 8005, 863572, 199001, 700762, 700764, 700765, 703325, 860004, 186217, 700786, 862580, 702328, 860029, 700288, 184194, 700805, 700926, 197003, 701342, 703391, 112033, 702881, 700834, 864167, 860584, 704947, 701878, 139703, 139704, 139705, 701368, 701883, 701366, 190905, 700863, 702914, 701379, 704968, 704976, 703953, 704978, 704503, 701907, 121813, 703958, 703961, 702433, 863203, 703460, 101349, 702438, 860654, 300015, 702962, 705011, 111604, 704501, 111606, 111607, 148474, 705022"""

BENCHMARK_HAS_SUBSET = "trie.has_subset([%s])" % LARGE_SET

BENCHMARK_ITER_SUBSETS = """
for _ in trie.iter_subsets([{set}]):
    ...
""".format(
    set=LARGE_SET
)


def main():
    print("Benchmark")

    # test contains
    print("  contains           ", end="", flush=True)
    print(
        "%.4f sec"
        % timeit.timeit(setup=SCRIPT_SETUP, stmt=SCRIPT_CONTAINS, number=100000)
    )

    # test has superset
    print("  has_superset       ", end="", flush=True)
    print(
        "%.4f sec"
        % timeit.timeit(setup=SCRIPT_SETUP, stmt=BENCHMARK_HAS_SUPERSET, number=100000)
    )

    # test iter supersets
    print("  iter_supersets     ", end="", flush=True)
    print(
        "%.4f sec"
        % timeit.timeit(
            setup=SCRIPT_SETUP, stmt=BENCHMARK_ITER_SUPERSETS, number=100000
        )
    )

    # test has subset
    print("  has_subset         ", end="", flush=True)
    print(
        "%.4f sec"
        % timeit.timeit(setup=SCRIPT_SETUP, stmt=BENCHMARK_HAS_SUBSET, number=100000)
    )

    # test iter subset
    print("  iter_subsets       ", end="", flush=True)
    print(
        "%.4f sec"
        % timeit.timeit(setup=SCRIPT_SETUP, stmt=BENCHMARK_ITER_SUBSETS, number=100000)
    )


if __name__ == "__main__":
    exit(main())
