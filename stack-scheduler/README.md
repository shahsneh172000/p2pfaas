<div align="center">

# P2PFaaS

A Framework for FaaS load balancing  | _`stack-scheduler` repository_

![License](https://img.shields.io/badge/license-GPLv3-green?style=flat)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/c0e7267c8935441fb53485dff6d5612b)](https://www.codacy.com/gl/p2p-faas/stack-scheduler/dashboard?utm_source=gitlab.com&amp;utm_medium=referral&amp;utm_content=p2p-faas/stack-scheduler&amp;utm_campaign=Badge_Grade)
[![Go Report Card](https://goreportcard.com/badge/gitlab.com/p2p-faas/stack-scheduler)](https://goreportcard.com/badge/gitlab.com/p2p-faas/stack-scheduler)

</div>

# Introduction

The P2PFaaS is a framework that allows you to implement a load balancing/scheduling algorithm for FaaS.

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

# Repository

This is the scheduler service of the framework. It's written in Go and it is packaged with Docker.

## Build & Run

To build the image:
```
docker build -t p2p-faas/stack-scheduler:latest .
```

To run the scheduler please use the `docker-compose.yml` provided in the [stack repo](https://gitlab.com/p2p-faas/stack).

## Development

For running the development change directory to the root of the project, then change the `GOPATH`:
```
export GOPATH=$(pwd)
```

Build run the image with 

```
go build server
```

For further reference visit [p2p-faas.gitlab.io](https://p2p-faas.gitlab.io/)