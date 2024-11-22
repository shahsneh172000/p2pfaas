# P2PFaaS: A Decentralized Framework for Function-as-a-Service (FaaS) in Edge and Fog Computing

---

# 🌐 P2PFaaS Framework

A **peer-to-peer Function-as-a-Service (FaaS)** framework for decentralized scheduling and load balancing in **Fog and Edge computing** environments. Built with **Docker containers**, P2PFaaS provides a modular and portable platform for real-world testing of scheduling algorithms, including those based on Reinforcement Learning.

---

## ✨ Features
- **Fully Decentralized Scheduling**: No central orchestrator; nodes make independent decisions.
- **Edge & Fog Ready**: Tested on x86 servers and ARM-based devices (e.g., Raspberry Pi).
- **Reinforcement Learning Integration**: Built-in support for learning-based scheduling.
- **Modular Architecture**: Scheduler, Discovery, and Learner services.
- **Real-World Compatibility**: Overcomes simulation-only limitations with practical implementations.

---

## 📁 Repository Structure
```
├── scheduler/             # Scheduler Service (Go)
├── learner/               # Learner Service (Python)
├── discovery/             # Discovery Service (Go)
├── docker-compose.yml     # Deployment configuration
├── docker-compose-fn.yml  # Deployment configuration
└── README.md              # Project documentation
```

---

## 🚀 Getting Started

### 1️⃣ Prerequisites
- [Docker](https://www.docker.com/) 
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- Compatible environment:
  - x86 servers or ARM devices
  - Go 1.18, Python 3.8

### 2️⃣ Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/shahsneh172000/P2PFaaS.git
   cd P2PFaaS
   ```
2. FaaS Function and OpenFaaS Setup:
   
   OpenFaas Setup: 
   
   OpenFaaS® makes it easy for developers to deploy event-driven functions 
   and microservices to Kubernetes without repetitive, boiler-plate coding. Package your 
   code or an existing binary in a Docker image to get a highly scalable endpoint with 
   auto-scaling and metric.

   ```bash
   # For MacOS / Linux:
   curl -SLsf https://get.arkade.dev/ | sudo sh

   # For Windows (using Git Bash)
   curl -SLsf https://get.arkade.dev/ | sh

   # Install Arkade
   arkade install openfaas 
   ```
   After the installation you'll receive a command to retrieve your OpenFaaS URL and password.

   ```bash
   Info for app: openfaas
   # Get the faas-cli
   curl -SLsf https://cli.openfaas.com | sudo sh

   # Forward the gateway to your machine
   kubectl rollout status -n openfaas deploy/gateway
   kubectl port-forward -n openfaas svc/gateway 8080:8080 &

   # If basic auth is enabled, you can now log into your gateway:
    PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
   echo -n $PASSWORD | faas-cli login --username admin --password-stdin

   faas-cli store deploy figlet
   faas-cli list

   # For Raspberry Pi
   faas-cli store list \
   --platform armhf

   faas-cli store deploy figlet \
   --platform armhf
   ```



2. Build the Docker containers:
   ```bash
   docker-compose build
   ```
3. Start the services:
   ```bash
   docker-compose up
   ```

### 3️⃣ Configuration
- Configure the Discovery Service:
  - Use the API endpoint: `/configuration` at port `19000`.

---

## 🛠 Architecture Overview

### Core Modules
- **Scheduler Service**: Handles function execution requests and scheduling logic.
- **Learner Service**: Manages Reinforcement Learning models.
- **Discovery Service**: Discovers and manages neighboring nodes.

### Operational Flow
1. Client requests function execution (via REST API).
2. Scheduler evaluates and forwards the task.
3. Task is executed locally or remotely.
4. RL-based schedulers update models post-execution.

![Architecture Diagram](https://your-diagram-link.com)

---

## 📊 Benchmarks & Use Cases
- Tested on **12 Raspberry Pi 4** devices using RL-based scheduling strategies.
- Supports diverse real-world scenarios like **latency optimization** and **load balancing**.

---

## 🛡 License
This project is licensed under the **GPLv3 License**. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing
We welcome contributions! Feel free to submit issues or pull requests.

---

## 📧 Support
For questions or feedback, reach out to:
- **Gabriele Proietti Mattia**: [proiettimattia@diag.uniroma1.it](mailto:proiettimattia@diag.uniroma1.it)

Happy coding! 🚀
