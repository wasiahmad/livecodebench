import json
import os
import zipfile
from dataclasses import dataclass, field, fields
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class Platform(Enum):
    CODEFORCES = "codeforces"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Test:
    input: str
    output: str


@dataclass
class CodeGenerationProblem:
    platform: Platform
    problem_id: str
    problem_title: str
    problem_statement: str
    link: str
    time_limit: int
    memory_limit: int
    difficulty: Difficulty
    language: str

    _zip_path: Path = field(repr=False)
    _cached_test_cases: Optional[List[Test]] = field(default=None, repr=False)

    def __post_init__(self):
        if isinstance(self.platform, str):
            self.platform = Platform(self.platform)
        if isinstance(self.difficulty, str):
            self.difficulty = Difficulty(self.difficulty)

    @property
    def test_cases(self) -> List[Test]:
        """Lazy loads test cases from the zip file only when accessed."""
        if self._cached_test_cases is not None:
            return self._cached_test_cases

        loaded_tests = []
        try:
            with zipfile.ZipFile(self._zip_path, "r") as zip_ref:
                all_files = set(zip_ref.namelist())

                input_files = [
                    f
                    for f in all_files
                    if f.startswith("testdata/") and f.endswith(".in")
                ]

                for in_file in sorted(input_files):
                    expected_ans = in_file[:-3] + ".ans"
                    if expected_ans in all_files:
                        with zip_ref.open(in_file) as f:
                            in_txt = f.read().decode("utf-8", errors="replace")
                        with zip_ref.open(expected_ans) as f:
                            ans_txt = f.read().decode("utf-8", errors="replace")

                        loaded_tests.append(Test(input=in_txt, output=ans_txt))

        except Exception as e:
            print(f"Error reading zip for problem {self.problem_id}: {e}")

        self._cached_test_cases = loaded_tests
        return self._cached_test_cases

    def insert_output(self, output_list: list[str], code_list: list[str]) -> dict:
        return {
            "platform": self.platform.value,
            "problem_id": self.problem_id,
            "problem_title": self.problem_title,
            "problem_statement": self.problem_statement,
            "link": self.link,
            "time_limit": self.time_limit,
            "memory_limit": self.memory_limit,
            "difficulty": self.difficulty.value,
            "output_list": output_list,
            "code_list": code_list,
            "language": self.language,
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
                    "inputs": [t.input for t in self.test_cases],
                    "outputs": [t.output for t in self.test_cases],
                }
            ),
        }


def index_zip_files(directory_path: Path) -> Dict[str, Path]:
    target_dir = Path(directory_path)
    if not target_dir.exists():
        print(f"Test directory not found: {target_dir}")
        return {}
    print("Indexing zip files...")
    return {p.stem: p for p in target_dir.glob("*.zip")}


def load_code_generation_dataset_from_file(
    filepath, language, test_dir
) -> List[CodeGenerationProblem]:
    zip_index = index_zip_files(Path(test_dir))

    dataset = []
    init_fields = {
        f.name
        for f in fields(CodeGenerationProblem)
        if f.name not in ["_zip_path", "_cached_test_cases"]
    }

    print(f"Loading problems from {filepath}...")
    skipped_count = 0

    with open(filepath, "r") as f:
        for line in f:
            if not line.strip():
                continue
            p = json.loads(line)

            p_id = str(p.get("problem_id", ""))
            zip_path = zip_index.get(p_id)
            if not zip_path:
                skipped_count += 1
                continue

            filtered_p = {key: value for key, value in p.items() if key in init_fields}
            try:
                problem = CodeGenerationProblem(
                    **filtered_p, language=language, _zip_path=zip_path
                )
                dataset.append(problem)
            except Exception as e:
                print(f"Error initializing problem {p_id}: {e}")

    print(f"Loaded {len(dataset)} problems.")
    if skipped_count > 0:
        print(
            f"⚠️  Skipped {skipped_count} problems because their .zip file was missing."
        )

    return dataset


if __name__ == "__main__":
    # Example paths
    jsonl_path = (
        "/home/wahmad/Desktop/workspace/ns-data/livecodebench-pro/test_25q1.jsonl"
    )
    test_zip_dir = "/home/wahmad/Desktop/workspace/ns-data/livecodebench-pro/testcases"

    if os.path.exists(jsonl_path) and os.path.isdir(test_zip_dir):
        problems = load_code_generation_dataset_from_file(
            filepath=jsonl_path, language="python", test_dir=test_zip_dir
        )
        if problems:
            print(f"Example Problem: {problems[0].problem_id}")
            print(f"Test cases loaded: {len(problems[0].test_cases)}")
            print(f"First Input: {problems[0].test_cases[0].input[:50]}...")
