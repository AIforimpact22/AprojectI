# This makes the directory a Python package
from .tab1 import show as show_tab1
from .tab2 import show as show_tab2
from .tab3 import show as show_tab3

def show():
    tab1, tab2, tab3 = st.tabs(["Welcome", "Course Instructions", "Stay Connected"])
    with tab1: show_tab1()
    with tab2: show_tab2()
    with tab3: show_tab3()
