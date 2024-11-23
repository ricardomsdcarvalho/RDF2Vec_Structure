from operator import itemgetter
import json

import rdflib
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
                        ents.append(headEnt)

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
                            ents.append(headEnt)

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