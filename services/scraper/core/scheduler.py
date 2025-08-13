import os

def parse_scope(scope: str):
    # format: <tier>:<code|*>:<entity|*>
    # examples: federal:*:daily | provincial:on:representatives | city:toronto:bills
    parts = scope.split(":")
    return (parts + ["*","*","*"])[:3]

def enabled():
    return os.getenv("SCHEDULER_ENABLED","true").lower()=="true"