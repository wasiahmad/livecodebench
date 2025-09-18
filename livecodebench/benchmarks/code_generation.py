import json
import zlib
import pickle
import base64
from enum import Enum
from datasets import load_dataset
from dataclasses import dataclass, fields


class TestType(Enum):
    STDIN = "stdin"
    FUNCTIONAL = "functional"


@dataclass
class Test:
    input: str
    output: str
    testtype: TestType

    def __post_init__(self):
        self.testtype = TestType(self.testtype)


@dataclass
class CodeGenerationProblem:
    question_id: str
    task: str
    public_test_cases: list[Test]
    private_test_cases: list[Test]

    def __post_init__(self):
        if self.public_test_cases:
            self.public_test_cases = json.loads(self.public_test_cases)  # type: ignore
            self.public_test_cases = [Test(**t) for t in self.public_test_cases]
        else:
            self.public_test_cases = []

        try:
            self.private_test_cases = json.loads(self.private_test_cases)  # type: ignore
        except:
            self.private_test_cases = json.loads(
                pickle.loads(
                    zlib.decompress(
                        base64.b64decode(self.private_test_cases.encode("utf-8"))  # type: ignore
                    )
                )
            )  # type: ignore
        self.private_test_cases = [Test(**t) for t in self.private_test_cases]

        self.metadata = json.loads(self.metadata)  # type: ignore

    def insert_output(self, output_list: list[str], code_list: list[str]) -> dict:
        return {
            "question_id": self.question_id,
            "task": self.task,
            "output_list": output_list,
            "code_list": code_list
        }

    def insert_output_evaluation(
            self,
            output_list: list[str],
            code_list: list[str],
            graded_list: list[bool],
            **kwargs,
    ) -> dict:
        output = self.insert_output(output_list, code_list)
        output["graded_list"] = graded_list
        output["pass@1"] = graded_list.count(True) / len(graded_list)
        for k, v in kwargs.items():
            output[k] = v
        return output

    def get_evaluation_sample(self):
        return {
            "input_output": json.dumps(
                {
                    "inputs": [
                        t.input
                        for t in self.public_test_cases + self.private_test_cases
                    ],
                    "outputs": [
                        t.output
                        for t in self.public_test_cases + self.private_test_cases
                    ],
                    "fn_name": self.metadata.get("func_name", None),
                }
            ),
        }


def load_code_generation_dataset() -> list[CodeGenerationProblem]:
    dataset = load_dataset("livebench/coding", split="test", trust_remote_code=True)
    valid_keys = {f.name for f in fields(CodeGenerationProblem)}
    filtered_dataset = []
    for p in dataset:
        filtered_p = {key: value for key, value in p.items() if key in valid_keys}
        problem = CodeGenerationProblem(**filtered_p)
        filtered_dataset.append(problem)
    print(f"Loaded {len(filtered_dataset)} problems")
    return filtered_dataset
