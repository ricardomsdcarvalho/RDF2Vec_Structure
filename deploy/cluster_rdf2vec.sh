#!/bin/bash
#SBATCH --job-name=rdf2vec                                        # Job name
#SBATCH --partition=tier2                                         # Partition
#SBATCH --nodelist=liseda-01                                      # Node
#SBATCH --nodes=1                                                 # Number of nodes
#SBATCH --cpus-per-task=4                                         # Number of CPUs
#SBATCH --mem=24G                                                 # Memory
#SBATCH --time=08:00:00                                           # Time limit
#SBATCH --gres=gpu:1                                              # Number of GPUs
#SBATCH --output=/home/rcarvalho/exp/Embeddings/rdf2vec_job_%j_out.log       # Output file (includes job ID)
#SBATCH --error=/home/rcarvalho/exp/Embeddings/rdf2vec_job_%j_err.log        # Error file (includes job ID)



#uv venv .venv
#SEMANTIC LAYER EMBEDDINGS
uv run python /home/rcarvalho/rdf2vec_structure/emb-rdf2vec/inUseRdf2Vec.py \
       --entities home/rcarvalho/datasets/ICU/Ncit_semantic_notime/entity2id.txt\
       --relations home/rcarvalho/datasets/ICU/Ncit_semantic_notime/relation2id.txt\
       --triples home/rcarvalho/datasets/ICU/Ncit_semantic_notime/OENT.txt\
       --targets /home/rcarvalho/datasets/Targets.txt\
       --outpath /home/rcarvalho/exp/Embeddings/ \
       --experiment rdf2vec_icuNcit_semantic_300 \

#SIMPLE EMBEDDINGS
uv run python /home/rcarvalho/rdf2vec_structure/emb-rdf2vec/inUseRdf2Vec.py \
       --entities home/rcarvalho/datasets/ICU/Ncit_simple_notime/entity2id.txt\
       --relations home/rcarvalho/datasets/ICU/Ncit_simple_notime/relation2id.txt\
       --triples home/rcarvalho/datasets/ICU/Ncit_simple_notime/PENT.txt\
       --targets /home/rcarvalho/datasets/Targets.txt\
       --outpath /home/rcarvalho/exp/Embeddings/ \
       --experiment rdf2vec_icuNcit_simple_300 \
       