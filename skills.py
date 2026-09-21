# skills.py
import os, re

SKILLS_DIR = "skills"

def discover_skills() -> list[dict]:
    """Scans skills/ and extracts only the frontmatter (name + description)."""
    skills = []
    for skill_name in os.listdir(SKILLS_DIR):
        skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        with open(skill_path) as f:
            content = f.read()
        match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        meta = {}
        if match:
            for line in match.group(1).splitlines():
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
        skills.append({"name": meta.get("name", skill_name), "description": meta.get("description", "")})
    return skills


def load_skill(skill_name: str) -> str:
    """Loads the full content (minus frontmatter) of a given skill."""
    skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
    with open(skill_path) as f:
        content = f.read()
    return re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL).strip()