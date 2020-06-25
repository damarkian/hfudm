from typing import Iterable, Optional, List, Tuple
import copy
import numpy as np
import json
from scipy.linalg import expm

def swap_forward(iterable_item: Iterable,
                 starting_index: Optional[int] = 0):
    new_sequence = copy.deepcopy(iterable_item)
    for i in range(starting_index, len(iterable_item) - 1, 2):
        new_sequence[i + 1], new_sequence[i] = \
            new_sequence[i], new_sequence[i + 1]
    return new_sequence

def test_swap_forward():
    list_to_swap = list(range(6))
    test_swapped_list = swap_forward(list_to_swap, starting_index=0)
    assert test_swapped_list == [1, 0, 3, 2, 5, 4]

    test_swapped_list = swap_forward(list_to_swap, starting_index=1)
    assert test_swapped_list == [0, 2, 1, 4, 3, 5]


def hiddenhello():
    message = "Hi There"

    message_dict = {}
    message_dict["message"] = message
    message_dict["schema"] = "message"

    with open("hiddenhello.json",'w') as f:
        f.write(json.dumps(message_dict, indent=2)) # Write message to file as this will serve as output artifact
