# simpletyper
simpletyper is a fast and clean Text-based User Interface (TUI) app powered by [textual](https://github.com/Textualize/textual) for testing your typing speed.


## Demo:
https://user-images.githubusercontent.com/87934749/177049034-b80e99e8-d2bf-46b7-8d8a-77b642456487.mp4

## Features
- Clean UI
- Arbitrarily long passages randomly generated from up to 25000 english words
- Count down mode and relax mode

## Limitations
- The "screen" of the app cannot scroll, so it is reccomended to choose the number of words that will fit in one screen

## Installation
### Using `poetry`
1. `git clone` this repo, `cd` into it and run `poetry install`
2. Activate the poetry enviroment either by running `poetry shell` or `sourcing` the `virtualenv` directly
3. Run the app with `simpletyper`
---
### Using `pip`
1. Run `pip install simpletyper` or `pip install git+https://github.com/WilsonOh/simpletyper.git`
2. Run the app with `simpletyper`

## Usage
### Overview
The app has 3 parameters: `count_down`, `file_name` and `num_words`.
`count_down` refers to the timer in "count down mode",
`num_words` refers to the number of words to be used in the speed test,
and `file_name` refers to the file from which the app will source the words. (i.e. from `simpletyper/words/{filename}`)<br>

### Keybindings
- `Escape` / `Ctrl+C` to quit out of the app
- `Ctrl+R` to reset the app

### Flags
The app can be run with 3 flags to set the parameters explained above:
- `-n` or `--num_words` to set `num_words`
- `-t` or `--timer` to set the `count_down` timer
- `-f` or `--file` to set the file to source words from
- `-h` or `--help` to display a help message 
---
> **Note**
Running the game without any arguments will run the game using the default parameters of `num_words` = 20, `count_down` = 0 and `file` = top2500.
#### Omitting the `timer` flag will simply run the app in "relax mode", where you can take all the time you need to complete the passage.
An example command would be
```console
simpletyper -n 30 -t 10
```
This will set the number of words to 30, and there will be a count down of 10s

## Credits
[toipe](https://github.com/Samyak2/toipe) for the folder of word lists and inspiration for the UI

## Todo
- [ ] Make the app more configurable for the colors and styling used
- [ ] Use actual english passages instead of random words
