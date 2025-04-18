# modules_week1/__init__.py  (at the top)
from db import get_engine
from sqlalchemy import text

def make_db_tab(week:int, tab:int):
    tbl = f"w{week}tab{tab}"
    def show():
        engine = get_engine()
        r = engine.connect().execute(
            text(f"SELECT title, content FROM {tbl} LIMIT 1")
        ).fetchone()
        if r:
            st.markdown(r.title, unsafe_allow_html=True)
            st.markdown(r.content, unsafe_allow_html=True)
        else:
            st.info("No content yet.")
    return show

# then below, instead of importing static tab1.show, you could do:
default_tabs = [
    ("1.1 …", make_db_tab(1,1)),
    ("1.2 …", make_db_tab(1,2)),
    # …
]
