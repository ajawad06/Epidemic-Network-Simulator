# 🦠 Infectious Disease Spread Simulation (SEIRD)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Pygame](https://img.shields.io/badge/Library-Pygame-green) ![NetworkX](https://img.shields.io/badge/Graph-NetworkX-orange)

A real-time, agent-based simulation modeling the spread of a virus through a social network using the **SEIRD** model. Unlike simple grid-based simulations, it uses **Small-World Network topology** to mimic realistic human interactions, where clusters of friends have short paths to other groups.

> **Course:** Data Structures & Algorithms

---

## 🚀 Key Features:
*   **Real-time Visualization:** Watch the infection spread node-by-node using Pygame.
*   **Stochastic Logic:** Uses Monte Carlo methods (Bernoulli trials) for infection, recovery, and death probabilities.
*   **Optimization:** Implements an $O(N)$ game loop by optimizing the transmission traversal step.
*   **Post-Simulation Analysis:** Generates a Matplotlib bar chart/curve showing the final demographic breakdown.

---

## 🧬 Epidemiological Model: SEIRD
The agents traverse through five distinct states based on configurable time and probability thresholds:

1.  🟢 **(S) Susceptible:** Healthy individuals liable to infection.
2.  🟡 **(E) Exposed/Incubating:** Infected but not yet contagious (Latent period).
3.  🔴 **(I) Infectious:** Actively spreading the disease to connected neighbors.
4.  🔵 **(R) Recovered:** Survived the virus and acquired immunity.
5.  ⚫ **(D) Dead:** Fatal cases based on age-specific mortality rates.

---

## 🕸 Graph Theory & Algorithms

### 1. Network Topology
We utilize the **Watts-Strogatz Algorithm** to generate the social graph.
*   **Why?** It produces a "Small-World" network, which has high clustering (like real social circles) and short average path lengths (six degrees of separation).
*   **Process:** Starts with a Ring Lattice and randomly rewires edges with probability $p$.

### 2. Data Structures
*   **Adjacency Lists (via NetworkX):** Used to store graph connections.
    *   *Space Complexity:* $O(V + E)$
*   **Set/Hash Maps:** Used for tracking infected nodes to allow $O(1)$ lookups during transmission checks.

### 3. Simulation Complexity
*   **Initialization:** $O(V)$
*   **Transmission Step:** $O(I \times k)$
    *   Where $I$ is the number of currently infected nodes and $k$ is the average number of neighbors.
    *   *Optimization:* We iterate **only** through infected nodes rather than the entire population every frame.

---

## 🛠 Tech Stack

| Component | Technology | Usage |
| :--- | :--- | :--- |
| **Core Logic** | Python | Main simulation loop and state management. |
| **Visualization** | Pygame | Rendering the nodes, edges, and UI updates at 30+ FPS. |
| **Graph Logic** | NetworkX | Generating the Watts-Strogatz graph and spring layouts. |
| **Math/Stats** | NumPy | Handling probabilities for masks, vaccines, and age demographics. |
| **Analysis** | Matplotlib | Plotting the final result curves/bar charts. |

---

## 💻 Installation & Usage

### Prerequisites
Ensure you have Python installed. Install dependencies using the generated requirements file:

```bash
pip install -r requirements.txt
```

### Running the Simulation
After installing the dependencies, clone the repository and run the main script:

```bash
git clone <repository-url>
cd <repository-folder>
python main.py
```
