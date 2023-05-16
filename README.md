# Wordle Solver using Information Theory
![Python](https://img.shields.io/badge/python-3.10.10-green)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
## Overview
This project is a Wordle solver that leverages principles from **information theory** to efficiently guess the hidden word in the Wordle game. Built using Python and scipy, this solver aims to enhance the player's Wordle experience by providing the statistically best words based on the player's guesses. The solver utilizes a non-comprehensive Spanish dictionary to generate word suggestions.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/wordle-solver.git
   ```

2. Navigate to the project directory:

   ```bash
   cd wordle-solver
   ```

3. Install Poetry (if not already installed):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. Install the project dependencies using Poetry:

   ```bash
   poetry install
   ```

5. Run the solver:

   ```bash
   poetry run python wordle_solver_gui.py
   ```


## Usage

1. Launch the solver using the installation instructions mentioned above.

2. Click on `show entropies` to see the best words to guess.

3. Enter any words you have tried and add the colors of the letters in the interface.

4. Click `compute entropies` to compute again the entropies with the newly inserted words and patterns.

## License

This project is licensed under the CC BY-NC 4.0 License. See the [LICENSE](LICENSE) file for more information.


## Contributing

Contributions are welcome! If you'd like to enhance the Wordle solver or fix any issues, please follow these steps:

1. Fork the repository.

2. Create a new branch for your feature/fix:

   ```bash
   git checkout -b feature/your-feature
   ```

3. The commits adhere to the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) convention. Make the necessary changes and commit them: 

   ```bash
   git commit -m 'feat: add your feature description'
   ```


4. Push your changes to the forked repository:

   ```bash
   git push origin feature/your-feature
   ```

5. Open a pull request to the main repository's `main` branch.
