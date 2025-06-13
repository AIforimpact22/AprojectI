
import re
import csv
import math
import os
from PIL import Image

def grade_assignment(code, html_path, png_path, csv_path):
    total_score = 0
    debug_info = []

    ##########################################
    # 1. Library Imports (20 Points)
    ##########################################
    imports_score = 0
    # Define four groups:
    # Group 1: folium
    # Group 2: matplotlib or seaborn
    # Group 3: requests or urllib
    # Group 4: pandas
    required_libraries = {
        'folium': False,
        'matplotlib_or_seaborn': False,
        'requests_or_urllib': False,
        'pandas': False,
    }
    
    # Check for folium
    if re.search(r"(?i)(import|from)\s+folium\b", code):
        required_libraries['folium'] = True

    # Check for matplotlib or seaborn
    if re.search(r"(?i)(import|from)\s+matplotlib\b", code) or re.search(r"(?i)(import|from)\s+seaborn\b", code):
        required_libraries['matplotlib_or_seaborn'] = True

    # Check for requests or urllib
    if re.search(r"(?i)(import|from)\s+requests\b", code) or re.search(r"(?i)(import|from)\s+urllib\b", code):
        required_libraries['requests_or_urllib'] = True

    # Check for pandas
    if re.search(r"(?i)(import|from)\s+pandas\b", code):
        required_libraries['pandas'] = True

    # Each group is worth 5 points:
    for key, found in required_libraries.items():
        if found:
            imports_score += 5
    debug_info.append(f"Imports score: {imports_score:.2f} / 20")
    
    ##########################################
    # 2. Code Quality (20 Points)
    ##########################################
    # a) Descriptive Variable Names (5 Points)
    naming_score = 0
    if re.search(r"\bearthquake_map\b", code):
        naming_score += 5
    if re.search(r"\bmagnitude_counts\b", code):
        naming_score += 5
    naming_score = min(5, naming_score)
    
    # b) Spacing After Operators (5 Points)
    # Fix: Escape the '-' character or place it at the end of the character class
    spacing_score = 5 if not re.search(r"\S[=<>+*/-]{1}\S", code) else 2.5

    # c) Comments (5 Points)
    comment_lines = sum(1 for line in code.splitlines() if line.strip().startswith("#"))
    comments_score = min(5, (comment_lines / 3) * 5)
    
    # d) Code Organization (5 Points)
    organization_score = 5 if re.search(r"\n\s*\n", code) else 0

    quality_score = naming_score + spacing_score + comments_score + organization_score
    quality_score = min(20, quality_score)
    debug_info.append(f"Quality score: {quality_score:.2f} / 20")
    
    ##########################################
    # 3. Fetching Data from the API (5 Points)
    ##########################################
    api_score = 5 if re.search(r"(https?://\S+query\?[^'\"]*(starttime|endtime))", code, re.IGNORECASE) else 0
    debug_info.append(f"API score: {api_score} / 5")
    
    ##########################################
    # 4. Filtering Earthquakes (5 Points)
    ##########################################
    filter_score = 0
    # 2.5 points for filtering condition "magnitude > 4.0"
    if re.search(r"magnitude\s*[><=]+\s*4\.0", code):
        filter_score += 2.5
    # 2.5 points for detecting at least 4 key fields: latitude, longitude, magnitude, time
    extraction_hits = 0
    for field in ["latitude", "longitude", "magnitude", "time"]:
        if re.search(field, code, re.IGNORECASE):
            extraction_hits += 1
    if extraction_hits >= 4:
        filter_score += 2.5
    debug_info.append(f"Filter score: {filter_score} / 5")
    
    ##########################################
    # 5. Map Visualization (HTML) (25 Points)
    ##########################################
    map_score = 0
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read().lower()
        
        # (a) Markers (10 points): Check for substring "marker("
        if "marker(" in html_content:
            map_score += 10
        
        # (b) Color Keywords (10 points): Check for "green", "red", "yellow"
        colors_found = sum(1 for color in ["green", "red", "yellow"] if color in html_content)
        map_score += 10 * (colors_found / 3)
        
        # (c) Popup Content (5 points): Check for keywords "magnitude", "location", "time"
        popup_hits = sum(1 for keyword in ["magnitude", "location", "time"] if keyword in html_content)
        map_score += 5 * (popup_hits / 3)
    except Exception as e:
        debug_info.append(f"Map visualization check error: {e}")
    map_score = min(25, map_score)
    debug_info.append(f"Map visualization score: {map_score} / 25")
    
    ##########################################
    # 6. Bar Chart (PNG) (5 Points)
    ##########################################
    # Check that the PNG file is non-empty.
    bar_chart_score = 0
    try:
        if os.path.getsize(png_path) > 0:
            bar_chart_score = 5
    except Exception as e:
        debug_info.append(f"Bar chart file error: {e}")
    debug_info.append(f"Bar chart score: {bar_chart_score} / 5")
    
    ##########################################
    # 7. Text Summary (CSV) (20 Points)
    ##########################################
    summary_score = 0
    correct_values = {
        "Total Earthquakes (>4.0)": (218.0, 1),
        "Average Magnitude": (4.63, 0.1),
        "Maximum Magnitude": (7.1, 0.1),
        "Minimum Magnitude": (4.1, 0.1),
        "4.0-4.5": (75.0, 1),
        "4.5-5.0": (106.0, 1),
        "5.0+": (37.0, 1)
    }
    
    found_values = {metric: False for metric in correct_values}
    try:
        with open(csv_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                for cell in row:
                    try:
                        num = float(cell.strip())
                        for metric, (expected, tol) in correct_values.items():
                            if not found_values[metric] and math.isclose(num, expected, abs_tol=tol):
                                found_values[metric] = True
                    except ValueError:
                        continue
        partial = 0
        total_metrics = len(correct_values)
        for metric in correct_values:
            if found_values[metric]:
                partial += 20 / total_metrics
        summary_score = min(20, partial)
    except Exception as e:
        debug_info.append(f"CSV summary check error: {e}")
    debug_info.append(f"Text summary score: {summary_score} / 20")
    
    ##########################################
    # Total Score Calculation
    ##########################################
    total_score = (
        imports_score
        + quality_score
        + api_score
        + filter_score
        + map_score
        + bar_chart_score
        + summary_score
    )
    total_score = round(total_score, 2)
    
    # Uncomment the next line to print debug info locally for troubleshooting.
    # print("\n".join(debug_info))
    
    # Return only the total score (a number between 0 and 100)
    return total_score

