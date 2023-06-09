#!/usr/bin/env python3
# 
# Copyright    2023  Xiaomi Corp.        (authors: Yifan Yang)
#
# See ../../../../LICENSE for clarification regarding multiple authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Usage:
python ./show_wers.py \
    --start-epoch 21 \
    --end-epoch 40 \
    --decoding-method greedy_search \
    --exp-names exp_960 \
    --dataset "test-clean test-other"
"""
import os
import argparse


class AttributeDict(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(f"No such attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
            return
        raise AttributeError(f"No such attribute '{key}'")


def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--start-epoch",
        type=int,
        default=20,
    )

    parser.add_argument(
        "--end-epoch",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--start-avg",
        type=int,
        default=-1,
    )

    parser.add_argument(
        "--end-avg",
        type=int,
        default=99999,
    )

    parser.add_argument(
        "--decoding-method",
        type=str,
        default="greedy_search",
        help="""Possible values are:
          - greedy_search
          - beam_search
          - modified_beam_search
          - fast_beam_search
          - fast_beam_search_LG
          - fast_beam_search_nbest
          - fast_beam_search_nbest_oracle
          - fast_beam_search_nbest_LG
        """,
    )

    parser.add_argument(
        "--metrics",
        type=str,
        default="WER",
        help="""Possible values are:
          - WER
          - PER
        """,
    )

    parser.add_argument(
        "--exp-names",
        type=str,
        default="exp",
        help="""If there are more than one,
        please separate them with spaces,
        e.g 'exp_100 exp_960'
        """
    )

    parser.add_argument(
        "--dataset",
        type=str,
        default="test-clean test-other",
        help="""If there are more than one,
        please separate them with spaces,
        e.g 'dev test'
        """
    )

    return parser


def get_params():
    params = AttributeDict()

    return params

def main():
    parser = get_parser()
    args = parser.parse_args()

    params = get_params()
    params.update(vars(args))

    assert params.start_epoch > 1, params.start_epoch
    datasets = params.dataset.split()
    metrics = params.metrics

    os.system("rm missed.txt")
    for exp_dir_path in params.exp_names.split(" ", -1):
        os.system(f"rm wers_{exp_dir_path}.txt")
        dir_path = os.path.join(exp_dir_path, params.decoding_method)
        for dataset in datasets:
            for epoch in range(params.start_epoch, params.end_epoch + 1):
                for avg in range(1, 21):
                    if os.system(f"cat {dir_path}/{metrics.lower()}-summary-{dataset}-epoch-{epoch}-avg-{avg}-beam-10.0-max-contexts-8-max-states-64-use-averaged-model.txt | grep beam_10.0_max_contexts_8_max_states_64 | sed 's/beam_10.0_max_contexts_8_max_states_64/{params.decoding_method}/g' >> wers_{exp_dir_path}.txt"):
                        with open("missed.txt", "a") as f:
                            f.write(f"{exp_dir_path} {epoch} {avg}\n")
                    else:
                        os.system(f"echo '{dataset} {epoch} {avg}' >> wers_{exp_dir_path}.txt")

    for exp_dir_path in params.exp_names.split(" ", -1):
        data = {}
        with open(f"wers_{exp_dir_path}.txt") as f:
            l = f.readlines()
        for i in l:
            i = i.rstrip()
            if datasets[0] in i or datasets[1] in i:
                i = i.split(" ", -1)
                d, e, a = i[0], i[1], i[2]
                data[f"{e}-{a}-{d}"] = float(res)
            else:
                i = i.split(f"{params.decoding_method}", -1)
                res = i[1].strip()

        sorted_data = {}
        print("###", exp_dir_path)
        print(f"| {datasets[0]} & {datasets[1]} | sum | config |")
        print("| --- | --- | --- | ")
        for i in range(params.start_epoch, params.end_epoch + 1):
            for j in range(1, 21):
                c = data[f"{i}-{j}-{datasets[0]}"]
                o = data[f"{i}-{j}-{datasets[1]}"]
                s = c + o
                res = str(c) + " & " + str(o)
                ll = "| " + res + " | " + f"{s:.2f}" + " | " + f"epoch {i} avg {j} |"
                sorted_data[ll] = s

        for i, j in sorted(sorted_data.items(), key=lambda x:x[1]):
            print(i)


if __name__ == "__main__":
    main()
