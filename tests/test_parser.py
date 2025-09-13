from gamebox import classify_event

def test_hit_double():
    ev = classify_event("2B")
    assert ev.is_batter_event and not ev.is_runner_event
    assert ev.is_ab and ev.hit == "2B"
    assert not ev.walk and not ev.so
    assert ev.home_run_allowed is False

def test_groundout_path():
    ev = classify_event("G6-3")
    assert ev.is_batter_event and ev.is_ab
    assert ev.field_path == [6,3]

def test_error_reach():
    ev = classify_event("E5")
    assert ev.is_batter_event and ev.is_ab
    assert ev.roe == 5 and ev.errors_on_play == 1

def test_hr_modifiers():
    ev = classify_event("HR+RBI(3)")
    assert ev.hit == "HR" and ev.explicit_rbis == 3 and ev.home_run_allowed

def test_runner_cs():
    ev = classify_event("CS3-25")
    assert ev.is_runner_event and not ev.is_batter_event

def test_advances_parse():
    ev = classify_event("1B+ROE(5)", advances_str="B-1;B-2(E5)")
    assert ev.advances == [("B","1",None), ("B","2","E5")]
    assert ev.errors_on_play == 1 and ev.roe == 5
