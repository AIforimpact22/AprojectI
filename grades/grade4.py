
def grade_assignment(code_input, rectangle_grade, thresholded_image_grade, outlined_image_grade):
    total_grade = 0
    grading_breakdown = {}

    # 1. Library Imports (Up to 20 Points)
    # Modified: 8 points for "cv2", 6 points for "numpy", and 6 points for "matplotlib".
    libraries = {
        "cv2": 8,
        "numpy": 6,
        "matplotlib": 6
    }
    library_score = 0
    for lib, points in libraries.items():
        if lib in code_input:
            library_score += points
    grading_breakdown["Library Imports"] = min(library_score, 20)
    total_grade += grading_breakdown["Library Imports"]

    # 2. Code Quality (Supposedly 14 Points)
    code_quality = {
        "Variable Naming": 4 if "x" not in code_input or "y" not in code_input else 0,
        "Spacing": 2 if " =" not in code_input and "= " not in code_input else 0,
        "Comments": 2 if "#" in code_input else 0,
        "Code Organization": 2 if "\n\n" in code_input else 0,
    }
    grading_breakdown["Code Quality"] = sum(code_quality.values())
    total_grade += grading_breakdown["Code Quality"]

    # 3. Rectangle Coordinates
    # Each correct number (order-independent) earns 1 point.
    grading_breakdown["Rectangle Coordinates"] = rectangle_grade
    total_grade += rectangle_grade

    # 4. Thresholded Image (5 Points)
    # If a valid thresholded image is uploaded, award 5 points.
    grading_breakdown["Thresholded Image"] = thresholded_image_grade
    total_grade += thresholded_image_grade

    # 5. Image with Rectangles Outlined (5 Points)
    # If a valid outlined image is uploaded, award 5 points.
    grading_breakdown["Image with Rectangles Outlined"] = outlined_image_grade
    total_grade += outlined_image_grade

    return total_grade, grading_breakdown
