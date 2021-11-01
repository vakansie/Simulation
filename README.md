# Simulation

# cellular automaton

red can spread on green,
green can spread on yellow,
yellow can spread on red

every cell will try to spread every iteration

by default:

| description                                              | option                   | hotkey                     | notes         |
| ---                                                      | ---                      | ---                        | ---           |
| cells spread once per iteration                          | spread factor            | `+` / `-`                  | top slider    |
| cells spread in random order                             | toggle random iter order | `z`                 |               |
| cells spread in random direction                         | toggle random spread     | `x`                 |               |
| cells spread to 1 of their 8 neighboring cells           | toggle diagonal spread   | `d`                 |               |
| an unsuccesfull spread can't backfire                    | toggle reverse eating    | `f`                 |               |
| a succesfull spread wont recursively try to spread again | toggle recursive eating  | `r` --> hotkey '<>' | bottom slider |
| a cell can only change once per iteration                | toggle only change once  | `c`                 |               |
| the seed density is 100 random squares in random places  | set seed density         | menu option                |               |
| all cells are drawn                                      | toggle only draw changed | `v`                 |               |

## Other Hotkeys:

- play/pause - `space`
- back/pause - `b`
- step - `left` `right`
- reset simulation - `shift-r` (keeps settings)
- reset default settings - `shift-d`
- save - `ctrl-s`
- load - `ctrl-l`
- nuke - mouse button 3


# Installation using pipenv

 1. `tkinter` is not installable through pip and therefore must be installed manually. See [documentation](https://tkdocs.com/tutorial/install.html). 
 2. Make sure `pipenv` is installed on your platform using `pip install pipenv`.
 3. Install all required packages using `pipenv install`

## About `pipenv`
`pipenv` is used for bundling dependencies. Dependencies are defined in `./Pipfile` and versions are pinned down using `./Pipfile.lock`.

### Adding new dependencies

eg. for adding numpy

```bash
pipenv install numpy
```

### Updating dependencies

```bash
pipenv update
git add Pipfile.lock
git commit -m "Updated Dependencies"
```
