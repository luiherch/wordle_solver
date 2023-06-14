<h1 align="center">Wordle Solver using Information Theory</h1>
<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/luiherch/wordle_solver/blob/main/img/logo_light.png?raw=true">
  <source media="(prefers-color-scheme: light)" srcset="https://github.com/luiherch/wordle_solver/blob/main/img/logo_dark.png?raw=true">
  <img alt="Wordle Solver logo" src="https://github.com/luiherch/wordle_solver/blob/main/img/logo_dark.png?raw=true" width=128px>
</picture>
</p>  

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10.10-green" alt="Chat">
  <a href="https://creativecommons.org/licenses/by-nc/4.0/"><img src="https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg" alt="Chat"></a>
</p> 

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
   poetry run python main.py
   ```


## Usage

1. Launch the program running `main.py`

2. Enter the words you have tried using the virtual keyboard

3. Click on the screen buttons to select which pattern you obtained in the wordle game so far

4. Click on `compute entropies` to compute the best words based on the words and patterns entered

5. Click on `show entropies` to see the best words to guess based on the entropy score of every word

6. Press reset button to try new words and patterns

## To-Do List

- [ ] Integrate physical keyboard
- [ ] Add multiprocessing to speed up initial computation
- [ ] Improve light mode appearance
- [ ] Write comprehensive documentation
- [ ] Build web version
- [ ] Add file dialog to change the word dictionary to allow different languages
- [ ] Improve appearance of light mode


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
