'''
resume_parser.py: store the resume parsing logic in this file.
- Access resumes from data/resumes/raw
- Output: structured JSON, sotred under data/resume/parsed
'''

import json
import re
from pathlib import Path
from datetime import datetime
import pdfplumber

from core.parser.schema import Resume, Skills, Experience, Project, Metadata

DATE_PATTERN = r"""
(
    (?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s*\d{4}
    |
    \d{2}/\d{2}/\d{4}
    |
    \d{2}/\d{4}
    |
    \d{4}
)
"""

ROLE_KEYWORDS = [
    "engineer",
    "developer",
    "intern",
    "analyst",
    "consultant",
    "programmer",
    "designer",
]

SECTION_SYNONYMS = {
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "internship",
        "internships",
    ],
    "projects": [
        "projects",
        "my projects",
        "academic projects",
        "personal projects",
        "technical projects",
    ],
    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "skill set",
        "technologies",
        "technical proficiency",
    ],
}


def contains_date(line: str) -> bool:
    return re.search(DATE_PATTERN, line.lower(), re.VERBOSE) is not None


RAW_DIR = Path("data/resumes/raw")
PARSED_DIR = Path("data/resumes/parsed")
PARSER_VERSION = "latex-template-v1" # u can change this to keep track of different runs on the same resume 


def extract_text_from_pdf(pdf_path: Path) -> list[str]:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return [l.strip() for l in text.splitlines() if l.strip()]


# ---------------- SECTION SPLITTING ----------------

def split_by_sections(lines):
    sections = {}
    current = None

    for line in lines:
        normalized = line.lower().strip()

        found_section = False

        for section, keywords in SECTION_SYNONYMS.items():
            if normalized in keywords:
                current = section
                sections[current] = []
                found_section = True
                break

        if found_section:
            continue

        if current:
            sections[current].append(line)

    return sections



# ---------------- SKILLS ----------------

def parse_skills(lines):
    languages = []
    frameworks = []
    tools = []

    for line in lines:

        #dont pars skills if we hit non-skills sections
        if line.strip().lower() in ["achievements", "profile links","projects","experiences","education"]:
            break
        
        if "languages" in line.lower():
            languages = [x.strip() for x in line.split(":")[1].split(",")]
        elif "technologies" in line.lower() or "framework" in line.lower():
            frameworks = [x.strip() for x in line.split(":")[1].split(",")]
        else:
            if ":" in line:
                values = line.split(":", 1)[1]
                tools.extend([x.strip() for x in values.split(",")])
            elif "," in line :
                tools.extend([x.strip() for x in line.split(",")])    

    languages = list(dict.fromkeys(languages))
    frameworks = list(dict.fromkeys(frameworks))
    tools = list(dict.fromkeys(tools))            

    return Skills(
        languages=languages,
        frameworks=frameworks,
        tools=tools
    )


# ---------------- EXPERIENCE ----------------

def parse_experience(lines):
    experiences = []
    current = None
    claims = []

    for line in lines:
        line = re.sub(r"^[•\u2022\u25cf\u25aa\u25e6\-]+", "", line).strip()
        #print(repr(line))  # uncomment for debugging

        # dont pars experience if we hit non-experience sections
        if line.lower() in ["achievements", "profile links", "projects", "skills","education"]:
            break

        # detect NEW ROLE while another experience is active
        if (
            current
            and any(
                re.search(rf"\b{k}\b", line.lower())
                for k in ROLE_KEYWORDS
            )
            and not contains_date(line)
            and "|" not in line
        ):
            experiences.append(
                Experience(
                    role=current["role"],
                    company=current["company"],
                    duration=current["duration"],
                    claims=claims,
                    tools=current["tools"]
                )
            )

            current = {
                "company": "",
                "role": line,
                "duration": "",
                "tools": []
            }
            claims = []
            continue


        # detect ROLE first (role → company → duration)
        if (
            current is None
            and not re.search(DATE_PATTERN, line.lower(),re.VERBOSE)
            and any(
               re.search(rf"\b{k}\b", line.lower())
                for k in ROLE_KEYWORDS
            )
        ):
            current = {
                "company": "",
                "role": line,
                "duration": "",
                "tools": []
            }
            claims = []
            continue

        # detect COMPANY after role
        if (
            current
            and current["role"]
            and not current["company"]
            and not re.search(DATE_PATTERN, line.lower(),re.VERBOSE)
            and "|" not in line
        ):
            current["company"] = line
            continue

        # 1. Detect company name line (start of a new experience)
        if (
            "|" not in line
            and not line.startswith("-")
            and re.search(DATE_PATTERN, line.lower(),re.VERBOSE)
            and not line.strip().lower().startswith((
            "jan","feb","mar","apr","may","jun",
            "jul","aug","sep","oct","nov","dec",
            "0","1","2","3","4","5","6","7","8","9"
            ))
        ):
            # Save previous experience before starting new one
            if current:
                experiences.append(
                    Experience(
                        role=current["role"],
                        company=current["company"],
                        duration=current["duration"],
                        claims=claims,
                        tools=current["tools"]
                    )
                )
                claims = []

            # Split company and duration using date tokens
            match = re.search(
                r"(.*?)(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4}).*)",
                line.lower()
            )

            if match:
                company = match.group(1).strip().title()
                duration = match.group(2).strip()
            else:
                company = line
                duration = ""

            current = {
                "company": company,
                "role": "",
                "duration": duration,
                "tools": []
            }
            continue

        # Detect DURATION on a seperate line
        if current and not current["duration"] and re.search(DATE_PATTERN, line.lower(),re.VERBOSE):
            current["duration"] = line
            continue

        # Detect ROLE | TOOLS
        if current and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            current["role"] = parts[0]
            if len(parts) > 1:
                current["tools"] = [t.strip() for t in parts[1].split(",")]
            continue

        # Detect TOOLS on a seperate line
        if (
            current
            and current["role"]
            and not current["tools"]
            and (
                line.lower().startswith("tools")
                or "," in line
                and not re.match(
                r"^(developed|designed|implemented|created|built|improved|optimized|researched|maintained|collaborated)",
                line.lower())
            )
        ):
            tools_line = line.split(":", 1)[-1]
            current["tools"] = [t.strip() for t in tools_line.split(",")]
            continue

        # Detect CLAIMS
        if current:
            line = line.lstrip("•\u2022- ").strip()
            claims.append(line)

    # Save LAST experience
    if current:
        experiences.append(
            Experience(
                role=current["role"],
                company=current["company"],
                duration=current["duration"],
                claims=claims,
                tools=current["tools"]
            )
        )

    return experiences

def coalesce_lines(lines):
    """Merge continuation lines that appear to be wrapped text."""
    merged = []
    buffer = ""

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # bullet → flush buffer
        if stripped.startswith(("•", "-", "–")):
            if buffer:
                merged.append(buffer.strip())
                buffer = ""
            merged.append(stripped)
            continue

        # If buffer is empty, start a new one
        if not buffer:
            buffer = stripped
            continue

        # Check if this looks like a new section/line (starts with capital and buffer ends with period)
        # or if the line looks like a project title (short, all caps indicator words, or is single short phrase)
        '''is_new_line = (
            (buffer.endswith(".") and stripped[0].isupper()) or
            stripped.startswith("Tools") or
            stripped.startswith("Tech") or
            (len(stripped.split()) <= 8 and stripped[0].isupper() and 
             not buffer.endswith(",") and not buffer.endswith("–"))
        )'''
        is_new_line = (
            (buffer.endswith(".") and stripped[0].isupper()) or
            stripped.startswith(("Tools", "Tech", "Stack"))
        )

        if is_new_line:
            merged.append(buffer.strip())
            buffer = stripped
        else:
            # continuation - append to buffer
            buffer += " " + stripped

    if buffer:
        merged.append(buffer.strip())

    return merged


def parse_projects_ai_soln(lines):
    lines = coalesce_lines(lines)

    projects = []
    current = None
    claims = []
    incomplete_claim = None  # Track incomplete claims (those not ending with period)

    for line in lines:
        lower = line.lower()

        # stop condition
        if lower in ["achievements", "experience", "skills", "education"]:
            break

        # bullet → claim
        if line.startswith(("•", "-", "–")):
            if current:
                claim = line.lstrip("•–- ").strip()
                if incomplete_claim:
                    incomplete_claim += " " + claim
                    if incomplete_claim.endswith("."):
                        claims.append(incomplete_claim)
                        incomplete_claim = None
                else:
                    if claim.endswith("."):
                        claims.append(claim)
                    else:
                        incomplete_claim = claim
            continue

        # Handle pipe-separated format: "Project | Tools"
        if "|" in line and not line.startswith("-"):
            # Flush incomplete claim
            if incomplete_claim:
                claims.append(incomplete_claim)
                incomplete_claim = None
            
            # Save previous project
            if current:
                projects.append(
                    Project(
                        name=current["name"],
                        claims=claims,
                        tools=current["tools"]
                    )
                )
            
            # Parse pipe-separated line
            parts = [p.strip() for p in line.split("|")]
            name = parts[0]
            tools = [t.strip() for t in parts[1].split(",")] if len(parts) > 1 else []
            
            current = {"name": name, "tools": tools}
            claims = []
            continue

        # tech stack / tools
        if lower.startswith(("tech stack", "tools:", "stack:")):
            # Flush incomplete claim
            if incomplete_claim:
                claims.append(incomplete_claim)
                incomplete_claim = None
            
            if current:
                tools_line = line.split(":", 1)[-1]
                current["tools"] = [t.strip() for t in tools_line.split(",")]
            continue

        # project title detection (for non-pipe format): looks like project title if:
        # - doesn't end with period (likely not a claim)
        # - not too long (not a full description)
        # - either we have no current project OR we have accumulated claims
        is_project_title = (
            not line.endswith(".")
            and len(line.split()) <= 12
            and not line.startswith("•")
            and not lower.startswith(("aims", "developed", "implemented", "includes", "tested", "currently", "involved", "over", "focused", "data", "system"))
        )

        if is_project_title and (current is None or claims):
            # Flush incomplete claim
            if incomplete_claim:
                claims.append(incomplete_claim)
                incomplete_claim = None
            
            # Save previous project
            if current:
                projects.append(
                    Project(
                        name=current["name"],
                        claims=claims,
                        tools=current["tools"]
                    )
                )
            current = {"name": line, "tools": []}
            claims = []
            continue

        # claim (add if project exists)
        if current:
            if incomplete_claim:
                # Append to incomplete claim
                incomplete_claim += " " + line
                if incomplete_claim.endswith("."):
                    claims.append(incomplete_claim)
                    incomplete_claim = None
            else:
                # Start new claim or buffer if not ending with period
                if line.endswith("."):
                    claims.append(line)
                else:
                    incomplete_claim = line

    # flush last incomplete claim and project
    if incomplete_claim:
        claims.append(incomplete_claim)
    
    if current:
        projects.append(
            Project(
                name=current["name"],
                claims=claims,
                tools=current["tools"]
            )
        )

    return projects



# ---------------- MAIN ----------------

def parse_resume(resume_id: str):
    pdf_path = RAW_DIR / f"{resume_id}.pdf"
    out_path = PARSED_DIR / f"{resume_id}.json"

    lines = extract_text_from_pdf(pdf_path)
    sections = split_by_sections(lines)
    print("SECTIONS FOUND:", sections.keys())

    resume = Resume(
        resume_id=resume_id,
        metadata=Metadata(
            parsed_at=datetime.utcnow().isoformat(),
            parser_version=PARSER_VERSION
        ),
        education=[],                     # explicitly ignored
        skills=parse_skills(sections.get("skills", [])),
        experience=parse_experience(sections.get("experience", [])),
        projects=parse_projects_ai_soln(sections.get("projects", [])) # used AI's solution, modify to use old one if we stick to only one format 
    )

    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(resume.model_dump(), f, indent=2) #apparently dict() is outdated

    return out_path


def parse_resume_to_dict(pdf_path: Path) -> dict:
    """
    Parse a resume from a file path and return the dictionary directly.
    Does NOT write to disk.
    """
    lines = extract_text_from_pdf(pdf_path)
    sections = split_by_sections(lines)

    resume = Resume(
        resume_id=pdf_path.stem,
        metadata=Metadata(
            parsed_at=datetime.utcnow().isoformat(),
            parser_version=PARSER_VERSION
        ),
        education=[],  # explicitly ignored
        skills=parse_skills(sections.get("skills", [])),
        experience=parse_experience(sections.get("experience", [])),
        projects=parse_projects(sections.get("projects", []))
    )
    
    return resume.dict()
