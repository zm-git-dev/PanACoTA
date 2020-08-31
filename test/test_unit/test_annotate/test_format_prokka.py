#!/usr/bin/env python3
# coding: utf-8

"""
Unit tests for general_format_functions.py
"""

import os
import logging
import shutil
from io import StringIO
import pytest

import PanACoTA.annotate_module.format_prokka as prokkafunc
import PanACoTA.utils as utils
import test.test_unit.utilities_for_tests as tutil

ANNOTEDIR = os.path.join("test", "data", "annotate")
EXP_ANNOTE = os.path.join(ANNOTEDIR, "exp_files")
TEST_ANNOTE = os.path.join(ANNOTEDIR, "test_files")
GENEPATH = os.path.join(ANNOTEDIR, "generated_by_unit-tests")

LOGFILE_BASE = os.path.join(GENEPATH, "logfile")
LOGFILES = [LOGFILE_BASE + ext for ext in [".log", ".log.debug", ".log.details", ".log.err"]]

@pytest.fixture(autouse=True)
def setup_teardown_module():
    """
    Remove log files at the end of this test module

    Before each test:
    - init logger
    - create directory to put generated files

    After:
    - remove all log files
    - remove directory with generated results
    """
    os.mkdir(GENEPATH)
    print("setup")

    yield
    shutil.rmtree(GENEPATH)
    print("teardown")


def test_tbl_to_lst_not_changed_names(caplog):
    """
    Check that generated lstinfo file is as expected, when the genome name is the same as
    it already was in the genome given to prokka.
    The test tblfile contains the following aspects:
    - gene in D strand (start < end)
    - gene in C strand (start > end)
    - CDS features (some with all info = ECnumber, gene name, product etc. ;
    some with missing info)
    - tRNA type
    - repeat_region type (*2)
    - contigs with more than 2 genes
    - contig with only 2 genes (both 'b' loc)
    - contig with 1 gene ('b' loc)
    - contig without gene (should be skipped)
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prokka")
    tblfile = os.path.join(TEST_ANNOTE, "original_name.fna-prokkaRes", "prokka_out_for_test.tbl")
    lstfile = os.path.join(GENEPATH, "res_test_tbl2lst.lst")
    contigs = {"test.0417.00002.0001": "test.0417.00002.0001",
               "test.0417.00002.0002": "test.0417.00002.0002",
               "test.0417.00002.0003": "test.0417.00002.0003",
               "test.0417.00002.0004": "test.0417.00002.0004",
               "test.0417.00002.0005": "test.0417.00002.0005",
               "test.0417.00002.0006": "test.0417.00002.0006",
               "test.0417.00002.0007": "test.0417.00002.0007",
              }
    name = "test.0417.00002"
    gpath = "genome_init"
    assert prokkafunc.tbl2lst(tblfile, lstfile, contigs, name, gpath)
    exp_lst = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    assert tutil.compare_order_content(exp_lst, lstfile)


def test_tbl_to_lst_changed_names(caplog):
    """
    Check that generated lstinfo file is as expected, when the genome name is not the same as
    it already was in the genome given to prokka.
    The test tblfile contains the following aspects:
    - gene in D strand (start < end)
    - gene in C strand (start > end)
    - CDS features (some with all info = ECnumber, gene name, product etc. ;
    some with missing info)
    - tRNA type
    - repeat_region type (*2)
    - contigs with more than 2 genes
    - contig with only 2 genes (both 'b' loc)
    - contig with 1 gene ('b' loc)
    - contig without gene (should be skipped)
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prokka")
    tblfile = os.path.join(TEST_ANNOTE, "prokka_out_tbl_changed-contnames.tbl")
    lstfile = os.path.join(GENEPATH, "res_test_tbl2lst.lst")
    contigs = {"toto_1": "test.0417.00002.0001",
               "toto_2": "test.0417.00002.0002",
               "toto_3": "test.0417.00002.0003",
               "toto_4": "test.0417.00002.0004",
               "toto_5": "test.0417.00002.0005",
               "toto_6": "test.0417.00002.0006",
               "toto_7": "test.0417.00002.0007",
              }
    name = "test.0417.00002"
    gpath = "path_to_genome"
    assert prokkafunc.tbl2lst(tblfile, lstfile, contigs, name, gpath)
    exp_lst = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    assert tutil.compare_order_content(exp_lst, lstfile)


def test_tbl_to_lst_unknown(caplog):
    """
    A contig name in the fna file does not exist -> error message, and all result files
    must be removed for this genome
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prokka")
    tblfile = os.path.join(TEST_ANNOTE, "prokka_out_tbl_changed-contnames.tbl")
    lstfile = os.path.join(GENEPATH, "res_test_tbl2lst.lst")
    contigs = {"toto_1": "test.0417.00002.0001",
               "toto_2": "test.0417.00002.0002",
               "toto_3": "test.0417.00002.0003",
               "toto_5": "test.0417.00002.0004",
               "toto_6": "test.0417.00002.0006",
               "toto_7": "test.0417.00002.0007",
              }
    name = "test.0417.00002"
    gpath = "path_to_genome"
    assert not prokkafunc.tbl2lst(tblfile, lstfile, contigs, name, gpath)
    assert ("'toto_4' found in test/data/annotate/test_files/prokka_out_tbl_changed-contnames.tbl "
            "does not exist in path_to_genome") in caplog.text


def test_create_gff(caplog):
    """
    Check generated gff file. Must have all sequences in header (even replicons without gene),
    and then 1 line per gene
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prodigal")
    gfffile = os.path.join(TEST_ANNOTE, "original_name.fna-prokkaRes",
                           "prokka_out_for_test.gff")
    contigs = {"test.0417.00002.0001": "test.0417.00002.0001",
               "test.0417.00002.0002": "test.0417.00002.0002",
               "test.0417.00002.0003": "test.0417.00002.0003",
               "test.0417.00002.0004": "test.0417.00002.0004",
               "test.0417.00002.0005": "test.0417.00002.0005",
               "test.0417.00002.0006": "test.0417.00002.0006",
               "test.0417.00002.0007": "test.0417.00002.0007",
              }
    sizes = {"test.0417.00002.0001": 14000,
             "test.0417.00002.0002": 5000,
             "test.0417.00002.0003": 4600,
             "test.0417.00002.0004": 8000,
             "test.0417.00002.0005": 1,
             "test.0417.00002.0006": "test.0417.00002.0006",
             "test.0417.00002.0007": "test.0417.00002.0007"
            }
    res_gff_file = os.path.join(GENEPATH, "prodigal_res.gff")
    res_lst = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    gpath = "original_genome_name"
    assert prokkafunc.generate_gff(gpath, gfffile, res_gff_file, res_lst, sizes, contigs)
    exp_gff = os.path.join(EXP_ANNOTE, "res_create_gff-prokka.gff")
    assert tutil.compare_order_content(exp_gff, res_gff_file)


def test_create_gff_wrong_start(caplog):
    """
    Check generated gff file. A sequence has not the same start in gff and in tbl
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prodigal")
    gfffile = os.path.join(TEST_ANNOTE, "prokka_out_gff-wrong-start.gff")
    contigs = {"test.0417.00002.0001": "test.0417.00002.0001",
               "test.0417.00002.0002": "test.0417.00002.0002",
               "test.0417.00002.0003": "test.0417.00002.0003",
               "test.0417.00002.0004": "test.0417.00002.0004",
               "test.0417.00002.0005": "test.0417.00002.0005",
               "test.0417.00002.0006": "test.0417.00002.0006",
               "test.0417.00002.0007": "test.0417.00002.0007",
              }
    sizes = {"test.0417.00002.0001": 14000,
             "test.0417.00002.0002": 5000,
             "test.0417.00002.0003": 4600,
             "test.0417.00002.0004": 8000,
             "test.0417.00002.0005": 1,
             "test.0417.00002.0006": "test.0417.00002.0006",
             "test.0417.00002.0007": "test.0417.00002.0007"
            }
    res_gff_file = os.path.join(GENEPATH, "prodigal_res.gff")
    res_lst = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    gpath = "original_genome_name"
    assert not prokkafunc.generate_gff(gpath, gfffile, res_gff_file, res_lst, sizes, contigs)
    assert ("Files prokka_out_gff-wrong-start.tbl and prokka_out_gff-wrong-start.gff "
            "(in prokka tmp_files: original_genome_name-prokkaRes) do not have the same "
            "start value for gene EPKOMDHM_00011 (3000 in gff, 3500 in tbl)") in caplog.text


def test_create_gff_error_gff(caplog):
    """
    Check generated gff file. The prokka output gff file has a problem (locus_tag != ID)
    -> returns False with error message
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prodigal")
    gfffile = os.path.join(TEST_ANNOTE, "prokka_out_gff-error.gff")
    contigs = {"test.0417.00002.0001": "test.0417.00002.0001",
               "test.0417.00002.0002": "test.0417.00002.0002",
               "test.0417.00002.0003": "test.0417.00002.0003",
               "test.0417.00002.0004": "test.0417.00002.0004",
               "test.0417.00002.0005": "test.0417.00002.0005",
               "test.0417.00002.0006": "test.0417.00002.0006",
               "test.0417.00002.0007": "test.0417.00002.0007",
              }
    sizes = {"test.0417.00002.0001": 14000,
             "test.0417.00002.0002": 5000,
             "test.0417.00002.0003": 4600,
             "test.0417.00002.0004": 8000,
             "test.0417.00002.0005": 1,
             "test.0417.00002.0006": "test.0417.00002.0006",
             "test.0417.00002.0007": "test.0417.00002.0007"
            }
    res_gff_file = os.path.join(GENEPATH, "prodigal_res.gff")
    res_lst = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    gpath = "original_genome_name"
    assert not prokkafunc.generate_gff(gpath, gfffile, res_gff_file, res_lst, sizes, contigs)
    assert ("Problem in prokka_out_gff-error.gff: ID=EPKOMDHM_00006 whereas "
            "locus_tag=toto") in caplog.text


def test_create_gen(caplog):
    """
    Check create gen file.
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prodigal")
    ffnfile = os.path.join(TEST_ANNOTE, "original_name.fna-prokkaRes",
                           "prokka_out_for_test.ffn")
    lstfile = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    res_gen_file = os.path.join(GENEPATH, "prodigal_res.gen")
    assert prokkafunc.create_gen(ffnfile, lstfile, res_gen_file)
    exp_gen = os.path.join(EXP_ANNOTE, "res_create_gene_prokka.gen")
    assert tutil.compare_order_content(exp_gen, res_gen_file)


def test_create_gen_wrong_crispr(caplog):
    """
    Check create gen file, but CRISPR number in lst is not the same as
    expected from ffn -> error and returns False
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prodigal")
    ffnfile = os.path.join(TEST_ANNOTE, "original_name.fna-prokkaRes",
                           "prokka_out_for_test.ffn")
    lstfile = os.path.join(TEST_ANNOTE, "test_create_gene_prokka-wrongCRISPRnum.lst")
    res_gen_file = os.path.join(GENEPATH, "prodigal_res.gen")
    assert not prokkafunc.create_gen(ffnfile, lstfile, res_gen_file)
    assert ("Problem with CRISPR numbers in test/data/annotate/test_files/"
            "test_create_gene_prokka-wrongCRISPRnum.lst. CRISPR >prokka_out_for_test "
            "in ffn is CRISPR num 1, whereas it is annotated as CRISPR num 2 "
            "in lst file.") in caplog.text


def test_create_gen_wrong_format(caplog):
    """
    Check create gen file, but 1 header has a wrong format
    -> error message and returns False
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prodigal")
    ffnfile = os.path.join(TEST_ANNOTE, "prokka_out_for_test-wrongFormat.ffn")
    lstfile = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    res_gen_file = os.path.join(GENEPATH, "prodigal_res.gen")
    assert not prokkafunc.create_gen(ffnfile, lstfile, res_gen_file)
    assert ("Unknown header format >JGIKIPIJ-00005 in test/data/annotate/test_files/"
            "prokka_out_for_test-wrongFormat.ffn.\nGen file will not be created.") in caplog.text


def test_create_gen_unknown_gene(caplog):
    """
    Check create gen file, but 1 gene is present in ffn, but not in lst
    -> error message and returns False
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prodigal")
    ffnfile = os.path.join(TEST_ANNOTE, "prokka_out_for_test-supGene.ffn")
    lstfile = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    res_gen_file = os.path.join(GENEPATH, "prodigal_res.gen")
    assert not prokkafunc.create_gen(ffnfile, lstfile, res_gen_file)
    assert ("Missing info for gene >sup_gene_00012 (from test/data/annotate/test_files/"
            "prokka_out_for_test-supGene.ffn) in test/data/annotate/exp_files/"
            "res_tbl2lst-prokka.lst. If it is actually present in the lst file, "
            "check that genes are ordered by increasing number in both "
            "lst and ffn files.") in caplog.text


def test_create_gen_missingSeq(caplog):
    """
    Check create gen file. A gene in lst does not have a sequence in ffn.
    Just skip it, and go to next sequence for gen file.
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prodigal")
    ffnfile = os.path.join(TEST_ANNOTE, "prokka_out_for_test-noSeqFor1gene.ffn")
    lstfile = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    res_gen_file = os.path.join(GENEPATH, "prodigal_res.gen")
    assert prokkafunc.create_gen(ffnfile, lstfile, res_gen_file)
    exp_gen = os.path.join(EXP_ANNOTE, "res_create_gene_prokka-missingSeq.gen")
    assert tutil.compare_order_content(exp_gen, res_gen_file)


def test_create_gen_missingLst(caplog):
    """
    Check create gen file, but there is 1 gene in ffn which does not exist in lst
    Error message and returns false
    """
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger("test_prodigal")
    ffnfile = os.path.join(TEST_ANNOTE, "prokka_out_for_test-noLstFor1gene.ffn")
    lstfile = os.path.join(EXP_ANNOTE, "res_tbl2lst-prokka.lst")
    res_gen_file = os.path.join(GENEPATH, "prodigal_res.gen")
    assert not prokkafunc.create_gen(ffnfile, lstfile, res_gen_file)
    assert ("Missing info for gene >JGIKIPIJ_003018 (from test/data/annotate/test_files/"
            "prokka_out_for_test-noLstFor1gene.ffn) in test/data/annotate/exp_files/"
            "res_tbl2lst-prokka.lst. If it is actually present in the lst file, "
            "check that genes are ordered by increasing number in both lst "
            "and ffn files.") in caplog.text

