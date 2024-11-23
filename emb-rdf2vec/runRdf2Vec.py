# Importing Packages
import sys

sys.path.append('/home/ricciard0.dc/RDF2Vec_Structure')

from pyrdf2vec.graphs import kg
from pyrdf2vec.graphs.vertex import Vertex
from pyrdf2vec.rdf2vec import RDF2VecTransformer
from pyrdf2vec.embedders import Word2Vec
from pyrdf2vec.samplers import UniformSampler, ObjFreqSampler, PredFreqSampler, PageRankSampler
from pyrdf2vec.walkers import RandomWalker, WLWalker, WalkletWalker

import buildGraph as bg
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import manifold

from tqdm import tqdm

def main(ontologySet,annotationSet,annotationType,outputPath = '/home/ricciard0.dc/RDF2Vec_Structure/emb-rdf2vec/output/' ):
    # Creating a pyrdf2vec graph
    g,ents = bg.construct_kg(ontologySet,annotationSet,annotationType)
    g_pyrdf2vec = kg.KG(mul_req=False)
    for (s, p, o) in tqdm(g, desc="Creating Pyrdf2vec Graph", unit="KG Facts"):
        s_v = Vertex(str(s))
        o_v = Vertex(str(o))
        p_v = Vertex(str(p), predicate=True, vprev=s_v, vnext=o_v)
        g_pyrdf2vec.add_vertex(s_v)
        g_pyrdf2vec.add_vertex(p_v)
        g_pyrdf2vec.add_vertex(o_v)
        g_pyrdf2vec.add_edge(s_v, p_v)
        g_pyrdf2vec.add_edge(p_v, o_v)

    # Defining rdf2vec paramenters
    vector_size = 128
    n_walks = 500
    type_word2vec = 'skip-gram'
    walk_depth = 4
    walker_type = 'random'
    sampler_type = 'uniform'

    # Defining the word2vec strategy
    if type_word2vec == 'CBOW':
        sg_value = 0
    elif type_word2vec == 'skip-gram':
        sg_value = 1

    # Defining sampling strategy 
    if sampler_type.lower() == 'uniform':
        sampler = UniformSampler()
    elif sampler_type.lower() == 'predfreq':
        sampler = PredFreqSampler()
    elif sampler_type.lower() == 'objfreq':
        sampler = ObjFreqSampler()

    # Defining warker strategy
    if walker_type.lower() == 'random':
        walker = RandomWalker(max_depth=walk_depth, max_walks=n_walks, sampler = sampler)
    elif walker_type.lower() == 'wl':
        walker = WLWalker(max_depth=walk_depth, max_walks=n_walks, sampler = sampler)
    elif walker_type.lower() == 'walklet':
        walker = WalkletWalker(max_depth=walk_depth, max_walks=n_walks, sampler = sampler)


    # Training RDF2Vec embeddings
    print("Training RDF2Vec embeddings")    
    transformer = RDF2VecTransformer(Word2Vec(vector_size=vector_size, sg=sg_value), walkers=[walker])
    embeddings, literals = transformer.fit_transform(g_pyrdf2vec, ents)

    ######### Write the files #########
    with open(outputPath + f'rdf2vec_128_Embeddings.txt', 'w') as file:
        for entity, embedding in tqdm(zip(ents, embeddings), desc="Writing Embeddings", unit="Entities"):
            # Join the entity and its embedding values as a single line
            line = f"{entity} " + " ".join(map(str, embedding))
            file.write(line + '\n')

    print('Process Ran Successfully')

if __name__ == "__main__":
     # Load the knowledge graph
    ontologySet = ['/home/ricciard0.dc/mimicReadmission/mimicreadmission/Data/ontologies/Thesaurus.owl',
                '/home/ricciard0.dc/mimicReadmission/mimicreadmission/Data/ontologies/LOINC.rdf',
                '/home/ricciard0.dc/mimicReadmission/mimicreadmission/Data/ontologies/dron.owl',
                '/home/ricciard0.dc/mimicReadmission/mimicreadmission/Data/ontologies/ICD9CM.ttl'
                   ]
    annotationSet = ['/home/ricciard0.dc/mimicReadmission/mimicreadmission/Data/annotations/AnnotationsInitialDiagnosis.csv',
                    '/home/ricciard0.dc/mimicReadmission/mimicreadmission/Data/annotations/AnnotationsLabEvents.csv',
                    '/home/ricciard0.dc/mimicReadmission/mimicreadmission/Data/annotations/AnnotationsPrescriptions.csv',
                    '/home/ricciard0.dc/mimicReadmission/mimicreadmission/Data/annotations/AnnotationsProcedures.csv',
                    '/home/ricciard0.dc/mimicReadmission/mimicreadmission/Data/annotations/AnnotationsFinalDiagnosis.csv'
                    ]
                    
    annotationType = ['hasInitialDiagnosis',
                    'hasLabEvent',
                    'hasPrescription',
                    'hasProcedure',
                    'hasFinalDiagnosis'
                      ]

    main(ontologySet,annotationSet,annotationType)