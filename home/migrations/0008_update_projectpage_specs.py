from django.db import migrations

# StreamField data migrations don't reconstruct block definitions
# reliably through Django's historical model state, so this imports
# the real model directly (the approach Wagtail's own docs recommend
# for StreamField content migrations) rather than using apps.get_model.
from home.models import ProjectPage


def spec_table(heading, rows):
    return {
        "type": "spec_table",
        "value": {
            "heading": heading,
            "rows": [{"label": label, "value": value} for label, value in rows],
        },
    }


def bullet_list(heading, items):
    return {"type": "bullet_list", "value": {"heading": heading, "items": items}}


def text_section(heading, paragraphs):
    html = "".join(f"<p>{p}</p>" for p in paragraphs)
    return {"type": "text_section", "value": {"heading": heading, "text": html}}


# Same body as 0007_seed_projectpage_content, with the salient-features
# spec tables replaced by the fuller, more precise engineering figures
# supplied for the "Learn More" page: the old standalone "Timeline" table
# is renamed/repositioned into "Project Implementation Schedule" alongside
# the other technical tables, several tables gain rows and more precise
# wording (gate size, tailrace lengths, etc.), and the now-duplicate
# Construction Period row is dropped from Access Infrastructure.
BODY = [
    {
        "type": "stat_cards",
        "value": {
            "cards": [
                {"value": "1,125 MW", "label": "Installed Capacity"},
                {"value": "2032", "label": "Planned Commissioning"},
                {"value": "USD 1.7B", "label": "Estimated Cost"},
                {"value": "72 Months", "label": "Construction Period"},
            ]
        },
    },
    text_section(
        "Project Overview",
        [
            "The Dorjilung Hydroelectric Power Project (DHPP) is one of Bhutan's most important "
            "national infrastructure initiatives. It is envisioned as a transformational 1,125 MW "
            "run-of-river project that will significantly strengthen the country's long-term energy "
            "security, economic development, and commitment to low-carbon growth. Recognized as a "
            "national priority by His Majesty the King, DHPP represents a modern approach to "
            "hydropower development, one that emphasizes strong environmental and social safeguards, "
            "adherence to international best practices, and a transparent Public-Private Partnership "
            "model between Druk Green Power Corporation Limited (DGPC) and Tata Power Company Limited "
            "of India. Supported by the financial and technical expertise of the World Bank Group, "
            "the project is expected to become a leading example of sustainable hydropower "
            "development in South Asia."
        ],
    ),
    text_section(
        "Location & Description",
        [
            "Eastern Bhutan, along the right bank of the Kurichhu River. Major components in Mongar, "
            "with portions extending into Lhuentse Dzongkhag. Dam site is about 1 km upstream of "
            "Rewan village; powerhouse is near Lingmithang. The area has comparatively good "
            "accessibility and a smaller environmental footprint than hydropower projects of similar scale.",
            "Reservoir designed to provide 3–8 hours of daily peaking power. Water diverted for "
            "generation returns to the river through two tailrace tunnels.",
        ],
    ),
    bullet_list(
        "Partnership & Financing",
        [
            "Joint venture: DGPC 60% equity, TCPL (Tata Power) 40%",
            "Dorjilung Hydro Power Limited (DHPL) incorporated to develop, operate, and maintain",
            "Concession agreement with the Royal Government of Bhutan: 30 years",
            "Estimated cost: USD 1.7 billion",
            "Debt-equity ratio: 70% debt / 30% equity",
            "Lead multilateral financier: World Bank Group (concessional financing + technical guidance)",
        ],
    ),
    bullet_list(
        "Socio-Economic Impact",
        [
            "Estimated 4,000–5,000 direct and indirect jobs per year during construction",
            "Benefits cited: business opportunities, housing and transport demand, improved access "
            "roads, market activity for food and services",
            "Surplus power to be exported to India, especially valuable in summer when regional demand peaks",
        ],
    ),
    text_section(
        "Environmental & Social Safeguards",
        [
            "Studies completed: Biodiversity Management Plan, Cultural Heritage Management Plan, "
            "Cumulative Impact Assessment (CIA) Addendum, Gender and Vulnerability Action Plan, Land "
            "Acquisition and Livelihood Restoration Plan (LALRP), Stakeholder Engagement Plan, SEA/SH "
            "Action Plan. All publicly disclosed."
        ],
    ),
    bullet_list(
        "Safeguard Measures",
        [
            "53 affected parties identified; 1 household requiring physical relocation",
            "Compensation at replacement cost, livelihood restoration support, transitional allowances",
            "Grievance channels: phone, SMS, dedicated committees, social media, walk-in offices",
            "Labour influx managed via codes of conduct, cultural orientation, managed worker camps, "
            "community health and safety plans with local authorities, police, and forestry",
        ],
    ),
    text_section(
        "Dam Safety",
        [
            "Overseen by an international panel of experts. Includes real-time vibration monitoring, "
            "construction supervision and QA systems, detailed instrumentation plans, and an "
            "emergency preparedness plan. Approach informed by past Bhutanese and international "
            "projects on sediment management, slope stability, groundwater behaviour, and structural "
            "integrity."
        ],
    ),
    spec_table(
        "Hydrology & Catchment",
        [
            ("Catchment Area", "8,782 km² (5,813 km² outside Bhutan)"),
            ("Design Flood", "16,225 m³/s"),
            ("Check Flood", "20,123 m³/s"),
            ("Design Discharge", "451 m³/s"),
            ("Dewatered River Reach", "About 16 km (dam to tailrace outlet)"),
        ],
    ),
    spec_table(
        "Reservoir Characteristics",
        [
            ("Gross Storage", "44.17M m³"),
            ("Live Storage", "12.62M m³"),
            ("Reservoir Area (FRL)", "145.82 ha"),
            ("Full Reservoir Level", "EL. 850 m"),
            ("Min. Drawdown Level", "EL. 840 m"),
        ],
    ),
    spec_table(
        "Dam & Spillway",
        [
            ("Type", "Concrete Gravity (RCC and CVC)"),
            ("Top Level", "EL. 853.0 m"),
            ("Length at Crest", "241.0 m"),
            ("Maximum Height", "139.5 m (~85 m above riverbed)"),
            ("Spillway Bays", "6 gated"),
            ("Spillway Gate Size", "9.0 m (w) × 15.10 m (h)"),
        ],
    ),
    spec_table(
        "Water Conveyance System",
        [
            ("Headrace Tunnel", "Single, 14,974 m long"),
            ("HRT Diameter", "11.0 m (concrete-lined)"),
            ("Surge Shaft", "Single, restricted-orifice type"),
            ("Surge Shaft Size", "135 m high × 4.1 m diameter"),
            ("Pressure Shafts", "3 × 332.8 m long"),
            ("Pressure Shaft Diameter", "5.5 m (steel-lined)"),
        ],
    ),
    spec_table(
        "Powerhouse & Tailrace",
        [
            ("Type", "Underground Cavern"),
            ("Dimensions", "210 × 23 × 60.5 m"),
            ("Tailrace Tunnels", "2 (350 m & 360 m long)"),
            ("Tailrace Shape / Diameter", "Horseshoe, 8.0 m"),
            ("Normal Tail Water", "EL. 544.0 m"),
        ],
    ),
    spec_table(
        "Power Generation & Energy Output",
        [
            ("Installed Capacity", "1,125 MW (6 × 187.5 MW Francis units)"),
            ("Gross Head", "300.45 m"),
            ("Design Energy", "4,504 GWh"),
            ("Firm Power", "153 MW"),
        ],
    ),
    spec_table(
        "Project Implementation Schedule",
        [
            ("Planned Completion & Commissioning", "2032"),
            ("Construction Period", "72 months"),
        ],
    ),
    spec_table(
        "Access Infrastructure",
        [
            ("Access Roads", "29.10 km"),
            ("Major Bridges", "2"),
        ],
    ),
]


def update_body(apps, schema_editor):
    page = ProjectPage.objects.get(slug="project")
    page.body = BODY
    page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_seed_projectpage_content'),
    ]

    operations = [
        migrations.RunPython(update_body, migrations.RunPython.noop),
    ]
