# Project plan

## General outline
### 1. **Software Architecture**

The project can be divided into several key components:

#### a. **Game Engine**

- **Core Simulation**: Handles the rules, mechanics, and interactions between units.
- **State Management**: Keeps track of game state (positions, health, game phase, etc.).
- **Physics and Mechanics**: Simulates movement, combat resolution, and terrain interactions.

#### b. **Game Display**

- **Minimalistic UI**: Simple graphical representation (e.g., grid with units as icons).
- **Rendering**: Basic 2D visualization library (e.g., `pygame` or `matplotlib`).
- **User Interface**: Controls to allow interaction with the simulation.

#### c. **AI/Agent System**

- **AI Agents**: Different versions of AI for different factions.
- **Reinforcement Learning**: Learning framework for self-improvement.
- **Evaluation Framework**: Tracks performance metrics and guides rule adjustments.

#### d. **Training Environment**

- **Self-Play**: Instances of the AI pitted against each other.
- **Game Balance Metrics**: Metrics to evaluate balance (win rates, kill/death ratios).

#### e. **Rule Modification System**

- **Rule Definition**: Flexible data structure for rules.
- **Automated Testing**: Framework to evaluate new rule sets.

### 2. **Tools and Resources**

#### a. **Game Engine and Simulation**

- **Language**: Python (with libraries like `numpy` for calculations).
- **IDE**: Visual Studio Code, PyCharm, or Jupyter for prototyping.
- **Simulation Library**: `PyGame` for simple graphical output, or `matplotlib` for static visualizations.
- **Physics**: If needed, simple physics calculations can be done using `sympy` or similar libraries.

#### b. **AI/Agent System**

- **Language**: Python (due to excellent machine learning libraries).
- **Frameworks**:
    - `PyTorch` or `TensorFlow` for neural networks.
    - `Stable Baselines3` for reinforcement learning.
- **Data Handling**: `Pandas` and `NumPy` for data manipulation.
- **Computing Requirements**:
    - Training can be computationally intensive. Use a GPU if possible (e.g., through cloud services like Google Colab, AWS, or local resources).
    - For initial development, a standard CPU will suffice.

#### c. **Training Environment**

- **Simulation Scaling**: Run multiple instances in parallel (consider using multiprocessing or cloud computing).
- **Hyperparameter Tuning**: Tools like `Optuna` or `Ray Tune` can help.
- **Visualization**: `TensorBoard` for tracking training metrics.

#### d. **Rule Modification**

- **Rule Storage**: Use JSON or a similar format to store rule sets.
- **Automation**: Python scripts for rule manipulation and testing.
