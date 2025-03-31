import argparse
import sys

sys.path.append('/home/rcarvalho/RDF2Vec_Structure')

import buildGraph as bg
import matplotlib.pyplot as plt
import seaborn as sns

from pyrdf2vec.graphs import kg
from pyrdf2vec.graphs.vertex import Vertex
from pyrdf2vec.rdf2vec import RDF2VecTransformer
from pyrdf2vec.embedders import Word2Vec
from pyrdf2vec.samplers import UniformSampler, ObjFreqSampler, PredFreqSampler, PageRankSampler
from pyrdf2vec.walkers import RandomWalker, WLWalker, WalkletWalker
from sklearn import manifold
from tqdm import tqdm


def main(enityFile, triplesFile, relationsFile, targets ,outpath, experimentName):
    '''rdf2vec_icuNcit_simple_300'''

    g, ents = bg.in_use_construct_kg(enityFile, triplesFile, relationsFile)
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
    vector_size = 300
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

    #Training the model
    print(' ⏳ Trainging RDF2Vec embeddings')
    transformer = RDF2VecTransformer(Word2Vec(vector_size=vector_size, sg=sg_value), walkers=[walker])
    embeddings, literals = transformer.fit_transform(g_pyrdf2vec, list(ents))

    #Filter Target Entities
    with open(targets, 'r') as f:
        target_ents = set(line.strip() for line in f.readlines())
    
    ######### Write the files #########
    output_file = outpath + experimentName + '_embeddings.txt'
    with open(output_file, 'w') as file:
        for entity, embedding in tqdm(zip(ents, embeddings), desc="Writing Embeddings", unit="Entities"):
            if entity in target_ents:  # Filter only target entities
                embedding_str = "\t".join(map(str, embedding))  # Tab-separated values
                file.write(f"{entity}\t{embedding_str}\n")  # Match required format

    print(f"        ✅ Filtered embeddings written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Rdf2vec and extract embeddings")
    parser.add_argument("--entities", type=str, required=True, help="Path to enities file")
    parser.add_argument("--relations", type=str, required=True, help="Path to relations file")
    parser.add_argument("--triples", type=str, required=True, help="Path to triples file")
    parser.add_argument("--targets", type=str, required=True, help="Path to target entities file")
    parser.add_argument("--outpath", type=str, required=True, help="Path to output folder")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment name")
    args = parser.parse_args()
    
    main(
        enityFile=args.entities,
        triplesFile=args.triples,
        relationsFile=args.relations,
        targets=args.targets,
        outpath=args.outpath,
        experimentName=args.experiment
    )