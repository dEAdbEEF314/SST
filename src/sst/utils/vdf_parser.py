import re
from typing import Dict

def parse_acf(acf_content: str) -> Dict[str, str]:
    """
    Parse a Steam ACF (VDF) file and extract key-value pairs.
    This simple parser uses regex to extract flat "key" "value" pairs,
    which is sufficient for extracting appid, name, and installdir.
    """
    result = {}
    
    # Match "key" followed by whitespace and "value"
    pattern = re.compile(r'"([^"]+)"\s+"([^"]+)"')
    for match in pattern.finditer(acf_content):
        key, value = match.groups()
        # To handle potential nesting conflicts, we only take the first occurrence
        # or we just rely on the fact that appid, name, installdir are uniquely named at the top levels.
        if key not in result:
            result[key] = value
            
    return result
