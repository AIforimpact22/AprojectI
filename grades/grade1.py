def grade_assignment(code):
    """
    Calculates a numeric grade for the assignment based on the user's code.
    """
    import pandas as pd
    import re

    grade = 0

    # a. Library Imports (5 points)
    required_imports = ["folium", "geopy", "geodesic", "pandas"]
    imported_libraries = sum(1 for lib in required_imports if lib in code)
    grade += min(5, imported_libraries * 1.25)

    # b. Coordinate Handling (5 points)
    coordinates = ["36.325735, 43.928414", "36.393432, 44.586781", "36.660477, 43.840174"]
    correct_coordinates = sum(1 for coord in coordinates if coord in code)
    grade += min(5, correct_coordinates * (5 / 3))

    # c. Code Execution (10 points)
    try:
        local_context = {}
        exec(code, {}, local_context)
        grade += 10  # Full points if the code runs without errors
    except Exception as e:
        print(f"Execution Error: {e}")

    # d. Code Quality (10 points)
    code_quality_issues = 0
    if any(f" {char} =" in code or f" {char}=" in code for char in "abcdefghijklmnopqrstuvwxyz"):
        code_quality_issues += 1
    if "=" in code.replace(" = ", ""):
        code_quality_issues += 1
    if "#" not in code:
        code_quality_issues += 1
    if "\n\n" not in code:
        code_quality_issues += 1
    grade += max(0, 10 - code_quality_issues * 2.5)

    # 2. Map Visualization (40 points)
    if "folium.Map" in code:
        grade += 15

    marker_count = code.count("folium.Marker")
    grade += min(15, marker_count * 5)

    if "PolyLine" in code:
        grade += 5

    if "popup=" in code:
        grade += 5

    # 3. Distance Calculations (30 points)
    if "geodesic" in code:
        grade += 10  # Full points for geodesic implementation

        # Verify accuracy of distance calculations
        try:
            distances_df = None
            for var_name, var_value in local_context.items():
                if isinstance(var_value, pd.DataFrame):
                    distances_df = var_value
                    break

            actual_distances = []

            # Extract distances from a DataFrame if it exists
            if distances_df is not None:
                numeric_columns = distances_df.select_dtypes(include=["float", "int"]).columns
                if not numeric_columns.empty:
                    actual_distances = distances_df[numeric_columns[0]].tolist()
                else:
                    print("No numeric columns found in DataFrame.")

            # If no DataFrame, fallback to searching for numeric patterns in code
            if not actual_distances:
                numeric_pattern = r"[-+]?[0-9]*\.?[0-9]+"
                actual_distances = [float(match) for match in re.findall(numeric_pattern, code) if "." in match]

            # Validate distances
            expected_distances = [59.57, 73.14, 37.98]
            tolerance = 0.5
            correct_distances = 0
            for expected in expected_distances:
                if any(abs(expected - actual) <= tolerance for actual in actual_distances):
                    correct_distances += 1

            grade += correct_distances * (20 / len(expected_distances))
        except Exception as e:
            print(f"Distance Verification Error: {e}")

    return round(grade)
