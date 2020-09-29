import re
import uuid
import functools


@functools.lru_cache(maxsize=128, typed=False)
def get_job_id(protein_sequence, ligand_sequence, mutations):
    return str(uuid.uuid4())


def check_aa_sequence(aa_sequence: str) -> bool:
    return re.match("^[GVALICMFWPDESTYQNKRH]+$", aa_sequence) is not None


def check_mutations(mutations: str) -> bool:
    for mutation in mutations.split(","):
        if re.match("^[GVALICMFWPDESTYQNKRH][1-9]+[0-9]*[GVALICMFWPDESTYQNKRH]$", mutation) is None:
            return False
    return True


def mutation_matches_sequence(aa_sequence: str, mutation: str) -> bool:
    wt, pos, _ = mutation[0], int(mutation[1:-1]), mutation[-1]
    return aa_sequence[pos - 1] == wt
