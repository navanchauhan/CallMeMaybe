from typing import List
from langchain.agents import tool

from dotenv import load_dotenv
load_dotenv()

import os

CONTACTS = [
    {
        "name": "Greg",
        "phone" : os.getenv("TEST_PHONE_NUMBER")
    }
]

@tool("get_all_contacts")
def get_all_contacts(placeholder: str) -> List[dict]:
    """Returns all contacts in the user's phone book."""
    return CONTACTS