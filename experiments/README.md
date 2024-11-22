<div align="center">

# P2PFaaS

A Framework for FaaS load balancing  | _`stack` repository_

![License](https://img.shields.io/badge/license-GPLv3-green?style=flat)

</div>

# Introduction

This repository contains a set of scripts used for configuring the framework and performing benchmarks. In particular, the relevant subdirectories are:

- `benchmark-go/` - implements a benchmark script in Go
- `benchmark/` - old benchmark script written in Python
- `functions/` - set of functions from OpenFaaS that could have been modified
- `machines-setup/` - set of scripts for configuring the nodes and the framework


# Cite the work

For a detailed information about the framework you can read my MSc thesis at [raw.gpm.name/theses/master-thesis.pdf](https://raw.gpm.name/theses/master-thesis.pdf). If you are using P2PFaaS in your work please cite [https://doi.org/10.1016/j.softx.2022.101290](https://doi.org/10.1016/j.softx.2022.101290):

```bibtex
@article{PROIETTIMATTIA2023101290,
    title = {P2PFaaS: A framework for FaaS peer-to-peer scheduling and load balancing in Fog and Edge computing},
    journal = {SoftwareX},
    volume = {21},
    pages = {101290},
    year = {2023},
    issn = {2352-7110},
    doi = {https://doi.org/10.1016/j.softx.2022.101290},
    url = {https://www.sciencedirect.com/science/article/pii/S2352711022002084},
    author = {Gabriele {Proietti Mattia} and Roberto Beraldi},
    keywords = {Edge Computing, Fog Computing, FaaS}
}
```

For further reference visit [p2p-faas.gitlab.io](https://p2p-faas.gitlab.io/)