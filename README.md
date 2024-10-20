# 💻 INF1006 - Computer Network Project

This project consists of two main components: a network topology setup using Cisco Packet Tracer and a chatbot room using Python and OpenAI. Each component showcases fundamental concepts in networking and client-server interaction.

## 🖧 Network Topology Setup (Assignment 1)

### Overview

This part of the project involves a network topology created in **Cisco Packet Tracer**, which is represented in the `assignment1topology.pkt` file. It simulates a small to medium-sized network with routers, switches, and end devices (PCs/Servers). The purpose is to demonstrate:

- **Routing**: Configured to ensure that different subnets can communicate effectively.
- **Switching**: Local communication within subnets.
- **IP Addressing**: Each device is assigned a static IP to ensure communication across the network.

The `.pkt` file contains pre-configured routing tables and IP addressing schemes for efficient communication within and between subnets.

## 🤖 Chatbot Room (Assignment 2)

### Overview

This part of the project demonstrates a simple **client-server chatroom** application using Python. It features a chatbot that interacts with users in real-time, powered by OpenAI's GPT model.

- **Server (`server.py`)**: Manages multiple client connections and facilitates communication between the chatbot and clients.
- **Client (`client_real.py` and `client_fake.py`)**:
  - `client_real.py` connects to the server and uses OpenAI's GPT model for intelligent responses.
  - `client_fake.py` simulates the chatbot responses without utilizing the OpenAI API, used for testing client-server functionality.

This setup demonstrates the concept of client-server architecture and handling real-time communication in a chatroom-like environment. The real client leverages natural language processing capabilities from OpenAI to respond intelligently, while the fake client is useful for testing purposes without needing API access.

## 📋 Requirements

- **Cisco Packet Tracer** for Assignment 1.
- **Python 3.x** and **OpenAI API Key** for Assignment 2.
  
## 👥 Contributors
- [Owen Nyo]
- [Neo ZhiYong, Chai Jun Yu, Chia Qi Jun, Rayner Tan]
