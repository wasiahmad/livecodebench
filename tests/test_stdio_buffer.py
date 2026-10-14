"""Stdin/stdout handling of the stdio judge (grade_stdio via check_correctness).

Solutions may read input through sys.stdin.buffer and write through sys.stdout.buffer, as they
would against a real interpreter. Text-mode access must keep working unchanged.
"""

import json

import pytest

from livecodebench.evaluation.code_generation_metrics import check_correctness

# Two test cases per program, so state must reset between calls.
INPUTS = ["3\n1\n2\n3\n", "2\n5\n7\n"]
OUTPUTS = ["6\n", "12\n"]

PROGRAMS = {
    # binary stdin
    "buffer_read": "import sys\ndata = sys.stdin.buffer.read().split()\nprint(sum(map(int, data[1:])))\n",
    "buffer_readline": (
        "import sys\ninput = sys.stdin.buffer.readline\nn = int(input())\n"
        "print(sum(int(input()) for _ in range(n)))\n"
    ),
    "buffer_readlines": "import sys\nlines = sys.stdin.buffer.readlines()\nprint(sum(map(int, lines[1:])))\n",
    "buffer_iter": (
        "import sys\nit = iter(sys.stdin.buffer)\nn = int(next(it))\n"
        "print(sum(int(next(it)) for _ in range(n)))\n"
    ),
    # binary stdout, interleaved with text writes
    "stdout_buffer": (
        "import sys\nn, *xs = map(int, sys.stdin.read().split())\n"
        "sys.stdout.buffer.write(str(sum(xs)).encode())\nsys.stdout.write('\\n')\n"
    ),
    # text paths that must keep working
    "input": "n = int(input())\nprint(sum(int(input()) for _ in range(n)))\n",
    "stdin_read": "import sys\nprint(sum(map(int, sys.stdin.read().split()[1:])))\n",
    "stdin_readline": (
        "import sys\nn = int(sys.stdin.readline())\n"
        "print(sum(int(sys.stdin.readline()) for _ in range(n)))\n"
    ),
    "stdin_iter": "import sys\nlines = [l for l in sys.stdin if l.strip()]\nprint(sum(map(int, lines[1:])))\n",
}


def grade(code, inputs=INPUTS, outputs=OUTPUTS):
    sample = {"input_output": json.dumps({"inputs": inputs, "outputs": outputs, "fn_name": None})}
    result, metadata = check_correctness(sample, code, 6, debug=False, language="python")
    return bool(result) and all(r is True for r in result), metadata


@pytest.mark.parametrize("name", sorted(PROGRAMS))
def test_stdio_program_passes(name):
    ok, metadata = grade(PROGRAMS[name])
    assert ok, metadata


def test_stdout_buffer_preserves_order():
    code = "import sys\nprint('a')\nsys.stdout.buffer.write(b'b\\n')\nsys.stdout.write('c\\n')\n"
    ok, metadata = grade(code, inputs=[""], outputs=["a\nb\nc\n"])
    assert ok, metadata


def test_wrong_answer_still_fails():
    ok, _ = grade("print(0)\n")
    assert not ok
