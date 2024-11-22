<div align="center">

# P2PFaaS

A Framework for FaaS load balancing  | _`stack-learner` repository_

![License](https://img.shields.io/badge/license-GPLv3-green?style=flat)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/c0e7267c8935441fb53485dff6d5612b)](https://www.codacy.com/gl/p2p-faas/stack-scheduler/dashboard?utm_source=gitlab.com&amp;utm_medium=referral&amp;utm_content=p2p-faas/stack-scheduler&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/1f09d1cb8d824cf69cda711b8f0b49fb)](https://www.codacy.com/gl/p2p-faas/stack-learner/dashboard?utm_source=gitlab.com&amp;utm_medium=referral&amp;utm_content=p2p-faas/stack-learner&amp;utm_campaign=Badge_Grade)

</div>

# Introduction

This module of the P2PFaaS stack is in charge of taking a scheduling decision by using reinforcement learning. It is in charge of training a model and then doing the inference on that model.

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

## Build & Run

To build the image:
```
docker build -t p2p-faas/stack-learner:latest .
```

To boot the framework, please follow the instruction in the [stack repo](https://gitlab.com/p2p-faas/stack).

For further reference visit [p2p-faas.gitlab.io](https://p2p-faas.gitlab.io/)