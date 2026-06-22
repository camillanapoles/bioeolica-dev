import pytest
from modules.mapa_unico import MapaUnico, DataEntry

def test_dataentry():
    d = DataEntry(domain="mecanica", name="E_mod", data_type="scalar", data={"value": 200e9})
    assert d.domain == "mecanica"

def test_mapa_init():
    m = MapaUnico(project="TEST", base_path="/tmp/test_mapa")
    assert m.project == "TEST"

def test_mapa_register():
    m = MapaUnico(project="TEST", base_path="/tmp/test_mapa")
    eid = m.register(domain="mecanica", name="test_param", data={"E": 200e9})
    assert type(eid) == str
