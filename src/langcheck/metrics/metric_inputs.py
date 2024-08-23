from __future__ import annotations

from typing import Union

import pandas as pd
from jinja2 import Environment, meta

SingleInputType = Union[str, list[str], None]


def _map_pairwise_input_to_list(
    input: tuple[SingleInputType, SingleInputType],
) -> tuple[list[str] | None, list[str] | None]:
    return (
        _map_single_input_to_list(input[0]),
        _map_single_input_to_list(input[1]),
    )


def _map_single_input_to_list(
    input: SingleInputType,
) -> list[str] | None:
    if input is None:
        return None
    elif isinstance(input, str):
        return [input]
    else:
        return input


class MetricInputs:
    """A helper class to handle the inputs for the metric in a consistent way."""

    def __init__(
        self,
        single_inputs: dict[str, SingleInputType],
        pairwise_inputs: dict[str, tuple[SingleInputType, SingleInputType]]
        | None = None,
        required_params: list[str] | None = None,
        optional_params: list[str] | None = None,
        input_record_mapping: dict[str, str] | None = None,
    ):
        """TODO"""
        # Instantiate the paramater lists if None
        self.required_params = required_params or []
        self.optional_params = optional_params or []

        self.single_inputs = {
            key: _map_single_input_to_list(value)
            for key, value in single_inputs.items()
        }

        if pairwise_inputs is None:
            self.pairwise_inputs = {}
        else:
            self.pairwise_inputs = {
                key: _map_pairwise_input_to_list(value)
                for key, value in pairwise_inputs.items()
            }

        self.input_record_mapping = input_record_mapping or {}

        all_input_keys = list(self.single_inputs.keys()) + list(
            self.pairwise_inputs.keys()
        )
        for input_key in all_input_keys:
            if input_key not in self.input_record_mapping:
                # Add mapping for the input key itself
                self.input_record_mapping[input_key] = input_key

        # Do the validation of parameters
        # Validate that single_inputs and pairwise_inputs are disjoint
        single_input_keys = set(self.single_inputs.keys())
        pairwise_input_keys = set(self.pairwise_inputs.keys())
        if not single_input_keys.isdisjoint(pairwise_input_keys):
            overlap_keys = single_input_keys.intersection(pairwise_input_keys)
            raise ValueError(
                "Single input keys and pairwise input keys should be disjoint."
                f" Overlapping keys: {overlap_keys}"
            )

        all_input_keys = list(self.single_inputs.keys()) + list(
            self.pairwise_inputs.keys()
        )

        # Check that all the required parameters are present
        missing_required_params = set(self.required_params) - set(
            all_input_keys
        )
        if missing_required_params:
            raise ValueError(
                f"Missing required parameters: {missing_required_params}"
            )

        # Validate the single inputs
        for single_input_key in single_input_keys:
            single_input = self.single_inputs[single_input_key]
            if (
                single_input_key in self.required_params
                and single_input is None
            ):
                raise ValueError(
                    f"Required parameter '{single_input_key}' is None."
                )
            elif single_input_key not in self.optional_params:
                raise ValueError(f"Unknown parameter '{single_input_key}'")

        # Validate the pairwise inputs
        for pairwise_input_key in pairwise_input_keys:
            pairwise_input_a, pairwise_input_b = self.pairwise_inputs[
                pairwise_input_key
            ]
            if pairwise_input_key in self.required_params:
                if pairwise_input_a is None or pairwise_input_b is None:
                    raise ValueError(
                        f"Required parameter '{pairwise_input_key}' is None."
                    )
            elif pairwise_input_key in self.optional_params:
                # Raise an error if only one of the inputs is None
                if (pairwise_input_a is None) ^ (pairwise_input_b is None):
                    raise ValueError(
                        f"Both inputs of '{pairwise_input_key}' should be None or not None."
                    )
            else:
                raise ValueError(f"Unknown parameter '{pairwise_input_key}'")

            # If to_df is called, each key is mapped into two columns: key_a and
            # key_b. Check that the key is not already used.
            df_key_a = pairwise_input_key + "_a"
            if df_key_a in all_input_keys:
                raise ValueError(
                    f"Key '{df_key_a} will be added as a dataframe column, but it is already used as a input key."
                )
            df_key_b = pairwise_input_key + "_b"
            if df_key_b in all_input_keys:
                raise ValueError(
                    f"Key '{df_key_b} will be added as a dataframe column, but it is already used as a input key."
                )

        # Validate the lengths of the inputs
        input_lengths: set[int] = set()
        for key in self.single_inputs:
            single_input = self.single_inputs[key]
            if single_input is not None:
                input_lengths.add(len(single_input))

        for key in self.pairwise_inputs:
            pairwise_input_a, pairwise_input_b = self.pairwise_inputs[key]
            if pairwise_input_a is not None:
                input_lengths.add(len(pairwise_input_a))
            if pairwise_input_b is not None:
                input_lengths.add(len(pairwise_input_b))

        if len(input_lengths) > 1:
            single_input_lengths = "\n".join(
                f"{key}: {len(value)}"
                for key, value in self.single_inputs.items()
                if value is not None
            )

            pairwise_input_lengths = "\n".join(
                f"{key}: ({len(value[0])}, {len(value[1])})"
                for key, value in self.pairwise_inputs.items()
                if value[0] is not None and value[1] is not None
            )

            raise ValueError(
                f"All inputs should have the same length.\n {single_input_lengths}\n{pairwise_input_lengths}"
            )

        self.input_length = input_lengths.pop()
        if self.input_length == 0:
            raise ValueError("All inputs should have at least one element.")

        # Validate the mapping to prompt variables
        self.input_record_to_arg = {}

        for single_input_key in single_input_keys:
            input_record_name = self.input_record_mapping[single_input_key]
            if input_record_name in self.input_record_to_arg:
                raise ValueError(
                    f"Input record attribute '{input_record_name}' is mapped from multiple arguments: "
                    f"{self.input_record_to_arg[input_record_name]} and {single_input_key}"
                )

            self.input_record_to_arg[input_record_name] = single_input_key

        for pairwise_input_key in pairwise_input_keys:
            input_record_name_single = self.input_record_mapping[
                pairwise_input_key
            ]
            input_record_names = [
                input_record_name_single + "_a",
                input_record_name_single + "_b",
            ]

            for input_record_name in input_record_names:
                if input_record_name in self.input_record_to_arg:
                    raise ValueError(
                        f"Input record attribute '{input_record_name}' is mapped from multiple arguments: "
                        f"{self.input_record_to_arg[input_record_name]} and {pairwise_input_key}"
                    )

                self.input_record_to_arg[input_record_name] = pairwise_input_key

    def get_input_records(
        self, swap_pairwise: bool = False
    ) -> list[dict[str, str | None]]:
        """TODO"""
        input_records: list[dict[str, str | None]] = []
        for i in range(self.input_length):
            input_record = {}
            for single_key in self.single_inputs:
                single_input = self.single_inputs[single_key]
                single_var_key = self.input_record_mapping[single_key]
                if single_input is None:
                    input_record[single_var_key] = None
                else:
                    input_record[single_var_key] = single_input[i]

            for pairwise_key in self.pairwise_inputs:
                pairwise_input_a, pairwise_input_b = self.pairwise_inputs[
                    pairwise_key
                ]
                if swap_pairwise:
                    pairwise_input_a, pairwise_input_b = (
                        pairwise_input_b,
                        pairwise_input_a,
                    )
                input_record_key_a = (
                    self.input_record_mapping[pairwise_key] + "_a"
                )
                if pairwise_input_a is None:
                    input_record[input_record_key_a] = None
                else:
                    input_record[input_record_key_a] = pairwise_input_a[i]
                input_record_key_b = (
                    self.input_record_mapping[pairwise_key] + "_b"
                )
                if pairwise_input_b is None:
                    input_record[input_record_key_b] = None
                else:
                    input_record[input_record_key_b] = pairwise_input_b[i]
            input_records.append(input_record)

        return input_records

    def to_df(self) -> pd.DataFrame:
        """Convert the inputs to a DataFrame."""
        if self.input_length is None:
            raise ValueError(
                "Please run `validate` before calling this method."
            )
        input_lists = {}
        for single_key in self.single_inputs:
            single_input = self.single_inputs[single_key]
            if single_input is None:
                input_lists[single_key] = [None] * self.input_length
            else:
                input_lists[single_key] = single_input

        for pairwise_key in self.pairwise_inputs:
            pairwise_input_a, pairwise_input_b = self.pairwise_inputs[
                pairwise_key
            ]
            if pairwise_input_a is None:
                input_lists[pairwise_key + "_a"] = [None] * self.input_length
            else:
                input_lists[pairwise_key + "_a"] = pairwise_input_a

            if pairwise_input_b is None:
                input_lists[pairwise_key + "_b"] = [None] * self.input_length
            else:
                input_lists[pairwise_key + "_b"] = pairwise_input_b

        return pd.DataFrame(input_lists)

    def get_input_list(
        self, key: str
    ) -> tuple[list[str] | None, list[str] | None] | list[str] | None:
        """Get the input list for the key."""
        if key in self.single_inputs:
            return self.single_inputs[key]
        elif key in self.pairwise_inputs:
            return self.pairwise_inputs[key]
        else:
            raise ValueError(f"Unknown key: {key}")

    def validate_template(self, template_src: str):
        """TODO"""
        # Validate the expected parameters in the prompt template
        env = Environment()
        expected_params = meta.find_undeclared_variables(
            env.parse(template_src)
        )

        allowed_params = self.input_record_to_arg.keys()
        assert all(
            param in allowed_params for param in expected_params
        ), f"The prompt template contains invalid parameters. The allowed parameters are {allowed_params} but the prompt template expects the parameters {expected_params}"

        for param in expected_params:
            arg_key = self.input_record_to_arg[param]
            if arg_key in self.single_inputs:
                assert (
                    self.single_inputs[arg_key] is not None
                ), f'The prompt template expects the parameter "{param}" but it is not provided.'
            else:
                pairwise_inputs_a, _ = self.pairwise_inputs[arg_key]
                # It is already validated that both inputs are None or not None
                assert (
                    pairwise_inputs_a is not None
                ), f'The prompt template expects the parameter "{param}" but it is not provided.'
