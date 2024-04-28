from collections import Counter
from datasets import load_dataset
from api_comm import APICommunication, ExtendedUnittest
import argparse
import os

def add_exec_outcome(example):

    language = example['lang']
    # please note the `lang` is not `lang_cluster` since the executor needs a specific version of the programming language,
    # the supported version of `lang` is indicated in inference code.

    source_code = example['source_code'] # the code you use to run
    hidden_unit_tests = eval(example['testcases'])

    unittests = []
    for hidden_unit_test in hidden_unit_tests:
        unittests.append(
            ExtendedUnittest(
                input=hidden_unit_test['input'],
                output=hidden_unit_test['output']
            ).json()
        )

    api = APICommunication()
    response = api.execute_code(
        language=language,
        source_code=source_code,
        unittests=unittests
    )
    print(response)

    var_example = [{'exec_outcome': 'COMPILATION_ERROR', 'input': '', 'output': [], 'result': ''}]
    example['exec_outcome'] = response[0] if isinstance(response[0],list) else var_example

    return example

def main(args):
    dataset = load_dataset('json', split='train', data_files=os.path.join(args.codes_dir,args.code_filename))
    dataset = dataset.map(add_exec_outcome)

    lang_counts = Counter(dataset['lang'])
    for lang, count in lang_counts.items():
        print(f'{lang}: {count}')

    lang_cluster_counts = Counter(dataset['lang_cluster'])
    for lang_cluster, count in lang_cluster_counts.items():
        print(f'{lang_cluster}: {count}')

    dataset.to_json(os.path.join(args.results_dir,args.code_filename), lines=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--codes_dir', type=str, default='../../program_synthesis/inference/results', help='The folder where you store your code files')
    parser.add_argument('--results_dir', type=str, default='../../program_synthesis/execute_results', help='The folder where you store your run results')
    parser.add_argument('--code_filename', type=str, default='program_synthesis_eval_palm.jsonl', help='code data')

    args = parser.parse_args()
    main(args)
