import json
import rdflib

from operator import itemgetter
from rdflib.namespace import RDF, OWL, RDFS
from rdflib import URIRef
from tqdm import tqdm

# The format of the input files is allwaays: (id);[annoations]
# as such we can always split by ; and than loop the list

file_formats = {
    ".rdf": "xml",
    ".owl": "xml",
    ".ttl": "turtle",
    # Add other formats if needed
}

def in_use_construct_kg(entityFile,triplesFile,relationFile):
    '''
    The entites and relations files are used to create the KG and are formated as URI \t id
    All files start with a header line, so we skip the first line
    '''

    #Process Entities
    print("Processing Entities")
    ents = set()
    with open(entityFile, 'r') as file:
        for line in file.readlines()[1:]:
            entity, _id = line.split("\t")

            if 'http:' in entity:
                ents.add(entity.strip())
            else:
                #Make a temporary URI for the graph
                entity = f"http://purl.obolibrary.org/obo/{entity.strip()}"
                ents.add(entity)
                #print(f"Entity {entity} is not a valid URL")
    
    #Process Relations
    print("Processing Relations")
    rels = set()
    with open(relationFile, 'r') as file:
        for line in file.readlines()[1:]:
            relation, _id = line.split("\t")
        
            if 'http:' in relation:
                rels.add(relation.strip())
            else:
                #Make a temporary URI for the graph
                relation = f"http://purl.obolibrary.org/obo/{relation.strip()}"
                rels.add(relation)
                print(f"Relation {relation} is not a valid URL")

            rels.add(relation.strip())
            
    #Create the graph
    kg = rdflib.Graph()

    #Parse the triples and update the graph
    print("Processing Triples")
    with open(triplesFile, 'r') as file:
        for line in tqdm(file.readlines()[1:], desc="Loading Annotations", unit="annotation"):
            headEnt, tailEnt, _relation = line.split("\t")

            if 'http:' not in headEnt:
                headEnt = f"http://purl.obolibrary.org/obo/{headEnt.strip()}"
            
            if 'http:' not in tailEnt:
                tailEnt = f"http://purl.obolibrary.org/obo/{tailEnt.strip()}"
            
            if 'http:' not in _relation:
                _relation = f"http://purl.obolibrary.org/obo/{_relation.strip()}"

            if headEnt not in ents:
                ents.add(headEnt.strip())
            if tailEnt not in ents:
                ents.add(tailEnt.strip())
            if _relation not in rels:
                rels.add(_relation.strip())

            print(f"Head: {headEnt} Tail: {tailEnt} Relation: {_relation}")
            kg.add((URIRef(headEnt.strip()), URIRef(_relation), URIRef(tailEnt.strip())))
            kg.add((URIRef(headEnt.strip()), RDF.type, OWL.Class))
            kg.add((URIRef(tailEnt.strip()), RDF.type, OWL.Class))
    
    #Add the relations to the graph
    for rel in rels:
        kg.add((URIRef(rel), RDF.type, OWL.ObjectProperty))

    
    print("🚀 KG created")
    return kg,ents


def construct_kg(ontologySet,annotationSet,annotationType):
    try:
        assert len(annotationSet) == len(annotationSet), "The number of annotationFiles and annotationTypes must be the same"
        # Proceed with the rest of the function if assertion passes
        print("AnnotationTypes and annotationsFiles are correctly matched.")

        kg = rdflib.Graph()
        ents = set()

        for loc in tqdm(range(len(ontologySet)),desc="Loading Ontologies", unit="ontology"):

            extension = ontologySet[loc].split(".")[-1]
            format = file_formats.get(f".{extension.lower()}", None)

            if "ICD9" not in ontologySet[loc]:
                print('PARSING THE ONTOLOGY')
                kg.parse(ontologySet[loc], format=format)

                fileAnnotations = open(annotationSet[loc], "r")
                for annot in tqdm(fileAnnotations.readlines()[:], desc="Loading Annotations", unit="annotation"):
                    annot = annot.lstrip()

                    #Get Head and Tail Entities
                    headInfo, annotations = annot.split(";")[:2]
                    headEnt = f"http://purl.obolibrary.org/obo/{headInfo.split(',')[0]}"

                    ents.update((ent.strip() for ent in annotations.split(",")))

                    if headEnt not in ents:
                        ents.add(headEnt)

                    for urlAnnot in annotations.split(","):
                        kg.add((URIRef(headEnt), URIRef(f"http://purl.obolibrary.org/obo/{annotationType[loc]}"),
                                URIRef(urlAnnot.strip())))
                
                fileAnnotations.close()
                kg.add((URIRef(f"http://purl.obolibrary.org/obo/{annotationType[loc]}"), RDF.type, OWL.ObjectProperty))
            
            #Becasuse the ICD9CM ontology is used two parse two different annotation files
            else:
                print('PARSING THE ONTOLOGY')
                kg.parse(ontologySet[loc], format=format)

                for step in range(2):
                    trueLoc = loc + step
                    fileAnnotations = open(annotationSet[trueLoc], "r")
                    for annot in tqdm(fileAnnotations.readlines()[:], desc="Loading Annotations", unit="annotation"):
                        annot = annot.lstrip()

                        #Get Head and Tail Entities
                        headInfo, annotations = annot.split(";")[:2]
                        headEnt = f"http://purl.obolibrary.org/obo/{headInfo.split(',')[0]}"

                        ents.update((ent.strip() for ent in annotations.split(",")))
                        if headEnt not in ents:
                            ents.add(headEnt)

                        for urlAnnot in annotations.split(","):
                            kg.add((URIRef(headEnt), URIRef(f"http://purl.obolibrary.org/obo/{annotationType[trueLoc]}"),
                                    URIRef(urlAnnot.strip())))
                    
                    fileAnnotations.close()
                    kg.add((URIRef(f"http://purl.obolibrary.org/obo/{annotationType[trueLoc]}"), RDF.type, OWL.ObjectProperty))

    except AssertionError as error:
        print(f"Error: {error} Because the number of AnnotationTypes, AnnotationFiles must be the same")

    #kg.serialize(destination="/home/ricciard0.dc/mimicReadmission/mimicreadmission/data/myKG.xml")

    with open('/home/ricciard0.dc/RDF2Vec_Structure/targetEntities.txt', 'w') as file:
        for ent in ents:
            file.write(f'{ent}\n')

    print("KG created")
    return kg,ents

#if __name__ == '__main__':

    # Files
    #entityFile = '/Users/ricardocarvalho/Documents/Thesis/Data/TkgConstructions/ICU-NCIT/ON.txt'
    #relationFile = '/Users/ricardocarvalho/Documents/Thesis/Data/TkgConstructions/ICU-NCIT/OR.txt'
    #triplesFile = '/Users/ricardocarvalho/Documents/Thesis/Data/TkgConstructions/ICU-NCIT/OENT.txt'
    #in_use_construct_kg(entityFile,triplesFile,relationFile)