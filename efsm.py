# Importul modulului random pentru generare aleatoare de numere (folosit la cromozomi, mutatii, selectii etc.)
import random

# ---------------------------
# DEFINIREA FSM-ului (Finite State Machine) pentru clasa Book
# ---------------------------
class BookFSM:
    def __init__(self):
        # Initializam starea initiala ca "A" (Available - disponibil)
        self.state = 'A'
        # ID-ul clientului care a rezervat cartea (initial niciunul)
        self.resID = None
        # ID-ul clientului care a imprumutat cartea (initial niciunul)
        self.borID = None

    def res(self, x):
        # Functia de rezervare a unei carti
        # Guard: x > 0 (nu poti rezerva cu un ID negativ sau zero)
        if x <= 0:
            return False
        if self.state == 'A':  # Daca cartea e disponibila
            self.resID = x
            self.state = 'R'  # Devine rezervata
        elif self.state == 'B':  # Daca era deja imprumutata
            self.resID = x
            self.state = 'BR'  # Devine atat rezervata cat si imprumutata
        return True

    def bor(self, x):
        # Functia de imprumut
        # Din stare A, poate fi imprumutata de oricine cu ID pozitiv
        # Din stare R sau BR, doar de cel care a rezervat
        if self.state == 'A':
            if x <= 0:
                return False
            self.borID = x
            self.state = 'B'
            return True
        if self.state in ['R', 'BR']:
            if x != self.resID:
                return False
            self.borID = x
            self.state = 'BR'
            return True
        return False

# ---------------------------
# Secventa (path-ul) de tranzitii pe care dorim sa o testam
# ---------------------------
# Se doreste o rezervare x1 > 0 si apoi un imprumut cu x2 == x1
path = [
    ('res', ('>', 0)),          # rezervare cu x1 > 0
    ('bor', ('==', 'resID')),   # imprumutare cu x2 == resID
]

# ---------------------------
# Parametrii algoritmului genetic
# ---------------------------
POP_SIZE = 20       # cate "solutii" (cromozomi) in populatie
GENERATIONS = 30    # cate iteratii (generatii) rulam algoritmul
MUT_RATE = 0.1      # probabilitatea de mutatie pe gena
CROSS_RATE = 0.7    # probabilitatea de crossover (incrucisare)
GENE_RANGE = (-10, 10)  # intervalul de unde se aleg valorile genelor
K = 1.0             # constanta folosita la penalizare (fitness)

# ---------------------------
# Calculul distantei fata de conditia (guard-ul) dorita
# ---------------------------
def branch_distance_rel(op, a, b):
    # Functie care returneaza cat de "departe" e valoarea a de a satisface conditia cu b
    if op == '==': return 0 if a == b else abs(a - b) + K
    if op == '!=': return 0 if a != b else K
    if op == '<':  return 0 if a < b else (a - b) + K
    if op == '<=': return 0 if a <= b else (a - b) + K
    if op == '>':  return 0 if a > b else (b - a) + K
    if op == '>=': return 0 if a >= b else (b - a) + K
    return float('inf')  # fallback daca operatorul nu e cunoscut

def normalize(d):
    # Normalizeaza distanta (scalare intre 0 si 1)
    return 1.0 - 1.0 / (1.0 + d)

# ---------------------------
# Functie de fitness (cat de buna e o solutie/cromozom)
# ---------------------------
def fitness(chrom):
    fsm = BookFSM()               # instanta noua de FSM la fiecare test
    m = len(path)                # numarul de tranzitii din path
    approach = m                # initial presupunem ca nu trecem nicio tranzitie
    n_executed = 0

    print(f"\nEvaluating candidate: {chrom}")

    for i, gene in enumerate(chrom):
        method, (op, ref) = path[i]
        b = ref if isinstance(ref, int) else getattr(fsm, ref)  # valoare de comparatie: constanta sau din FSM
        d = branch_distance_rel(op, gene, b)

        print(f"  {method}({gene}) ? {op} {b} → d = {d:.2f}")

        if d > 0:  # daca nu a satisfacut guard-ul
            approach = m - n_executed
            fitness_value = approach + normalize(d)
            print(f"  Guard failed, fitness = {fitness_value:.3f}")
            return fitness_value

        getattr(fsm, method)(gene)  # executa tranzitia
        print(f"  Passed. State: {fsm.state}")
        n_executed += 1

    print("  All transitions passed!")
    return 0.0  # toate trecerile au reusit, fitness ideal

# ---------------------------
# Initializarea populatiei
# ---------------------------
def init_population(n_genes):
    return [[random.randint(*GENE_RANGE) for _ in range(n_genes)] for _ in range(POP_SIZE)]

# ---------------------------
# Selectie (turneu)
# ---------------------------
def select(pop, fits):
    selected = []
    for _ in range(POP_SIZE):
        i, j = random.sample(range(POP_SIZE), 2)
        selected.append(pop[i] if fits[i] < fits[j] else pop[j])
    return selected

# ---------------------------
# Incrucisare si mutatie (reproducerea generatiei urmatoare)
# ---------------------------
def breed(parent1, parent2):
    if random.random() < CROSS_RATE:
        cx = random.randint(1, len(parent1) - 1)
        child = parent1[:cx] + parent2[cx:]  # recombinare
    else:
        child = parent1[:]
    for i in range(len(child)):
        if random.random() < MUT_RATE:
            child[i] = random.randint(*GENE_RANGE)
    return child

# ---------------------------
# Algoritmul genetic propriu-zis
# ---------------------------
def ga_search():
    pop = init_population(len(path))
    for gen in range(GENERATIONS):
        fits = [fitness(ind) for ind in pop]
        print(f"\nGeneration {gen} | Best fitness: {min(fits):.3f}")
        for i, ind in enumerate(pop):
            print(f"  #{i:2}: {ind} → fitness: {fits[i]:.3f}")
        if min(fits) == 0.0:
            idx = fits.index(0.0)
            print(f"\nFound valid input in generation {gen}: {pop[idx]}")
            return pop[idx], gen
        selected = select(pop, fits)
        pop = [breed(random.choice(selected), random.choice(selected)) for _ in range(POP_SIZE)]

    # Daca nu s-a gasit nimic perfect
    fits = [fitness(ind) for ind in pop]
    idx = fits.index(min(fits))
    print(f"\nNo exact match found. Best candidate: {pop[idx]} with fitness {fits[idx]:.3f}")
    return pop[idx], GENERATIONS

# ---------------------------
# Punctul de start (main)
# ---------------------------
if __name__ == '__main__':
    solution, gen = ga_search()
    print(f"\nFinal result after {gen} generations: {solution}")