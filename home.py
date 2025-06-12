
import streamlit as st
import streamlit.components.v1 as components
from theme import apply_dark_theme
from style import apply_custom_styles

def show_home():
    apply_dark_theme()      # ensures background is dark
    apply_custom_styles()   # ensures animated styles

    # Inject custom CSS to remove top padding/margin of the main container.
    st.markdown(
        """
        <style>
            /* Remove top padding from the main block container */
            .block-container {
                padding-top: 0rem;
                margin-top: 0rem;
            }
            /* Optionally, hide the Streamlit header if you want a full-screen experience */
            header { 
                visibility: hidden;
                height: 0;
            }
            /* Remove body margin */
            body {
                margin: 0;
                padding: 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Render the SVG graphic at the very top using components.html.
    svg_code = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
        <defs>
            <!-- Light Grey Wave Gradient -->
            <linearGradient id="impactWave" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#d3d3d3"/>
                <stop offset="50%" style="stop-color:#d3d3d3"/>
                <stop offset="100%" style="stop-color:#d3d3d3"/>
            </linearGradient>

            <!-- Enhanced glow effects -->
            <filter id="primaryGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="4" result="blur"/>
                <feFlood flood-color="#d3d3d3" flood-opacity="0.3" result="color"/>
                <feComposite in="color" in2="blur" operator="in" result="glow"/>
                <feMerge>
                    <feMergeNode in="glow"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>

            <!-- Tech pattern -->
            <pattern id="techGrid" x="0" y="0" width="50" height="50" patternUnits="userSpaceOnUse">
                <path d="M25 0 v50 M0 25 h50" stroke="#4B5563" stroke-width="0.5" opacity="0.15"/>
                <circle cx="25" cy="25" r="1" fill="#4B5563" opacity="0.2"/>
            </pattern>

            <!-- Binary rain effect -->
            <filter id="binaryRain">
                <feTurbulence type="fractalNoise" baseFrequency="0.01" numOctaves="5" seed="5"/>
                <feDisplacementMap in="SourceGraphic" scale="5"/>
            </filter>
        </defs>

        <!-- Pure black background -->
        <rect width="800" height="400" fill="#000000"/>
        <rect width="800" height="400" fill="url(#techGrid)"/>

        <!-- Dynamic world map representation -->
        <g transform="translate(50, 50)" filter="url(#primaryGlow)" opacity="0.3">
            <path d="M0 150 Q200 100 400 150 T800 150" stroke="url(#impactWave)" stroke-width="2" fill="none">
                <animate attributeName="d" 
                         dur="8s" 
                         values="M0 150 Q200 100 400 150 T800 150;
                                M0 170 Q200 120 400 170 T800 170;
                                M0 150 Q200 100 400 150 T800 150"
                         repeatCount="indefinite"/>
            </path>
            <!-- Connection points representing global impact -->
            <g class="impact-points">
                <circle cx="100" cy="120" r="3" fill="#d3d3d3">
                    <animate attributeName="r" values="3;5;3" dur="3s" repeatCount="indefinite"/>
                </circle>
                <circle cx="300" cy="140" r="3" fill="#d3d3d3">
                    <animate attributeName="r" values="3;5;3" dur="3s" begin="1s" repeatCount="indefinite"/>
                </circle>
                <circle cx="500" cy="130" r="3" fill="#d3d3d3">
                    <animate attributeName="r" values="3;5;3" dur="3s" begin="2s" repeatCount="indefinite"/>
                </circle>
            </g>
        </g>

        <!-- Advanced neural network visualization -->
        <g transform="translate(100, 100)" filter="url(#primaryGlow)">
            <!-- Multiple interconnected layers -->
            <g class="neural-network">
                <!-- Layer connections with data flow -->
                <path d="M0 100 C100 50 200 150 300 100" stroke="url(#impactWave)" stroke-width="1.5" fill="none" opacity="0.6">
                    <animate attributeName="stroke-dasharray" values="0,1000;1000,0" dur="5s" repeatCount="indefinite"/>
                </path>
                <path d="M0 150 C100 100 200 200 300 150" stroke="url(#impactWave)" stroke-width="1.5" fill="none" opacity="0.6">
                    <animate attributeName="stroke-dasharray" values="0,1000;1000,0" dur="5s" begin="0.5s" repeatCount="indefinite"/>
                </path>
            </g>
        </g>

        <!-- Python code elements with impact focus -->
        <g transform="translate(500, 140)" filter="url(#primaryGlow)">
            <g class="code-snippet" opacity="0.8">
                <text x="0" y="0" font-family="JetBrains Mono, monospace" fill="#A5B4FC" font-size="14">
                    class KurdistanFuture:
                    <animate attributeName="opacity" values="0.7;1;0.7" dur="4s" repeatCount="indefinite"/>
                </text>
                <text x="20" y="25" font-family="JetBrains Mono, monospace" fill="#A5B4FC" font-size="14">
                    def innovate(self):
                    <animate attributeName="opacity" values="0.7;1;0.7" dur="4s" begin="0.5s" repeatCount="indefinite"/>
                </text>
                <text x="40" y="50" font-family="JetBrains Mono, monospace" fill="#A5B4FC" font-size="14">
                    return AI.transform_region()
                    <animate attributeName="opacity" values="0.7;1;0.7" dur="4s" begin="1s" repeatCount="indefinite"/>
                </text>
            </g>
        </g>

        <!-- Web development elements -->
        <g transform="translate(500, 230)" filter="url(#primaryGlow)">
            <g class="web-elements" opacity="0.6">
                <text x="0" y="0" font-family="JetBrains Mono, monospace" fill="#818CF8" font-size="14">&lt;div class="impact"&gt;</text>
                <text x="20" y="25" font-family="JetBrains Mono, monospace" fill="#818CF8" font-size="14">&lt;App /&gt;</text>
                <text x="0" y="50" font-family="JetBrains Mono, monospace" fill="#818CF8" font-size="14">&lt;/div&gt;</text>
            </g>
        </g>

        <!-- Course title with impact animation -->
        <g transform="translate(400, 80)" filter="url(#primaryGlow)">
            <text text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" font-size="56" fill="#FFFFFF" font-weight="bold">
                AI for Impact
                <animate attributeName="opacity" values="0.9;1;0.9" dur="4s" repeatCount="indefinite"/>
            </text>
        </g>

        <!-- Inspiring subtitle -->
        <g transform="translate(400, 330)" filter="url(#primaryGlow)">
            <text text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" font-size="24" fill="#A5B4FC">
                Building Tomorrow's Solutions Today
                <animate attributeName="fill" values="#A5B4FC;#818CF8;#A5B4FC" dur="6s" repeatCount="indefinite"/>
            </text>
        </g>

        <!-- Technology stack with icons -->
        <g transform="translate(400, 370)" filter="url(#primaryGlow)">
            <text text-anchor="middle" font-family="Plus Jakarta Sans, sans-serif" font-size="16" fill="#6366F1">
                Python • Web Apps • Machine Learning • Data Analysis • Google Colab
            </text>
        </g>

        <!-- Floating particles representing data points -->
        <g class="particles" filter="url(#binaryRain)">
            <circle cx="150" cy="200" r="2" fill="#d3d3d3" opacity="0.5">
                <animate attributeName="cy" values="200;220;200" dur="4s" repeatCount="indefinite"/>
            </circle>
            <circle cx="650" cy="180" r="2" fill="#d3d3d3" opacity="0.5">
                <animate attributeName="cy" values="180;200;180" dur="4s" begin="1s" repeatCount="indefinite"/>
            </circle>
            <circle cx="400" cy="150" r="2" fill="#d3d3d3" opacity="0.5">
                <animate attributeName="cy" values="150;170;150" dur="4s" begin="2s" repeatCount="indefinite"/>
            </circle>
        </g>
    </svg>
    """

    # Render the SVG using components.html and ensure there is no extra margin.
    components.html(
        f"""
        <div style="margin:0; padding:0;">
            {svg_code}
        </div>
        """,
        height=500,
    )


if __name__ == "__main__":
    show_home()
