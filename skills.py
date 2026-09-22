"""Skills: instruction files the model can load on demand.

A skill is a folder skills/<name>/SKILL.md made of a short header (name + description)
and the full instructions. Only the header goes in the system prompt; the full text is
loaded later, if and when the model asks for it. Skills never do anything: they only
return text.
"""
import os
import re

SKILLS_DIR = "skills"


def discover_skills() -> list[dict]:
    """Scans skills/ and returns only the header (name + description) of each skill."""
    skills = []
    for skill_name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        with open(skill_path) as f:
            content = f.read()
        # The header sits between the two "---" lines at the top of the file.
        match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        meta = {}
        if match:
            for line in match.group(1).splitlines():
                key, _, value = line.partition(":")  # split at the first ":" only
                meta[key.strip()] = value.strip()
        skills.append({"name": meta.get("name", skill_name), "description": meta.get("description", "")})
    return skills


def load_skill(skill_name: str) -> str:
    """Returns the full instructions of a skill (header removed). Read-only: no side effect."""
    skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    with open(skill_path) as f:
        content = f.read()
    return re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL).strip()
