import json
from datetime import datetime
from livecodebench.benchmarks import load_code_generation_dataset
from livecodebench.evaluation import extract_instance_results, codegen_metrics


def evaluate(
        custom_output_file: str,
        release_version: str = "release_latest",
):
    benchmark = load_code_generation_dataset(release_version)
    # benchmark = sorted(benchmark, key=lambda x: x.question_id)

    custom_outputs = dict()
    with open(custom_output_file, "r") as f:
        for line in f:
            output = json.loads(line)
            custom_outputs[output["question_id"]] = output

    assert len(custom_outputs) == len(benchmark), f"{len(custom_outputs)} != {len(benchmark)}"
    assert all(isinstance(custom_output, dict) for custom_output in custom_outputs.values())

    save_results, combined_results = [], []
    for instance in benchmark:
        custom_output = custom_outputs[instance.question_id]
        output = instance.insert_output(custom_output, custom_output)
        save_results.append(output)
        combined_results.append((custom_output, custom_output))

    eval_samples = [instance.get_evaluation_sample() for instance in benchmark]
    generations = [extracted for _, extracted in combined_results]
    metrics = codegen_metrics(
        eval_samples,
        generations,
        num_process_evaluate=12,
        timeout=6,
    )

    graded = extract_instance_results(metrics[1])

    metadatas = metrics[2]
    save_eval_results = [
        instance.insert_output_evaluation(
            outputs_list, extracted_list, graded_list, metadata=meta
        )
        for instance, (outputs_list, extracted_list), graded_list, meta in zip(
            benchmark, combined_results, graded, metadatas
        )
    ]

    # save_eval_results
    output_results = dict()
    output_results["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    for k in metrics[0]:
        if k.startswith("pass@"):
            print(f"{k}: {metrics[0][k]}")
            output_results[k] = metrics[0][k]
    output_results["eval"] = {r["question_id"]: r for r in save_eval_results}

    with open(custom_output_file[:-6] + "_eval_results.json", "w") as f:
        json.dump(output_results, f, indent=4)


def main():
    from fire import Fire

    Fire(evaluate)


if __name__ == "__main__":
    main()
