import streamlit as st
import mysql.connector
import json

# ──────────────────────────────────────────────────────────────────────────────
# DB helper (reads [mysql] block in secrets.toml)                                
# ──────────────────────────────────────────────────────────────────────────────

def _get_conn():
    cfg = st.secrets["mysql"]
    return mysql.connector.connect(
        host=cfg["host"],
        port=int(cfg.get("port", 3306)),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        autocommit=False,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Fetch progress data → [{name, progress:[w1..w5]}]                              
# ──────────────────────────────────────────────────────────────────────────────

def _fetch_progress():
    caps = {1: 10, 2: 12, 3: 12, 4: 12, 5: 7}  # full‑completion counts per week
    with _get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT users.fullname,
                   progress.week1track, progress.week2track,
                   progress.week3track, progress.week4track, progress.week5track
            FROM users
            JOIN progress ON users.username = progress.username
            WHERE users.approved = 1
            ORDER BY users.fullname;
            """
        )
        rows = cur.fetchall()

    data = []
    for row in rows:
        name = row[0] or "(no name)"
        progress = [row[i] / caps[i] if row[i] else 0 for i in range(1, 6)]
        data.append({"name": name, "progress": progress})
    return data


# ──────────────────────────────────────────────────────────────────────────────
# Streamlit page                                                                
# ──────────────────────────────────────────────────────────────────────────────

def show():
    st.title("Participants – Weekly Progress Heatmap")

    data = _fetch_progress()
    if not data:
        st.info("No approved participants yet.")
        return

    # Pass data to the client‑side via JSON embedded in the HTML.
    json_data = json.dumps(data)
    cell = 22  # px for each square (incl. small padding)
    chart_height = len(data) * cell + 40

    html = f"""
    <script src=\"https://d3js.org/d3.v7.min.js\"></script>
    <div id=\"chart\"></div>
    <script>
    const data = {json_data};
    const cell = {cell};

    const weeks = 5;
    const width = 150 + weeks * cell;              // 150px left margin for names
    const height = data.length * cell + 30;        // plus space for week labels

    const svg = d3.select('#chart').append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('font', '12px sans-serif');

    // Color scale – blue shades from 0 (white) to 1 (deep blue)
    const color = d3.scaleSequential(d3.interpolateBlues).domain([0, 1]);

    // Participant names
    svg.append('g')
      .selectAll('text')
      .data(data)
      .join('text')
        .attr('x', 0)
        .attr('y', (d, i) => i * cell + cell * 0.7)
        .text(d => d.name);

    // Heatmap cells
    const g = svg.append('g').attr('transform', `translate(150,0)`);

    g.selectAll('g')
      .data(data)
      .join('g')
        .attr('transform', (d, i) => `translate(0,${i * cell})`)
      .selectAll('rect')
      .data(d => d.progress.map((v, w) => ({v, w})))
      .join('rect')
        .attr('x', d => d.w * cell + 2)
        .attr('y', 2)
        .attr('width', cell - 4)
        .attr('height', cell - 4)
        .attr('fill', d => color(d.v))
      .append('title')
        .text(d => `Week ${d.w + 1}: ${(d.v * 100).toFixed(0)}%`);

    // Week labels along the bottom
    svg.append('g')
      .attr('transform', `translate(150,${data.length * cell + 5})`)
      .selectAll('text')
      .data(d3.range(1, weeks + 1))
      .join('text')
        .attr('x', (d) => (d - 1) * cell + 2)
        .text(d => `W${d}`);
    </script>
    """

    st.components.v1.html(html, height=chart_height, scrolling=True)


# Run standalone (helpful during local dev)
if __name__ == "__main__":
    show()
