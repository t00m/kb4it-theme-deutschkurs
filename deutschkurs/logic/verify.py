"""Hook for kb4it verify: the metadata checks without a build."""

from .checks import check_properties


def verify(repo, docs):
    """One line per metadata problem; docs maps file name to {key: [values]}."""
    settings = (repo or {}).get("deutschkurs") or {}
    topics = settings.get("topics")
    lines = []
    for name in sorted(docs):
        lines.extend(str(p) for p in check_properties(name, docs[name], topics))
    return lines
