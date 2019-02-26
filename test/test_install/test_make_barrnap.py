#!/usr/bin/env python3
# coding: utf-8

"""
Tests for make script, installing genomeAPCAT according to already existing dependencies
From a computer with ubuntu and barrnap installed only
"""
import os
import pytest

from . import utilities as utils

@pytest.fixture
def install_panacota():
    print("INSTALLING PANACOTA")
    cmd = "python3 make"
    error = "Error installing"
    utils.run_cmd(cmd, error)


def teardown_function(function):
    """
    Uninstall genomeAPCAT and installed dependencies
    """
    print("TEARDOWN\n")
    cmd = "python3 make uninstall"
    error = "Error uninstall"
    utils.run_cmd(cmd, error)
    os.remove("install.log")
    print("cleaning repo")


def test_install():
    """
    Test that when installing from a computer containing only barrnap, it installs
    genomeAPCAT, and returns the list of missing dependencies
    """
    cmd = "python3 make"
    error = "Error trying to install genomeAPCAT from base"
    assert utils.check_installed("barrnap")
    assert not utils.check_installed("prokka")
    utils.run_cmd(cmd, error)
    assert not utils.check_installed("prokka")
    assert utils.check_installed("barrnap")
    assert utils.check_installed("genomeAPCAT")
    cmd = "pip3 show genomeAPCAT"
    err = "error pip3"
    stdout = "stdout_pip3show.out"
    with open(stdout, "w") as stdof:
        utils.run_cmd(cmd, err, stdout=stdof, stderr=stdof)
    with open(stdout, "r") as stdof:
        lines = stdof.readlines()
        assert "Summary: Large scale comparative genomics tools" in lines[2]
    os.remove(stdout)
    logfile = "install.log"
    content = ["Installing genomeAPCAT",
               "Some dependencies needed for some subcommands of genomeAPCAT are "
               "not installed. Here is the list of missing dependencies, and for what they are "
               "used. If you plan to use the subcommands hereafter, first install required "
               "dependencies:",
               "- mmseqs (for pangenome subcommand)",
               "- mafft (to align persistent genomes in order to infer a phylogenetic tree "
               "after)",
               "- prokka (for annotate subcommand, with syntaxic + functional annotation)",
               "- prodigal : for annotate subcommand, you at least need prodigal (for syntaxic ",
               "- One of the 3 following softwares, used to infer a phylogenetic tree:",
               "* FastTree (see README or documentation for more information on how to "
               "install it)", "* FastME", "* Quicktree"]
    # Check output logfile content. Check that all content is present, in any order.
    with open(logfile, "r") as logf:
        logf_content = "".join(logf.readlines())
        for linec in content:
            assert linec in logf_content
    # Check that needed packages are installed
    assert utils.is_package_installed("argparse")
    assert utils.is_package_installed("progressbar")
    assert utils.is_package_installed("numpy")
    assert utils.is_package_installed("matplotlib")
    assert utils.is_package_installed("Bio")


def test_upgrade(install_panacota):
    """
    Test upgrading genomeAPCAT when dependencies are still installed
    # """
    install_panacota
    assert utils.check_installed("barrnap")
    assert not utils.check_installed("prokka")
    assert utils.check_installed("genomeAPCAT")
    cmd = "python3 make upgrade"
    error = "Error upgrade"
    utils.run_cmd(cmd, error)
    assert utils.check_installed("barrnap")
    assert not utils.check_installed("prokka")
    assert utils.check_installed("genomeAPCAT")
    logfile = "install.log"
    with open(logfile, "r") as logf:
        lines = logf.readlines()
        assert len(lines) == 1
        assert "Upgrading genomeAPCAT" in lines[0]


def test_uninstall(install_panacota):
    """
    Test uninstalling PanACoTA
    """
    install_panacota
    assert utils.check_installed("barrnap")
    assert not utils.check_installed("prokka")
    assert utils.check_installed("genomeAPCAT")
    cmd = "python3 make uninstall"
    error = "Error uninstalling"
    utils.run_cmd(cmd, error)
    assert utils.check_installed("barrnap")
    assert not utils.check_installed("prokka")
    assert not utils.check_installed("genomeAPCAT")
    logfile = "install.log"
    with open(logfile, "r") as logf:
        lines = logf.readlines()
        assert len(lines) == 1
        assert ":: INFO :: Uninstalling genomeAPCAT" in lines[0]


def test_develop():
    """
    Test installing genomeAPCAT in developer mode, when barrnap is already installed
    """
    assert not utils.check_installed("genomeAPCAT")
    assert utils.check_installed("barrnap")
    assert not utils.check_installed("prokka")
    cmd = "python3 make develop"
    error = "Error develop"
    utils.run_cmd(cmd, error)
    assert utils.check_installed("genomeAPCAT")
    assert utils.check_installed("barrnap")
    assert not utils.check_installed("prokka")
    cmd = "pip3 show genomeAPCAT"
    err = "error pip3"
    stdout = "stdout_pip3show.out"
    with open(stdout, "w") as stdof:
        utils.run_cmd(cmd, err, stdout=stdof, stderr=stdof)
    # Check that it was not installed
    with open(stdout, "r") as stdof:
        for line in stdof:
            print(line)
        # lines = stdof.readlines()
    #     found = False
    #     for line in lines:
    #         if "/Users/" in line:
    #             found = True
    #             break
    #     assert found
    # os.remove(stdout)
    # logfile = "install.log"
    # content = ["Installing developer packages needed for genomeAPCAT",
    #            "Some dependencies needed for some subcommands of genomeAPCAT are "
    #            "not installed. Here is the list of missing dependencies, and for what they are "
    #            "used. If you plan to use the subcommands hereafter, first install required "
    #            "dependencies:",
    #            "- mmseqs (for pangenome subcommand)",
    #            "- mafft (to align persistent genomes in order to infer a phylogenetic tree "
    #            "after)",
    #            "- prokka (for annotate subcommand, with syntaxic + functional annotation)",
    #            "- prodigal : for annotate subcommand, you at least need prodigal (for syntaxic ",
    #            "- One of the 3 following softwares, used to infer a phylogenetic tree:",
    #            "* FastTree (see README or documentation for more information on how to "
    #            "install it)", "* FastME", "* Quicktree"]
    # # Check output logfile content. Check that all content is present, in any order.
    # with open(logfile, "r") as logf:
    #     logf_content = "".join(logf.readlines())
    #     for linec in content:
    #         assert linec in logf_content
    # # Check that needed packages are installed
    # assert utils.is_package_installed("argparse")
    # assert utils.is_package_installed("progressbar")
    # assert utils.is_package_installed("numpy")
    # assert utils.is_package_installed("matplotlib")
    # assert utils.is_package_installed("Bio")
    # assert utils.is_package_installed("sphinx")
    # assert utils.is_package_installed("coverage")
