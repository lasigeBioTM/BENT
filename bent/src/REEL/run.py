#!/usr/bin/env python
import os
import bent.src.cfg as cfg
from bent.src.REEL.pre_process import pre_process
from bent.src.REEL.post_process import process_results


def run(run_id, ner_dir, kb, entity_type, abbreviations, nil_mode=None):
    """Apply the REEL model (preprocess, candidate scoring with PPR,
    postprocess) to the entities present in files in ner_dir.

    :param ner_dir: path to directory where the recognized entities are
        stored in the annotations files
    :type ner_dir: str
    :param kb: target knowledge base
    :type kb: str
    :param entity_type: the type of the entities that will be linked
    :type entity_type: str
    :param abbreviations: abbreviations with format:
        {'doc_id': {'abbv1': 'long_form'}]
    :type abbreviations: dict
    :return: nel_run_id representing the identifier of the current run of REEL.
        The results of the run will be located in the directory
        'tmp/REEL/results/<run_id/>'.
    :rtype: str
    """

    nel_run_name = f"{run_id}/{entity_type}"

    # Use relations extracted from external corpora and relations described in
    # the targer knowledge base
    link_mode = "kb_corpus"

    # Use NILINKER model if available
    if nil_mode:
        #TODO: implement efficient NILINKER-ctd_chem model
        available_kbs_nilinker = ["chebi", "medic", "go_bp", "hp"]
        
        if kb in available_kbs_nilinker:
            nil_mode = "NILINKER"
    # -------------------------------------------------------------------------#
    #                        REEL: PRE_PROCESSING
    #        Pre-processes the corpus to create a candidates file for each
    #        document in dataset to allow further building of the
    #        disambiguation graph.
    # -------------------------------------------------------------------------#
    pre_process(
        nel_run_name, ner_dir, kb, entity_type, link_mode, nil_mode, abbreviations
    )

    # ------------------------------------------------------------------------#
    #                          REEL: PPR
    #         Builds a disambiguation graph from each candidates file:
    #         the nodes are the candidates and relations are added
    #         according to candidate link_mode. After the disambiguation
    #         graph is built, it runs the PPR algorithm over the graph
    #         and ranks each candidate.
    # ------------------------------------------------------------------------#
    if kb != "ncbi_gene":
        ppr_dir = f"{cfg.root_path}/src/REEL/"
        comm = f"java -classpath :{ppr_dir} ppr_for_ned_all {nel_run_name} ppr_ic"
        os.system(comm)

    # ------------------------------------------------------------------------#
    #                         REEL: Post-processing
    # ------------------------------------------------------------------------#
    process_results(nel_run_name, entity_type, kb)

    return nel_run_name
