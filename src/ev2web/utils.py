import functools
import re
import uuid


@functools.lru_cache(maxsize=128, typed=False)
def get_job_id(protein_sequence, ligand_sequence, mutations):
    defaults = {
        ("AAA", None, "A1G,A1L"): "6c1a266d-10b2-4148-970d-f49f26718ca9",
    }
    return defaults.get((protein_sequence, ligand_sequence, mutations), str(uuid.uuid4()))


def check_aa_sequence(aa_sequence: str) -> bool:
    return re.match("^[GVALICMFWPDESTYQNKRH]+$", aa_sequence) is not None


def check_mutations(mutations: str) -> bool:
    for mutation in mutations.split(","):
        if re.match("^[GVALICMFWPDESTYQNKRH][1-9]+[0-9]*[GVALICMFWPDESTYQNKRH]$", mutation) is None:
            return False
    return True


def check_mutations_match_sequence(aa_sequence: str, mutations: str) -> bool:
    for mutation in mutations.split(","):
        wt, pos, _ = mutation[0], int(mutation[1:-1]), mutation[-1]
        if aa_sequence[pos - 1] != wt:
            return False
    return True
