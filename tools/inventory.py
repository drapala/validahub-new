#!/usr/bin/env python3
import json, os, sys
ROOT = os.getcwd()

LANG_MARKERS = {
    "python": ["pyproject.toml", "requirements.txt"],
    "node": ["package.json"],
    "java": ["build.gradle", "pom.xml", "gradlew"],
    "go": ["go.mod"]
}

def is_service_dir(path):
    files = set(os.listdir(path))
    for lang, markers in LANG_MARKERS.items():
        if any(m in files for m in markers):
            return lang
    return None

def walk_services():
    services = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # pular diretórios comuns
        skip = any(seg.startswith('.') or seg in {'node_modules','venv','.venv','dist','build','.git'} for seg in dirpath.split(os.sep))
        if skip: 
            continue
        lang = is_service_dir(dirpath)
        if lang:
            rel = os.path.relpath(dirpath, ROOT)
            name = os.path.basename(rel)
            services.append({"name": name, "path": rel.replace("\\","/"), "lang": lang})
    return services

def find_rules_dirs():
    candidates = []
    for d in ["rules", "rulesets", "data/rules", "config/rules"]:
        if os.path.isdir(d):
            candidates.append(d)
    # varrer outras ocorrências
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if 'rules.yml' in filenames or 'mappings.yml' in filenames:
            candidates.append(os.path.relpath(dirpath, ROOT).replace("\\","/"))
    return sorted(set(candidates))

def main():
    services = walk_services()
    rules_dirs = find_rules_dirs()
    out = {"services": services, "rules_dirs": rules_dirs}
    os.makedirs("tools", exist_ok=True)
    with open("tools/services.json","w",encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    sys.exit(main())