#!/usr/bin/env python3
import wrapper
import os.path
import unittest
import json
import traceback
from copy import deepcopy


TEST_DIRECTORY = os.path.dirname(__file__)

################################################################################
################################################################################
# Tests

class Test_1_AnimalMovement(unittest.TestCase):

    def test_01(self): verify_case('1-1')

    def test_02(self): verify_case('1-2')

    def test_03(self): verify_case('1-3')

    def test_04(self): verify_case('1-4')

    # This test case is a tiny grid, so doesn't render well in the UI
    def test_05(self): verify_case('1-5')


class Test_2_KeeperPlacement(unittest.TestCase):

    def test_01(self): 
        verify_case('2-1a')
        verify_case('2-1b')

    def test_02(self): 
        verify_case('2-2a')
        verify_case('2-2b')

    def test_03(self): 
        verify_case('2-3a')
        verify_case('2-3b')

    def test_04(self): 
        verify_case('2-4a')
        verify_case('2-4b')

    def test_05(self): 
        verify_case('2-5a')
        verify_case('2-5b')


class Test_3_Feeding(unittest.TestCase):

    def test_01(self): verify_case('3-1')

    def test_02(self): verify_case('3-2')

    def test_03(self): verify_case('3-3')

    def test_04(self): verify_case('3-4')

    def test_05(self): verify_case('3-5')


# End of test cases.
################################################################################
################################################################################


################################################################################
################################################################################
# Test setup from here on.

def almost_equal(result, expected, delta=.001):
    """ Determines if two unique_order tuples are truly equal 
    (within a delta for numbers). 
    """
    if len(result) != len(expected):
        raise AssertionError("\nIncorrect formation dictionary keys:\nExpected: \n" 
                                + str(len(expected)) + " keys"
                                + "\nGot:\n" 
                                + str(len(result)) + " keys")

    for i, j in zip(result, expected):
        if isinstance(j, (int, float)) and isinstance(i, (int, float)) and abs(i-j) > delta:
            return False
        elif isinstance(i, str) and i != j:
            return False
        elif j is None:
        	return i is None
    return True

def compare_formations(result_formations, expected_formations):
    """ Hashes the formations for comparison with == """
    if len(result_formations) != len(expected_formations):
        return False

    result_formations_list = unique_order(result_formations)
    expected_formations_list = unique_order(expected_formations)
    return all((almost_equal(result, expected)
                for result, expected in zip(result_formations_list, expected_formations_list)))

def unique_order(formations):
    result = []
    for form in formations:
        if "aim_dir" in form: 
            t = (*tuple(form["loc"]), *tuple(form["size"]), form["texture"], *tuple(form.get("aim_dir", [None]) or [None]))
        else: 
            t = (*tuple(form["loc"]), *tuple(form["size"]), form["texture"])
        result.append(t)
    return sorted(result)

def pretty_str(formations):
    def dictify(form):
        d = {"loc": tuple(form["loc"]), 
             "size": tuple(form["size"]), 
             "texture": form["texture"]}
        if "aim_dir" in form:
            d["aim_dir"] = form["aim_dir"]
        return d
    sorted_f = sorted([dictify(form) for form in formations], 
                          key=lambda f: (*f["loc"], *f["size"], f["texture"]))
    prettied = "\n"
    for f in sorted_f:
        prettied += str(f)
        prettied += "\n"
    return prettied

def verify_render(result, expected):
    assert set(result) == set(expected)

    # Check for an in-game exception
    if "error" in result:
        return result["error"] == expected["error"]

    if not compare_formations(result['formations'], expected['formations']):
        raise AssertionError("\nIncorrect set of formations:\nExpected: \n" 
                                + pretty_str(expected['formations']) 
                                + "\nGot:\n" 
                                + pretty_str(result['formations']))

    for attr in ('money', 'status', 'num_allowed_remaining'):
        assert result[attr] == expected[attr], "\nIncorrect \"{}\" value:\nExpected {}.\nGot {}.".format(attr, expected[attr], result[attr])

    return True

def verify_replay(result_trace, expected_trace):
    assert len(result_trace) == len(expected_trace)
    for result, expected in zip(result_trace, expected_trace):
        assert verify_render(result, expected)

def verify(result, input_data, gold):
    restype, result = result

    if restype == "error":
        return False, "raised an error: {}".format(result)

    try:
        test_type = input_data["type"]
        verifn = {"replay": verify_replay}[test_type]
        errmsg = verifn(result, gold)

        if errmsg is not None:
            return False, errmsg
        else:
            return True, "is correct. Hooray!"
    except:
        traceback.print_exc()
        return False, "crashed :(. Stack trace is printed above so you can debug."

def read_input_file(cname):
    with open(os.path.join('cases', cname+'.in'), 'r') as f:
        indata = json.loads(f.read())
    assert {"type", "map", "events", "money", "num_allowed_unfed",
            "spawn_interval", "animal_speed"}.issubset(set(indata.keys()))
    indata["events"] = [tuple(event) if isinstance(event, list) else event for event in indata["events"]]
    return indata

def read_output_file(cname):
    with open(os.path.join('cases', cname+'.out'), 'r') as f:
        outdata = json.loads(f.read())

    # If there's no exception, compare the render outputs
    for render_dict in outdata:
        if "error" in render_dict:
            continue
        for formation in render_dict["formations"]:
            formation["loc"] = tuple(formation["loc"])
            formation["size"] = tuple(formation["size"])
            if "aim_dir" in formation:
                formation["aim_dir"] = tuple(formation["aim_dir"]) if formation["aim_dir"] else None

    return outdata

def verify_case(cname):
    # read .in and .out files from cases
    indata = read_input_file(cname)
    outdata = read_output_file(cname)

    # first run the test
    result = wrapper.run_test(deepcopy(indata))

    # then run the verifier
    vresult, vmsg = verify(result, deepcopy(indata), deepcopy(outdata))

    # if failure, alert the test system
    if not vresult:
        raise AssertionError(vmsg)


if __name__ == '__main__':
    res = unittest.main(verbosity=3, exit=False)
