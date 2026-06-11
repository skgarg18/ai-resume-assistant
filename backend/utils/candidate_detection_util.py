from services.vector_db_store import chat_collection
from typing import List

def detect_candidates(question: str):

    data = chat_collection.get()

    matched_candidates = set()

    candidate_lookup = {}

    for meta in data["metadatas"]:

        full_name = meta["candidate"]

        # Skip duplicates
        if full_name in candidate_lookup.values():
            continue

        # Store full name
        candidate_lookup[full_name.lower()] = full_name

        # Store first name and last name
        parts = full_name.split()

        for part in parts:
            candidate_lookup[part.lower()] = full_name

    question = question.lower()

    for key, full_name in candidate_lookup.items():

        if key in question:
            matched_candidates.add(full_name)

    return list(matched_candidates)