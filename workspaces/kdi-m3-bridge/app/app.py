"""KDI-M³ Dashboard — AI-assisted CAD/CAE with interactive config control."""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "cad-cae-platform"))

import streamlit as st
import pandas as pd

st.set_page_config(page_title="KDI-M³ AI CAD/CAE", layout="wide")
st.title("KDI-M³ CAD/CAE — AI-Assisted Design")
st.caption("Macro → Meso → Micro | config.json-driven | NVIDIA CUDA accelerated")

cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
from modules.kdi_forwarder import KDIForwarder

tab_config, tab_macro, tab_meso, tab_micro, tab_report = st.tabs(
    ["📋 Config", "🌍 Macro", "🔧 Meso", "🔬 Micro", "📊 Report"]
)

with tab_config:
    st.header("Configuration Editor")
    with open(cfg_path) as f:
        cfg_data = json.load(f)
    new_cfg = st.text_area("config.json", json.dumps(cfg_data, indent=2), height=400)
    if st.button("Save Config"):
        with open(cfg_path, "w") as f:
            json.dump(json.loads(new_cfg), f, indent=2)
        st.success("Config saved!")

with tab_macro:
    st.header("Macro-Scale Analysis")
    kf = KDIForwarder(cfg_path)
    if st.button("Run Macro Analysis"):
        with st.spinner("Running..."):
            r = kf.run_macro()
        st.json(r)
        dims = r.get("dimensions_mm", {})
        env = r.get("environment", {})
        c1, c2, c3 = st.columns(3)
        c1.metric("Volume", f"{r.get('volume_mm3',0):.0f} mm³")
        c2.metric("Mass", f"{r.get('mass_kg',0):.3f} kg")
        c3.metric("Wind Pressure", f"{env.get('wind_pressure_kPa',0):.2f} kPa")

with tab_meso:
    st.header("Meso-Scale Analysis")
    st.metric("Kt (stress concentration)", "3.0")
    # Add a visual
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Stress_concentration_factor.svg/320px-Stress_concentration_factor.svg.png",
             caption="Kirsch stress concentration factor Kt = 3.0 (infinite plate)")

with tab_micro:
    st.header("Micro-Scale Analysis")
    kf = KDIForwarder(cfg_path)
    if st.button("Run Micro Analysis"):
        with st.spinner("Running material homogenization..."):
            r = kf.run_micro()
        st.json(r)
        c1, c2, c3 = st.columns(3)
        c1.metric("E1 (GPa)", r.get("E1_GPa", 0))
        c2.metric("E2 (GPa)", r.get("E2_GPa", 0))
        c3.metric("Density (g/cm³)", r.get("density_g_cm3", 0))

with tab_report:
    st.header("Combined M³ Report")
    kf = KDIForwarder(cfg_path)
    if st.button("Run Full M³ Analysis"):
        with st.spinner("Running macro + meso + micro..."):
            r = kf.run_all()
        st.json(r)
