"""Baseline entity extraction using regex and heuristics for business cards."""

import re
from typing import List, Dict
from src.utils import logger, get_empty_entity_dict, sanitize_text

EMAIL_PATTERN: str = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
PHONE_PATTERN: str = r"[\+]?[\d\s\-\(\)\.]{7,20}"
WEBSITE_PATTERN: str = (
    r"(?:https?://)?(?:www\.)?[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?"
)

DESIGNATION_KEYWORDS: List[str] = [
    "ceo", "cto", "cfo", "coo", "cmo", "vp", "president", "director",
    "manager", "engineer", "developer", "designer", "analyst", "consultant",
    "specialist", "coordinator", "administrator", "executive", "officer",
    "head", "lead", "senior", "junior", "associate", "intern", "founder",
    "co-founder", "partner", "supervisor", "architect", "scientist",
    "researcher", "professor", "dr", "doctor", "attorney", "lawyer",
    "accountant", "advisor", "chairman", "secretary", "treasurer",
    "representative", "sales", "marketing", "operations", "technology",
    "information", "human resources", "hr", "it", "chief",
]

ADDRESS_KEYWORDS: List[str] = [
    "street", "st", "road", "rd", "avenue", "ave", "boulevard", "blvd",
    "drive", "dr", "lane", "ln", "way", "court", "ct", "plaza", "plz",
    "suite", "ste", "floor", "fl", "building", "bldg", "apt", "unit",
    "po box", "p.o. box", "zip", "pin", "state", "city", "country",
]


def _extract_emails(text_lines: List[str]) -> List[str]:
    """Extract email addresses from text lines.

    Args:
        text_lines: List of text strings to search.

    Returns:
        List[str]: List of found email addresses.
    """
    emails = []
    for line in text_lines:
        found = re.findall(EMAIL_PATTERN, line, re.IGNORECASE)
        emails.extend(found)
    return emails


def _extract_phones(text_lines: List[str]) -> List[str]:
    """Extract phone numbers from text lines.

    Args:
        text_lines: List of text strings to search.

    Returns:
        List[str]: List of found phone numbers.
    """
    phones = []
    for line in text_lines:
        if re.search(EMAIL_PATTERN, line):
            continue
        if re.search(WEBSITE_PATTERN, line):
            cleaned = re.sub(WEBSITE_PATTERN, "", line)
        else:
            cleaned = line
        found = re.findall(PHONE_PATTERN, cleaned)
        for phone in found:
            digits = re.sub(r"[^\d]", "", phone)
            if 7 <= len(digits) <= 15:
                phones.append(sanitize_text(phone))
    return phones


def _extract_websites(text_lines: List[str]) -> List[str]:
    """Extract website URLs from text lines.

    Args:
        text_lines: List of text strings to search.

    Returns:
        List[str]: List of found website URLs.
    """
    websites = []
    for line in text_lines:
        if re.search(EMAIL_PATTERN, line):
            continue
        found = re.findall(WEBSITE_PATTERN, line, re.IGNORECASE)
        for site in found:
            if not re.search(EMAIL_PATTERN, site):
                websites.append(sanitize_text(site))
    return websites


def _is_designation(text: str) -> bool:
    """Check if text likely contains a job designation.

    Args:
        text: Text string to check.

    Returns:
        bool: True if the text appears to be a designation.
    """
    lower_text = text.lower()
    for keyword in DESIGNATION_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, lower_text):
            return True
    return False


def _is_address(text: str) -> bool:
    """Check if text likely contains an address.

    Args:
        text: Text string to check.

    Returns:
        bool: True if the text appears to be an address.
    """
    lower_text = text.lower()
    for keyword in ADDRESS_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, lower_text):
            return True
    if re.search(r"\b\d{5,6}\b", text):
        return True
    return False


def _has_mostly_digits(text: str) -> bool:
    """Check if text is mostly digits (likely a phone number line).

    Args:
        text: Text string to check.

    Returns:
        bool: True if over 50% of the characters are digits.
    """
    digits = sum(1 for c in text if c.isdigit())
    total = len(text.replace(" ", ""))
    if total == 0:
        return False
    return digits / total > 0.5


def extract_entities(text_lines: List[str]) -> Dict[str, str]:
    """Extract business card entities from OCR text using regex and heuristics.

    Args:
        text_lines: List of text strings extracted from a business card.

    Returns:
        Dict[str, str]: Dictionary mapping entity fields to extracted values.
    """
    entities = get_empty_entity_dict()

    if not text_lines:
        logger.warning("No text lines provided for entity extraction")
        return entities

    emails = _extract_emails(text_lines)
    phones = _extract_phones(text_lines)
    websites = _extract_websites(text_lines)

    if emails:
        entities["Email"] = emails[0]
    if phones:
        entities["Phone"] = ", ".join(phones[:3])
    if websites:
        entities["Website"] = websites[0]

    used_lines = set()
    for i, line in enumerate(text_lines):
        if re.search(EMAIL_PATTERN, line):
            used_lines.add(i)
        if _has_mostly_digits(line):
            used_lines.add(i)
        if re.search(WEBSITE_PATTERN, line) and not re.search(EMAIL_PATTERN, line):
            used_lines.add(i)

    remaining_lines = [
        (i, line) for i, line in enumerate(text_lines) if i not in used_lines
    ]

    designations = []
    addresses = []
    name_candidates = []
    company_candidates = []

    for i, line in remaining_lines:
        clean_line = sanitize_text(line)
        if not clean_line:
            continue

        if _is_designation(clean_line):
            designations.append(clean_line)
            used_lines.add(i)
        elif _is_address(clean_line):
            addresses.append(clean_line)
            used_lines.add(i)
        elif len(clean_line.split()) <= 4 and clean_line.replace(" ", "").isalpha():
            name_candidates.append((i, clean_line))
        else:
            company_candidates.append((i, clean_line))

    if designations:
        entities["Designation"] = designations[0]

    if addresses:
        entities["Address"] = ", ".join(addresses)

    if name_candidates:
        entities["Name"] = name_candidates[0][1]
        if len(name_candidates) > 1:
            company_candidates.insert(0, name_candidates[1])
    elif remaining_lines:
        unclassified = [
            (i, line) for i, line in remaining_lines if i not in used_lines
        ]
        if unclassified:
            entities["Name"] = sanitize_text(unclassified[0][1])

    remaining_company = [
        (i, line)
        for i, line in company_candidates
        if i not in used_lines and sanitize_text(line)
    ]
    if remaining_company:
        entities["Company"] = remaining_company[0][1]

    logger.info("Baseline extraction complete: %s", entities)
    return entities
