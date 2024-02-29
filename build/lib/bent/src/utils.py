#!/usr/bin/env python
from copy import deepcopy
import os
import gc
import psutil
import shutil
import orjson as json
import bent.src.cfg as cfg
from bent.src.classes import Document, Sentence, Entity

# ------------------------------------------------------------------------------
#                       INPUT ARGUMENTS VERIFICATION
# ------------------------------------------------------------------------------


def _check_input_types(types):
    """Check if the inputted entity types are valid, as well the selected
    target knowledge bases.

    :param types: a dictionary with the format {'entity_type: 'target_kb'}
    :type types: dict
    :raises ValueError: if types is an empty dictionary
    """

    if types == {}:
        raise ValueError("No specified entity types!")

    else:
        available_types = [
            "disease",
            "chemical",
            "gene",
            "organism",
            "bioprocess",
            "anatomical",
            "cell_component",
            "cell_line",
            "cell_type",
            "variant",
            "NILDis",
            "NILChem",
            "NILGene",
        ]

        for ent_type in types:

            if ent_type != "":
                assert (
                    ent_type in available_types
                ), f"{ent_type} is an invalid entity type to recognize! Options:\
                    'disease', 'chemical', 'gene', 'organism', 'bioprocess', \
                    'bioprocess', 'anatomical', 'cell_component', 'cell_line',\
                    'cell_type', 'variant', 'NILDis', 'NILChem', 'NILGene'"               


def _check_input_args(
    recognize,
    link,
    types,
    input_format,
    input_text,
    in_dir,
    ner_dir,
    out_dir,
):
    """Verify if the input arguments are valid."""

    available_formats = ["brat", "bioc_xml", "bioc_json", "pubtator"]

    # Verify selected task(s)
    assert (
        recognize is True or link is True
    ), "It is available Named Entity Recognition (NER) and/or Named Entity \
        ensure that either recognize == True and/or link == True"

    # Verify the inputed entity types and respective target KBs
    _check_input_types(types)

    # Verify input format and directory arguments
    if recognize:

        if input_text is None and in_dir is None:
            raise ValueError(
                'It is necessary to input either a text or a \
                list of texts (by setting the argument "input_text") \
                OR a directory containing file(s) with texts to annotate \
                (by setting the argument "text_dir").'
            )

        if (
            input_format == "bioc_json"
            or input_format == "bioc_xml"
            or input_format == "pubtator"
        ):

            assert (
                in_dir is not None or ner_dir is not None
            ), 'For input formats "bioc_json", "bioc_xml"and "pubtator" \
                    it is necessary to specify the input directory by setting \
                    the argument "in_dir"'

    if link:

        if not recognize:

            assert (
                ner_dir is not None
            ), 'No NER will be performed, only NEL: \
                it is necessary to specfiy the directory containing \
                NER annotations (by setting the argument "ner_dir").'

    # Check directory paths

    if in_dir is not None:
        assert (
            in_dir[-1:] == "/"
        ), 'Invalid argument "in_dir": the last \
            character in the directory path must be "/"\n. Examples: \
            "dataset/txt" -> INVALID directory path \
            "dataset/txt/" -> VALID directory path'

    if ner_dir is not None:
        assert (
            ner_dir[-1:] == "/"
        ), 'Invalid argument "ner_dir": the last \
            character in the directory path must be "/"\n. Examples: \
            "dataset/ann" -> INVALID directory path \
            "dataset/ann/" -> VALID directory path'

    if out_dir is not None:
        assert (
            out_dir[-1:] == "/"
        ), 'Invalid argument "out_dir": the last \
            character in the directory path must be "/"\n. Examples: \
            "dataset/ann" -> INVALID directory path \
            "dataset/ann/" -> VALID directory path'


# ------------------------------------------------------------------------------
#                       INPUT FILE FORMAT CONVERSION
# ------------------------------------------------------------------------------
def _parse_bioc_json_file(filename, include_text=True):

    with open(filename, "r", encoding="utf-8") as infile:
        parsed_data = json.loads(infile.read())
        infile.close()

    parsed_data_up = {}

    for doc in parsed_data["documents"]:
        title = ""
        abstract = ""
        annotations = []
        parsed_data_up[doc["id"]] = ["", []]

        for passage in doc["passages"]:

            if passage["infons"]["type"] == "title":
                title = passage["text"]

            if passage["infons"]["type"] == "abstract":
                abstract = passage["text"]

                for annot in passage["annotations"]:
                    ent_type = annot["infons"]["type"]
                    text = annot["text"]

                    begin = annot["locations"][0]["offset"]
                    end = str(int(begin) + int(annot["locations"][0]["length"]))

                    annotation = (ent_type, begin, end, text)
                    annotations.append(annotation)

        text = title + "\n" + abstract

        parsed_data_up[doc["id"]][0] = ""

        if include_text:
            parsed_data_up[doc["id"]][0] = text

        parsed_data_up[doc["id"]][1] = annotations

    return parsed_data_up


def output_parsed_docs(parsed_data, out_dir, recognize=False):

    # Output parsed documents to out_dir in the BRAT format
    os.makedirs(f"{out_dir}txt/", exist_ok=True)
    os.makedirs(f"{out_dir}ann/", exist_ok=True)

    for doc_id in parsed_data:
        doc_text = parsed_data[doc_id][0]

        with open(f"{out_dir}txt/{doc_id}.txt", "w", encoding="utf-8") as txt_file:
            txt_file.write(doc_text)
            txt_file.close()

        if not recognize:
            # In this case only the NEL step will be performed
            # Make annotations file
            annotations = parsed_data[doc_id][1]
            annot_str = ""

            for i, annot in enumerate(annotations):
                annot_str += f"T{str(i + 1)}\t{annot[0]} {annot[1]} {annot[2]}\t{annot[3]}\n"

            with open(f"{out_dir}ann/{doc_id}.ann", "w", encoding="utf-8") as ann_file:
                ann_file.write(annot_str)
                ann_file.close()


def _convert_input_files(in_dir=None, input_text=None):
    """Convert input file(s) into brat/standoff format"""

    if input_text is not None:

        if isinstance(input_text, str):
            input_files = [input_text]

        elif isinstance(input_text, list):
            input_files = input_text

        # Create a txt file for later use in the NEL module.
        for i, text in enumerate(input_files, start=1):
            doc_id = f"doc_{str(i)}"

            with open(f"{in_dir}{doc_id}.txt", "w", encoding="utf-8") as txt_file:
                txt_file.write(text)
                txt_file.close()


# ------------------------------------------------------------------------------
#                       TEXT PARSING AND OBJECTIFICATION
# ------------------------------------------------------------------------------


def _sentence_splitter(doc_text, lang_model):
    """Split given text into sentences using SpaCy and the ScispaCy model
    'en_core_sci_lg' (https://allenai.github.io/scispacy/).

    :param doc_text: the input text to be splitted into sentences
    :type doc_text: str
    :param lang_model: Spacy sentence splitter model
    :type lang_model:
    :return: doc_sentences including input text splitted in sentences
    :rtype: list
    """

    processed_doc = lang_model(doc_text)
    doc_sentences = [sent.text for sent in processed_doc.sents]

    return doc_sentences


def _objectify_ner_input(doc_id, doc_text, doc_sentences):
    """Convert a given input text into a Document object.

    :param doc_id: the idenfitifer of the input text
    :type doc_id: str
    :param doc_text: the input text
    :type doc_text: str
    :param doc_sentences: the sentences of the input text
    :type doc_sentences: list
    :return: doc_obj including all the information about the input text, such
        as its identifier and its sentences
    :rtype: Document objcet
    """

    # Hierarchy: Collection -> Document -> Sentence -> Entity
    doc_obj = Document(doc_text)
    doc_obj.set_id(doc_id)
    current_pos = 0
    last_sent_index = len(doc_sentences) - 1
    doc_text_len = len(doc_text)

    for i, sent_text in enumerate(doc_sentences):
        # ---------------------------------------------------------------------
        # Solve mismatches produced by the sentence splitter when current
        # sentence and previous sentence are not separated by ' '.
        # This allows the correction of the span of the recognized entities

        if sent_text.isalnum():

            try:
                if i == last_sent_index:
                    original_char = doc_text[current_pos - 1]

                elif i < last_sent_index:
                    original_char = doc_text[current_pos]

                if original_char == " ":
                    i = 0
                    proceed = True

                    while proceed:
                        current_pos += 1

                        if current_pos < (doc_text_len):
                            original_char = doc_text[current_pos]

                            if original_char != " ":
                                proceed = False

                        else:
                            proceed = False

                        i += 1

                else:
                    sent_first_char = sent_text[0]

                    if original_char != sent_first_char:
                        i = 0

                        while original_char != sent_first_char:
                            current_pos -= 1
                            original_char = doc_text[current_pos]
                            i += 1

            except IndexError:
                continue
        # ---------------------------------------------------------------------
        sent_start = current_pos
        sent_end = current_pos + len(sent_text)
        sent_obj = Sentence(sent_start, sent_end, sent_text)
        sent_obj.set_num(i)

        doc_obj.add_sentence(sent_obj)

        # Usually sentences are separated by ' ', so it is added 1 to the
        # current position but in some cases this is not true
        current_pos += len(sent_text) + 1

    return doc_obj


def _objectify_entities(entities, sent_pos, includes_links=False):
    """Convert inputted recognized entities into Entity objects.

    :param entities: entities to be objectified
    :type entities: list
    :param sent_pos: the position of the sentence where the input entities
        were recognized relative to the source document
    :type sent_pos: int
    :param includes_links: specifies if there are knowledge based identifiers
        associated with the input entities, defaults to False
    :type includes_links: bool, optional
    :return: entities_obj including the Entity objects relative to the input
        entities
    :rtype: list
    """

    entities_obj = []

    for entity in entities:
        kb_id = None

        if len(entity) == 2:
            entity_obj = Entity(None, None, entity[0], entity[1], None, None, None)

        elif len(entity) > 2:

            if includes_links:
                kb_id = entity[4]
                entity_obj = Entity(
                    entity[0],
                    entity[1],
                    entity[2],
                    entity[3],
                    kb_id,
                    entity[5],
                    sent_pos,
                )

            else:
                kb_id = None
                entity_obj = Entity(
                    entity[0],
                    entity[1],
                    entity[2],
                    entity[3],
                    kb_id,
                    entity[4],
                    sent_pos,
                )

        entities_obj.append(entity_obj)

    return entities_obj


# ------------------------------------------------------------------------------
#                        FORMAT OUTPUT
# ------------------------------------------------------------------------------
def _prepare_output_from_objects(doc, only_ner=True):
    """Output given dataset in BRAT format to the given directory"""

    doc_annots = ""
    normalizations = ""

    for i, entity in enumerate(doc.entities):
        annot_id = str(i + 1)
        doc_annots += f"T{annot_id}\t{entity.type} {entity.start} {entity.end}\t{entity.text}\n"

        if not only_ner:
            normalizations += f"N{annot_id}\tReference T{annot_id} {entity.kb_id}\t{entity.text}\n"

    if not only_ner:
        doc_annots += normalizations

    return doc_annots


def _merge_dicts(dict1, dict2):

    dict3 = {}
    overlapping_keys = dict1.keys() & dict2.keys()

    for key in overlapping_keys:
        dict3[key] = _merge_dicts(dict1[key], dict2[key])

    for key in dict1.keys() - overlapping_keys:
        dict3[key] = deepcopy(dict1[key])

    for key in dict2.keys() - overlapping_keys:
        dict3[key] = deepcopy(dict2[key])

    return dict3


def _import_reel_results(doc_id, nel_run_ids):
    """Parse the results outputted by REEL-NILINKER for given document from
    file into a dictionary.

    :param doc_id: the identifier of the document where the entities were
        recognized
    :type doc_id: str
    :param nel_run_ids: identifiers that allow the parsing of the output of the
        Named Entity Linking step from files
    :type nel_run_ids: list
    :return: linked_entities with format: {'entity_text': 'kb_id'}
    :rtype: dict
    """

    linked_entities = {}

    for run_id in nel_run_ids:
        results_dir = f"{cfg.tmp_dir}{run_id}/REEL/results/"
        results_files = os.listdir(results_dir)
        linked_entities_type = {}
        ent_type = run_id.split("/")[1]
        target_filename = f"{doc_id}.json"

        if target_filename in results_files:
            filepath = results_dir + target_filename

            with open(filepath, "r", encoding="utf-8") as infile:
                linked_entities_type = json.loads(infile.read())
                infile.close()

        if linked_entities_type != {}:
            # Transform the keys of linked_entities_type
            linked_entities_type_up = {}

            for key in linked_entities_type.keys():
                key_name = key + "_" + ent_type
                linked_entities_type_up[key_name] = linked_entities_type[key]

            linked_entities = _merge_dicts(linked_entities, linked_entities_type_up)

    return linked_entities


def _update_dataset_with_nel_output(dataset, nel_run_ids):
    """Update Dataset object containing recognized entities (Named Entity
    Recognition step) with the output of the Named Entity Linking pipeline,
    i.e. knowledge base identifiers for each recognized entity.

    :param dataset: includes the output of the Named Entity Recognition
        pipeline
    :type dataset: Dataset object
    :param nel_run_ids: identifiers that allow the parsing of the output of the
        Named Entity Linking step from files
    :type nel_run_ids: list
    :return: updated dataset combining Named Entity Recognition + Linking
        outputs
    :rtype: Dataset object
    """

    dataset_docs = dataset.documents

    for doc in dataset_docs:
        linked_entities = _import_reel_results(doc.id, nel_run_ids)

        for i, sent in enumerate(doc.sentences):
            sent_entities = sent.entities

            for entity in sent_entities:
                key_name = entity.text + "_" + entity.type

                if key_name in linked_entities:
                    kb_id = linked_entities[key_name][0]
                    entity.set_kb_id(kb_id)
                    sent.update_entity(entity)

            doc.update_sentence(sent, i)

    dataset.update_doc(doc, doc.id)

    return dataset


def _update_ner_file_with_nel_output(ner_dir, nel_run_ids, out_dir=None):
    """Update annotations file generated in the Named Entity Recognition step
    with the output of the Named Entity Linking pipeline, i.e. knowledge base
    identifiers for each recognized entity. The generated annotations files
    will be located in the directory 'ner_dir'.

    :param ner_dir: path to directory where the recognized entities are
        stored in the annotations files
    :type ner_dir: str
    :param nel_run_ids: identifiers that allow the parsing of the output of the
        Named Entity Linking step from files
    :type nel_run_ids: list
    :param out_format: the format of the ouput, defaults to 'brat'
    :type out_format: str, optional
    """

    ner_filenames = os.listdir(ner_dir)

    for filename in ner_filenames:
        doc_id = filename.strip(".ann")
        linked_entities = _import_reel_results(doc_id, nel_run_ids)
        complete_filepath = ner_dir + filename

        with open(complete_filepath, "r", encoding="utf-8") as ner_file:
            ner_output = ner_file.readlines()
            ner_file.close()

        # Add the normalization lines to the annotations file
        final_output = ""

        for line in ner_output:

            if line != "\n":
                entity_text = line.split("\t")[2].strip("\n")
                term_id = line.split("\t")[0]
                entity_type = line.split("\t")[1].split(" ")[0]
                final_output += line

                if final_output[-1:] != "\n":
                    final_output += "\n"

                key_name = entity_text + "_" + entity_type

                if key_name in linked_entities and term_id[0] == "T":
                    kb_id = linked_entities[key_name][0]
                    annot_id = term_id.split("T")[1]
                    final_output += f"N{annot_id}\tReference {term_id} {kb_id}\t{entity_text}\n"
            
        if final_output[-1:] == "\n":
            final_output = final_output[:-1]

        if out_dir is not None:
            out_filepath = out_dir + filename
            os.makedirs(out_dir, exist_ok=True)

        with open(out_filepath, "w", encoding="utf-8") as out_file:
            out_file.write(final_output)
            out_file.close()

    # Delete temporary files associated with given run_ids
    for run_id in nel_run_ids:
        dir_to_delete = cfg.tmp_dir + run_id
        shutil.rmtree(dir_to_delete, ignore_errors=True)


# ------------------------------------------------------------------------------
#                           OTHER
# ------------------------------------------------------------------------------


def garbage_collect(threshold=50.0):
    """Call the garbage collection if memory usage is greater than threshold.

    :param threshold: amount of memory usage that triggers the garbage
        collection, defaults to 50.0
    :type threshold: float, optional
    """

    if psutil.virtual_memory().percent >= threshold:
        gc.collect()
