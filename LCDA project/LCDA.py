import time
import copy
import networkx as nx   # librairie pour faire des graphes
import matplotlib.pyplot as plt  # librairie pour afficher le graphe

from derivation import *
from facts import *
from rule import *
from context import *
from dataset import *

def anomaly_Detection(rules, facts, context, negative_rules):
    # compteur de dérivations
    k = 0
    start = time.perf_counter()

    # listes pour comparer les résultats entre deux tours
    previous_result = []
    current_result = []

    # je crée un graphe orienté pour représenter les règles négatives
    G = nx.DiGraph()

    while True:
        k += 1
        negative_predicates = []

        # je découpe les faits selon le contexte
        partition_context = fact_Partition(facts, context)

        # si on a des règles négatives
        if len(negative_rules) > 0:
            combined_facts = generate_combinations(facts, len(facts))

            for rule in negative_rules:
                # j’ajoute chaque règle comme un nœud dans le graphe
                G.add_node(rule.getRuleID(), predicates=rule.getRuleBodyPredicates())

                # je teste la règle sur les combinaisons de faits
                for fact_partition in combined_facts:
                    result = derive_method(rule, fact_partition)

                    if result is not None:
                        for item in result:
                            if 'alert' in item.keys():
                                print("⚠️ Anomaly Detected!")
                                print("Rule ID:", rule.getRuleID())
                                print("Predicates:", rule.getRuleBodyPredicates())
                                end = time.perf_counter()
                                print("Processing time:", end - start)

                                # j’affiche le graphe avant de quitter
                                visualize_negative_rules(G)
                                return
                    else:
                        # si la règle n’a rien donné, je garde ses prédicats
                        negative_predicates.append(rule.getRuleBodyPredicates())
        else:
            print("Pas de règles négatives.")
            end = time.perf_counter()
            print("Processing time:", end - start)
            visualize_negative_rules(G)
            return

        # maintenant je regarde le contexte
        for c in context:
            conclusions = context_conclusion(c)
            # j’aplatis la liste des conclusions
            flat_conclusions = [item for sublist in conclusions for item in sublist]

            for p in negative_predicates:
                # je cherche les éléments communs entre conclusions et prédicats
                common = set(flat_conclusions).intersection(p)
                if len(common) == 0:
                    continue
                else:
                    # je génère des combinaisons de faits
                    com = generate_combinations(facts, len(facts))
                    for val in com:
                        derivation = context_make_derivation(c, val)
                        if derivation is not None and len(derivation) > 0:
                            current_result.append(derivation)
                            # j’ajoute une arête entre le contexte et les prédicats
                            for pred in p:
                                G.add_edge(c.getContextID(), pred)

        # si les résultats n’ont pas changé → on arrête
        if previous_result == current_result:
            print("Aucun nouveau fait dérivé.")
            end = time.perf_counter()
            print("Processing time:", end - start)
            visualize_negative_rules(G)
            return
        else:
            # sinon je mets à jour et j’ajoute les nouveaux faits
            previous_result = copy.deepcopy(current_result)
            for result in current_result:
                for item in result:
                    facts.add(item)


def visualize_negative_rules(G):
    """ Fonction pour afficher le graphe des règles négatives """
    plt.figure(figsize=(8,6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="gray",
            node_size=2000, font_size=10)
    labels = nx.get_node_attributes(G, 'predicates')
    nx.draw_networkx_labels(G, pos, labels={k: str(v) for k,v in labels.items()},
                            font_color="red")
    plt.title("Graph des règles négatives")
    plt.show()
