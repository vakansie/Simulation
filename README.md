Simulation

cellular automaton

red can spread on green,
green can spread on yellow,
yellow can spread on red

every cell will try to spread every iteration

by default:
- cells spread once per iteration                           - spread factor            - hotkeys '+-'  - top slider
- cells spread in random order                              - toggle random iter order - hotkey 'z'
- cells spread in random direction                          - toggle random spread     - hotkey 'x'
- cells spread to 1 of their 8 neighboring cells            - toggle diagonal spread   - hotkey 'd'
- an unsuccesfull spread can't backfire                     - toggle reverse eating    - hotkey 'f'
- a succesfull spread wont recursicely try to spread again  - toggle recursive eating  - hotkey 'r' --> hotkey '<>' - bottom slider 
- a cell can only change once per iteration                 - toggle only change once  - hotkey 'c'
- the seed density is 100 random squares in random places   - set seed density         - menu option
- all cells are drawn                                       - toggle only draw changed  -hotkey 'v'

other hotkeys:

- play/pause - space
- back/pause - b
- step - left right arrow keys
- reset simulation - shift-r (keeps settings)
- reset default settings - shift-d
- save - ctrl-s
- load - ctrl-l
- nuke - mouse button 3
