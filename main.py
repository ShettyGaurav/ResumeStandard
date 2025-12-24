from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import logging
from datetime import datetime
import os

styles = getSampleStyleSheet()

TEXT = HexColor("#091448")
HEADER_CONTENT_TOP_OFFSET = 35

# ---------------------------------Global Configs---------------
HEADER_STYLE = ParagraphStyle(
    "HeaderStyle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    textColor=white,      # 🔴 CRITICAL FIX
    alignment=1,
    leading=11,
)

CELL_STYLE = ParagraphStyle(
    "CellStyle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    textColor=TEXT,
    leading=11,
    wordWrap="CJK",       # 🔴 CRITICAL FIX
)

def header_cell(text):
    return Paragraph(text, HEADER_STYLE)

def body_cell(text):
    return Paragraph(text if text else "", CELL_STYLE)



logging.basicConfig(
    level=logging.INFO,  # change to DEBUG if needed
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("resume_pdf_generator")




# ---------------- PAGE CONFIG ----------------

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 72
RIGHT_MARGIN = PAGE_WIDTH - 72
BOTTOM_MARGIN = 72
LINE_HEIGHT = 14
SECTION_SPACING = 30
BASE_HEADER_HEIGHT = 70
CONTACT_EXTRA_HEIGHT = 60  # more fields
SPACE_BEFORE_SECTION = 20
FIRST_PAGE_HEADER_HEIGHT = 80
FIRST_PAGE_HEADER_WITH_CONTACT = 90
FIRST_PAGE_HEADER_NO_CONTACT = 70
OTHER_PAGE_HEADER_HEIGHT = 60
CURRENT_PAGE = 1

LOGO_X_FIRST_PAGE = LEFT_MARGIN - 30  # current position
LOGO_X_OTHER_PAGES = 20  # more left (near page edge)


# ---------------- COLORS ----------------

BG_DARK = HexColor("#0A0F20")
SECTION = HexColor("#0B3A3E")
TEXT = HexColor("#091448")
TABLE_BG = HexColor("#F7F9FC")

# ---------------- OUTPUT ----------------


def cell(text, bold=False):
    style = styles["Normal"]
    style.fontName = "Helvetica-Bold" if bold else "Helvetica"
    style.fontSize = 9
    style.leading = 11
    style.wordWrap = "CJK"  # IMPORTANT: forces wrapping
    return Paragraph(text, style)


def output_path(name):
    os.makedirs("OutputFolder", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"OutputFolder/{name.replace(' ', '_')}_{ts}.pdf"


def extract_handle(url):
    if not url or url.lower() == "none":
        return None
    return url.rstrip("/").split("/")[-1]


# ---------------- HEADER ----------------


def draw_icon_text(c, icon_path, text, start_x, center_y, font="Helvetica", size=9):
    ICON_SIZE = 16
    ICON_GAP = 8

    text_width = c.stringWidth(text, font, size)

    # Icon vertically centered
    icon_y = center_y - ICON_SIZE / 2

    # Text baseline adjusted to visual center
    text_y = center_y - size * 0.3

    c.drawImage(
        icon_path,
        start_x,
        icon_y,
        ICON_SIZE,
        ICON_SIZE,
        mask="auto",
    )

    c.setFont(font, size)
    c.drawString(
        start_x + ICON_SIZE + ICON_GAP,
        text_y,
        text,
    )

    return start_x + ICON_SIZE + ICON_GAP + text_width



def draw_header(c, name, contact, page_no, logo_path="refernce/logoWhite.png"):
    is_first_page = page_no == 1

    if is_first_page:
        if contact:   # show_contact=True
            header_height = FIRST_PAGE_HEADER_WITH_CONTACT
        else:         # show_contact=False
            header_height = FIRST_PAGE_HEADER_NO_CONTACT
    else:
        header_height = OTHER_PAGE_HEADER_HEIGHT


    # Background
    c.setFillColor(BG_DARK)
    c.rect(0, PAGE_HEIGHT - header_height, PAGE_WIDTH, header_height, 0, 1)

    # Logo (LEFT – ALL pages)
    # Logo position based on page
    logo_x = LOGO_X_FIRST_PAGE if is_first_page else LOGO_X_OTHER_PAGES

    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(
            logo,
            logo_x,
            PAGE_HEIGHT - header_height + 10,
            width=80,
            height=header_height - 20,
            preserveAspectRatio=True,
            mask="auto",
        )

    if is_first_page:
        right_x = RIGHT_MARGIN
        y = PAGE_HEIGHT - HEADER_CONTENT_TOP_OFFSET

        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(white)
        name_width = c.stringWidth(name, "Helvetica-Bold", 20)
        c.drawString(right_x - name_width, y, name)
        y -= 22

        # -------- CONTACT (ONLY IF PRESENT) --------
        if contact:
            ICON_SIZE = 16
            ICON_GAP = 1
            ROW_GAP = 18

            c.setFont("Helvetica", 9)

            phone = contact.get("phone")
            email = contact.get("email")
            linkedin_url = contact.get("linkedin")
            github_url = contact.get("github")

            linkedin_handle = extract_handle(linkedin_url)
            github_handle = extract_handle(github_url)

            # -------- ROW 1 : PHONE + LINKEDIN --------
            row_y = y

            # LinkedIn (rightmost)
            ROW_CENTER_Y = y

# LinkedIn (right)
            if linkedin_handle:
                text_w = c.stringWidth(linkedin_handle, "Helvetica", 9)
                total_w = 16 + 4 + text_w
                li_x = right_x - total_w

                draw_icon_text(
                    c,
                    "assets/linkedin.png",
                    linkedin_handle,
                    li_x,
                    ROW_CENTER_Y,
                )

                c.linkURL(
                    linkedin_url,
                    (li_x, ROW_CENTER_Y - 8, right_x, ROW_CENTER_Y + 8),
                    relative=0,
                )

                phone_right_limit = li_x - 16
            else:
                phone_right_limit = right_x

            # Phone (left)
            if phone:
                phone_text = phone
                phone_w = c.stringWidth(phone_text, "Helvetica", 9)
                total_w = 16 + 4 + phone_w
                phone_x = phone_right_limit - total_w

                draw_icon_text(
                    c,
                    "assets/phone.png",
                    phone_text,
                    phone_x,
                    ROW_CENTER_Y,
                )
            if phone:
                phone_text = phone
                phone_w = c.stringWidth(phone_text, "Helvetica", 9)
                total_w = 16 + 4 + phone_w
                phone_x = phone_right_limit - total_w

                draw_icon_text(
                    c,
                    "assets/phone.png",
                    phone_text,
                    phone_x,
                    ROW_CENTER_Y,
                )


            # -------- ROW 2 : EMAIL + GITHUB --------
            row_y -= ROW_GAP

            ROW_CENTER_Y -= ROW_GAP

            # GitHub (right)
            if github_handle:
                gh_w = c.stringWidth(github_handle, "Helvetica", 9)
                total_w = 16 + 4 + gh_w
                gh_x = right_x - total_w

                draw_icon_text(
                    c,
                    "assets/github.png",
                    github_handle,
                    gh_x,
                    ROW_CENTER_Y,
                )

                c.linkURL(
                    github_url,
                    (gh_x, ROW_CENTER_Y - 8, right_x, ROW_CENTER_Y + 8),
                    relative=0,
                )

                email_right_limit = gh_x - 16
            else:
                email_right_limit = right_x

            # Email (left)
            if email:
                email_w = c.stringWidth(email, "Helvetica", 9)
                total_w = 16 + 4 + email_w
                email_x = email_right_limit - total_w

                draw_icon_text(
                    c,
                    "assets/email.png",
                    email,
                    email_x,
                    ROW_CENTER_Y,
                )


            y = row_y - ROW_GAP

    # 🔴 RESET CANVAS STATE
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 10)

    return header_height


def start_new_page(c, name, contact):
    global CURRENT_PAGE
    CURRENT_PAGE += 1
    c.showPage()

    header_height = draw_header(c, name, contact, CURRENT_PAGE)
    return PAGE_HEIGHT - header_height - 30


def draw_text(c, text, x, y, max_width, name, contact, size=10, bold=False):
    font = "Helvetica-Bold" if bold else "Helvetica"
    c.setFont(font, size)
    c.setFillColor(TEXT)

    for line in simpleSplit(text, font, size, max_width):
        if y < BOTTOM_MARGIN:
            y = start_new_page(c, name, contact)
            c.setFont(font, size)
            c.setFillColor(TEXT)
        c.drawString(x, y, line)
        y -= LINE_HEIGHT
    return y


def draw_bullet(c, text, y, name, contact):
    lines = simpleSplit(text, "Helvetica", 10, RIGHT_MARGIN - LEFT_MARGIN - 14)
    required = len(lines) * LINE_HEIGHT

    if y - required < BOTTOM_MARGIN:
        y = start_new_page(c, name, contact)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(LEFT_MARGIN, y, "•")

    c.setFont("Helvetica", 10)
    for line in lines:
        c.drawString(LEFT_MARGIN + 14, y, line)
        y -= LINE_HEIGHT
    return y


def section_title(c, title, y, name, contact):
    y -= SPACE_BEFORE_SECTION
    if y < BOTTOM_MARGIN + 30:
        y = start_new_page(c, name, contact)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(SECTION)
    c.drawString(LEFT_MARGIN, y, title.upper())
    y -= 6
    c.line(LEFT_MARGIN, y, RIGHT_MARGIN, y)
    return y - 16


# ---------------- SKILLSET ----------------


def draw_skillset_table(c, skillset, y, name, contact):
    # ---------------- HEADER ROW ----------------
    table_data = [
        [
            header_cell("Domain"),
            header_cell("Category"),
            header_cell("Skills"),
        ]
    ]

    # ---------------- DATA ROWS ----------------
    for domain, domain_data in skillset.items():

        # ---- CASE 1: DOMAIN IS A LIST ----
        if isinstance(domain_data, list):
            if domain_data:
                table_data.append([
                    body_cell(domain),
                    body_cell(""),
                    body_cell(", ".join(domain_data)),
                ])
            continue

        # ---- CASE 2: DOMAIN IS A DICT ----
        first_row = True

        for category, values in domain_data.items():

            # Nested dict (e.g., Databases → SQL / NoSQL)
            if isinstance(values, dict):
                for subcat, subvals in values.items():
                    if subvals:
                        table_data.append([
                            body_cell(domain if first_row else ""),
                            body_cell(f"{category} ({subcat})"),
                            body_cell(", ".join(subvals)),
                        ])
                        first_row = False

            # Normal list
            elif isinstance(values, list) and values:
                table_data.append([
                    body_cell(domain if first_row else ""),
                    body_cell(category),
                    body_cell(", ".join(values)),
                ])
                first_row = False

    # ---------------- NOTHING TO RENDER ----------------
    if len(table_data) == 1:
        return y

    # ---------------- TABLE ----------------
    table = Table(
        table_data,
        colWidths=[
            90,
            160,
            RIGHT_MARGIN - LEFT_MARGIN - 250,
        ],
        repeatRows=1,   # header repeats on page breaks
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BG_DARK),
                ("GRID", (0, 0), (-1, -1), 0.5, SECTION),
                ("BACKGROUND", (0, 1), (-1, -1), TABLE_BG),

                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),

                ("WORDWRAP", (0, 0), (-1, -1), True),
            ]
        )
    )

    # ---------------- PAGINATION ----------------
    table.wrapOn(c, PAGE_WIDTH, PAGE_HEIGHT)
    height = table._height

    if y - height < BOTTOM_MARGIN:
        y = start_new_page(c, name, contact)

    table.drawOn(c, LEFT_MARGIN, y - height)

    return y - height - 14



def draw_professional_history(c, history, y, name, contact):
    y = section_title(c, "Employment History", y, name, contact)

    for job in history:
        # Job title and company
        title_company = f"{job['title']} at {job['company']}"
        y = draw_text(
            c,
            title_company,
            LEFT_MARGIN,
            y,
            RIGHT_MARGIN - LEFT_MARGIN,
            name,
            contact,
            bold=True,
        )

        if job.get("timespan"):
            y -= 2
            y = draw_text(
                c,
                job["timespan"],
                LEFT_MARGIN,
                y,
                RIGHT_MARGIN - LEFT_MARGIN,
                name,
                contact,
                size=9.3,
            )
        y -= 3

        # Job points
        for point in job.get("points", []):
            y = draw_bullet(c, point, y, name, contact)

        y -= 8

    return y


def draw_projects(c, projects, y, name, contact):
    y = section_title(c, "Project Showcase", y, name, contact)

    for project in projects:
        y = draw_text(
            c,
            project["title"],
            LEFT_MARGIN,
            y,
            RIGHT_MARGIN - LEFT_MARGIN,
            name,
            contact,
            bold=True,
        )

        tech = ", ".join(project.get("technologies", []))
        if tech:
            y -= 2
            y = draw_text(
                c,
                f"Technologies: {tech}",
                LEFT_MARGIN,
                y,
                RIGHT_MARGIN - LEFT_MARGIN,
                name,
                contact,
                size=9.3,
            )
        y-=3

        for point in project.get("points", []):
            y = draw_bullet(c, point, y, name, contact)

        y -= 8

    return y


# ---------------- MAIN ----------------


def generate_resume_pdf(state, show_contact=True):
    logger.info("Starting PDF generation")

    global CURRENT_PAGE
    CURRENT_PAGE = 1  # must be reset at start
    logger.debug("Initialized CURRENT_PAGE = 1")

    resume = state.get("resume", {})
    name = resume.get("name", "Unknown")
    contact = resume.get("contact", {}) if show_contact else None

    output_file = output_path(name)
    logger.info(f"Output PDF path resolved: {output_file}")

    try:
        c = canvas.Canvas(output_file, pagesize=A4)

        header_height = draw_header(c, name, contact, CURRENT_PAGE)
        y = PAGE_HEIGHT - header_height - 30

        logger.debug(f"Header drawn, starting Y position: {y}")

        # ---------- SUMMARY ----------
        summary = " ".join(resume.get("summary", []))
        if summary:
            logger.info("Rendering Objectives section")
            y += 20
            y = section_title(c, "Objectives", y, name, contact)
            y = draw_text(
                c,
                summary,
                LEFT_MARGIN,
                y,
                RIGHT_MARGIN - LEFT_MARGIN,
                name,
                contact,
            )
            y -= 10
        else:
            logger.debug("No summary provided, skipping Objectives section")

        # ---------- CAREER SUMMARY ----------
        career = resume.get("sections", {}).get("Career Summary", [])
        if career:
            logger.info("Rendering Career Summary section")
            y = section_title(c, "Career Summary", y, name, contact)
            for idx, point in enumerate(career, start=1):
                logger.debug(f"Career bullet {idx}: {point[:60]}...")
                y = draw_bullet(c, point, y, name, contact)
        else:
            logger.debug("No Career Summary data found")

        # ---------- SKILLSET ----------
        skills = resume.get("sections", {}).get("Skillset", {})
        if skills:
            logger.info("Rendering Skillset section")
            y = section_title(c, "Skillset", y, name, contact)
            y = draw_skillset_table(c, skills, y, name, contact)
        else:
            logger.debug("No Skillset data found")

        # ---------- PROFESSIONAL HISTORY ----------
        professional_history = resume.get("sections", {}).get(
            "Professional History", []
        )
        if professional_history:
            logger.info("Rendering Professional History section")
            y = draw_professional_history(
                c, professional_history, y, name, contact
            )
        else:
            logger.debug("No Professional History found")

        # ---------- PROJECTS ----------
        projects = resume.get("sections", {}).get("Project Showcase", [])
        if projects:
            logger.info(f"Rendering {len(projects)} project(s)")
            y = draw_projects(c, projects, y, name, contact)
        else:
            logger.debug("No projects found")

        # ---------- EDUCATION ----------
        education = resume.get("sections", {}).get("Education", [])
        if education:
            logger.info("Rendering Education section")
            y = section_title(c, "Education", y, name, contact)
            for edu in education:
                y = draw_bullet(c, edu, y, name, contact)
        else:
            logger.debug("No Education data found")

        c.save()
        logger.info("PDF generated successfully")

        return output_file

    except Exception as e:
        logger.exception("PDF generation failed due to an exception")
        raise





state = {
    "resume": {
        "name": "Shetty Gaurav Jagadeesha",
        "sections": {
            "Career Summary": [
                "Designed, deployed, and maintained cloud-native infrastructure to support highly available and scalable applications.",
                "Automated CI/CD pipelines to improve deployment reliability and reduce release turnaround time.",
                "Managed containerized workloads using Docker and Kubernetes in production environments.",
                "Implemented infrastructure as code to standardize and version control cloud resources.",
                "Monitored systems and services to ensure uptime, performance, and rapid incident response.",
            ],
            "Education": [
                "B.E. in Artificial Intelligence and Machine Learning from Alvas Institute of Engineering and Technology",
                "PCMB (Physics, Chemistry, Mathematics, Biology) from Viveka PU College, Kota",
            ],
            "Project Showcase": [
                {
                    "title": "Cloud-Native CI/CD Platform",
                    "technologies": [
                        "AWS",
                        "Docker",
                        "Kubernetes",
                        "GitHub Actions",
                    ],
                    "points": [
                        "Built a fully automated CI/CD pipeline for containerized applications using GitHub Actions.",
                        "Containerized services with Docker and deployed them to Kubernetes clusters.",
                        "Implemented rolling deployments and rollback strategies to minimize downtime.",
                        "Integrated build, test, and deployment stages to ensure reliable releases.",
                    ],
                },
                {
                    "title": "Infrastructure as Code with Terraform",
                    "technologies": ["Terraform", "AWS", "EC2", "VPC"],
                    "points": [
                        "Provisioned cloud infrastructure using Terraform for repeatable and version-controlled deployments.",
                        "Designed VPCs, subnets, security groups, and EC2 instances using modular Terraform configurations.",
                        "Reduced manual configuration errors by enforcing infrastructure standards through code.",
                        "Enabled rapid environment setup for development and testing.",
                    ],
                },
                {
                    "title": "Monitoring and Logging Stack",
                    "technologies": ["Prometheus", "Grafana", "Docker"],
                    "points": [
                        "Set up centralized monitoring for containerized applications using Prometheus.",
                        "Built Grafana dashboards to visualize system metrics and application performance.",
                        "Configured alerting rules to detect failures and performance degradation early.",
                        "Improved operational visibility and reduced mean time to resolution.",
                    ],
                },
            ],
            "Professional History": [
                {
                    "title": "DevOps Engineer",
                    "company": "Tech Solutions Inc.",
                    "timespan": "Jan 2023 - Present",
                    "points": [
                        "Led cloud infrastructure migration reducing operational costs by 30%",
                        "Implemented automated CI/CD pipelines serving 50+ microservices",
                        "Managed Kubernetes clusters handling 10M+ daily requests",
                    ],
                },
                {
                    "title": "Junior DevOps Engineer",
                    "company": "StartupXYZ",
                    "timespan": "Jun 2022 - Dec 2022",
                    "points": [
                        "Containerized legacy applications using Docker",
                        "Set up monitoring and alerting systems using Prometheus and Grafana",
                        "Automated deployment processes reducing release time by 50%",
                    ],
                },
            ],
            "Skillset": {
                "DevOps": {
                    "CI / CD": ["GitHub Actions", "Jenkins"],
                    "Containerization & Orchestration": ["Docker", "Kubernetes"],
                    "Monitoring & Logging": ["Prometheus", "Grafana"],
                },
                "Cloud": {
                    "Cloud Platforms": ["AWS"],
                    "Cloud Services": ["EC2", "VPC", "IAM"],
                },
                "Backend": {
                    "Server Runtime": ["Node.js"],
                    "Databases": {"SQL": ["PostgreSQL"], "NoSQL": ["MongoDB"]},
                },
                "Tools": {
                    "Infrastructure as Code": ["Terraform"],
                    "Version Control": ["Git"],
                },
            },
        },
        "summary": [
            "DevOps-focused engineer with hands-on experience in cloud infrastructure, automation, and containerized systems.",
            "Skilled in building reliable CI/CD pipelines and managing Kubernetes-based deployments.",
            "Strong interest in infrastructure automation, monitoring, and scalable cloud-native architectures.",
        ],
        "contact": {
            "phone": "+91 9876543210",
            "email": "gaurav@example.com",
            "linkedin": "https://linkedin.com/in/gauravshetty",
            "github": "https://github.com/gauravshetty",
            "location": "Mangaluru, India",
        },
    }
}

# render_resume_from_state(state, True)
