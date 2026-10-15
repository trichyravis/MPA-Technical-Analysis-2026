"""Offline Streamlit integration tests; no provider requests or account required."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]


def test_demo_app_and_replay_render_without_exceptions():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
    assert not app.exception
    assert len(app.metric)==5
    toggle=next(x for x in app.checkbox if x.label=='Historical replay')
    toggle.check().run()
    assert not app.exception
    assert any('REPLAY' in x.value for x in app.warning)
    next(x for x in app.button if x.label=='Next session').click().run()
    assert not app.exception


def test_demo_screener_runs_offline():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
    next(x for x in app.button if x.label=='Run screener').click().run(timeout=90)
    assert not app.exception
    assert any(len(x.value)==52 for x in app.dataframe)
