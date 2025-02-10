# LiveCodeBench

Official repository: https://github.com/LiveCodeBench/LiveCodeBench

This is an unofficial modification of LiveCodeBench official repository to support execution-based evaluation of LiveCodeBench "codegeneration" subset. The goal was to keep a bare minimum code in this repository such that following style of evaluation are possible.

```pytholn
import subprocess
import sys

sample_file_path = "path_to_custom_model_outputs"


def install_from_git(git_url):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", git_url])
        print("Package installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")


if __name__ == "__main__":
    try:
        from livecodebench.evaluate import evaluate
    except ImportError:
        print("Package 'livecodebench' not found. Attempting to install...")
        install_from_git("git+https://github.com/wasiahmad/livecodebench.git")
        try:
            from livecodebench.evaluate import evaluate
        except ImportError:
            print("Failed to install 'livecodebench'. Please install it manually.")
            raise

    evaluate(sample_path)
```

The `sample_file` should include model outputs in the following format.

```
[
    {"question_id": "id1", "code_list": ["code1", "code2"]},
    {"question_id": "id2", "code_list": ["code1", "code2"]}
]
```
